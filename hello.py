from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete

def Main(operation, args):
    """
    This is the main entry point for the dApp
    :param operation: the operation to be performed
    :type operation: str
    :param args: an optional list of arguments
    :type args: list
    :return: indicating the successful execution of the dApp
    :rtype: bool
    """

    context = GetContext()
    if operation == 'hi':
        Put(context, 'Hello', "World")
    else:
        n = Get(context, "Hello")
        Log(n)
        return n
