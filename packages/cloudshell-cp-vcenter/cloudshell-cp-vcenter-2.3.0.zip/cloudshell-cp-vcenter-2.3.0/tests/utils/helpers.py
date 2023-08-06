from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim

from .testing_credentials import TestCredentials

from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService


def get_uuid(virtual_machine_name):
    credentials = TestCredentials()
    py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
    si = py_vmomi_service.connect(
        credentials.host, credentials.username, credentials.password, credentials.port
    )
    vm_uuid = get_vm_uuid(py_vmomi_service, si, virtual_machine_name)
    return vm_uuid


def get_vm_uuid(py_vmomi_service, si, virtual_machine_name):
    vm = py_vmomi_service.get_obj(
        si.content, [[vim.VirtualMachine]], virtual_machine_name
    )
    vm_uuid = vm.config.uuid
    return vm_uuid
