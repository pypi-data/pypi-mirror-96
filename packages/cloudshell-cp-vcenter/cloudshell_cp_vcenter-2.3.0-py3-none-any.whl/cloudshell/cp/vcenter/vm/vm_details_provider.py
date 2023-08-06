import ipaddress
import re

from cloudshell.cp.core.models import (
    VmDetailsData,
    VmDetailsNetworkInterface,
    VmDetailsProperty,
)
from pyVmomi import vim

from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.network.vnic.vnic_service import VNicService
from cloudshell.cp.vcenter.vm.ip_manager import VMIPManager


class VmDetailsProvider(object):
    def __init__(self, pyvmomi_service, ip_manager):
        self.pyvmomi_service = pyvmomi_service  # type: pyVmomiService
        self.ip_manager = ip_manager  # type: VMIPManager

    def create(
        self,
        vm,
        name,
        reserved_networks,
        ip_regex,
        deployment_details_provider,
        wait_for_ip,
        logger,
    ):
        """
        creates the details provider
        :param vm:
        :param name:
        :param reserved_networks:
        :param ip_regex:
        :param deployment_details_provider:
        :param wait_for_ip: type: string contains 'True' or 'False'
        :param logger:
        :return:
        """

        logger.info("waiting for ip = {0}".format(wait_for_ip))

        vm_instance_data = self._get_vm_instance_data(vm, deployment_details_provider)
        vm_network_data = self._get_vm_network_data(
            vm, reserved_networks, ip_regex, wait_for_ip, logger
        )

        return VmDetailsData(
            vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data
        )

    def _get_vm_instance_data(self, vm, deployment_details_provider):
        data = []

        data.extend(deployment_details_provider.get_details())

        memo_size_kb = vm.summary.config.memorySizeMB * 1024
        disk_size_kb = next(
            (
                device.capacityInKB
                for device in vm.config.hardware.device
                if isinstance(device, vim.vm.device.VirtualDisk)
            ),
            0,
        )
        snapshot = None
        if vm.snapshot:
            snapshot = self._get_snapshot_path(
                vm.snapshot.rootSnapshotList, vm.snapshot.currentSnapshot
            )

        data.append(VmDetailsProperty(key="Current Snapshot", value=snapshot))
        data.append(
            VmDetailsProperty(key="CPU", value="%s vCPU" % vm.summary.config.numCpu)
        )
        data.append(
            VmDetailsProperty(key="Memory", value=self._convert_kb_to_str(memo_size_kb))
        )
        data.append(
            VmDetailsProperty(
                key="Disk Size", value=self._convert_kb_to_str(disk_size_kb)
            )
        )
        data.append(
            VmDetailsProperty(key="Guest OS", value=vm.summary.config.guestFullName)
        )
        data.append(
            VmDetailsProperty(key="Managed Object Reference ID", value=vm._GetMoId())
        )

        return data

    def _get_vm_network_data(
        self, vm, reserved_networks, ip_regex, wait_for_ip, logger
    ):
        network_interfaces = []

        if wait_for_ip == "True":
            primary_ip = self._get_primary_ip(vm, ip_regex, logger)
        else:
            primary_ip = None

        net_devices = [
            d
            for d in vm.config.hardware.device
            if isinstance(d, vim.vm.device.VirtualEthernetCard)
        ]

        for device in net_devices:
            network = VNicService.get_network_by_device(
                vm, device, self.pyvmomi_service, logger
            )
            vlan_id = self._convert_vlan_id_to_str(
                VNicService.get_network_vlan_id(network)
            )
            private_ip = self._get_ip_by_device(vm, device)

            if vlan_id and (
                network.name.startswith("QS_") or network.name in reserved_networks
            ):
                is_primary = private_ip and primary_ip == private_ip
                is_predefined = network.name in reserved_networks

                network_data = [
                    VmDetailsProperty(key="IP", value=private_ip),
                    VmDetailsProperty(key="MAC Address", value=device.macAddress),
                    VmDetailsProperty(
                        key="Network Adapter", value=device.deviceInfo.label
                    ),
                    VmDetailsProperty(key="Port Group Name", value=network.name),
                ]

                current_interface = VmDetailsNetworkInterface(
                    interfaceId=device.macAddress,
                    networkId=vlan_id,
                    isPrimary=is_primary,
                    isPredefined=is_predefined,
                    networkData=network_data,
                    privateIpAddress=private_ip,
                )
                network_interfaces.append(current_interface)

        return network_interfaces

    def _get_primary_ip(self, vm, ip_regex, logger):
        match_function = self.ip_manager.get_ip_match_function(ip_regex)
        primary_ip = self.ip_manager.get_ip(
            vm, None, match_function, None, None, logger
        ).ip_address
        return primary_ip

    @staticmethod
    def _is_ipv4_address(ip):
        try:
            ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError:
            return False

        return True

    @staticmethod
    def _get_ip_by_device(vm, device):
        for net in vm.guest.net:
            if str(net.deviceConfigId) == str(device.key):
                for ip_address in net.ipAddress:
                    if VmDetailsProvider._is_ipv4_address(ip_address):
                        return ip_address

    @staticmethod
    def _get_snapshot_path(nodes, snapshot):
        for node in nodes:
            if node.snapshot == snapshot:
                return node.name
            sn = VmDetailsProvider._get_snapshot_path(node.childSnapshotList, snapshot)
            if sn:
                return node.name + "/" + sn
        return None

    @staticmethod
    def _convert_kb_to_str(kb):
        mb = kb / 1024
        gb = mb / 1024
        if gb > 0:
            return "%0.0f GB" % gb
        elif mb > 0:
            return "%0.0f MB" % mb
        else:
            return "%0.0f KB" % kb

    @staticmethod
    def _convert_vlan_id_to_str(vlan_id):
        if vlan_id:
            if isinstance(vlan_id, list):
                return ",".join(
                    [VmDetailsProvider._convert_vlan_id_to_str(v) for v in vlan_id if v]
                )

            if isinstance(vlan_id, vim.NumericRange):
                if vlan_id.start == vlan_id.end:
                    return "%s" % vlan_id.start
                else:
                    return "%s-%s" % (vlan_id.start, vlan_id.end)

            if isinstance(vlan_id, str):
                return vlan_id

            if isinstance(vlan_id, int):
                return str(vlan_id)

        return ""
