from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete

def Main(operation, key, value):
    """
    :param operation: get or put
    :param key: key
    :param value: value
    :return: Bool
    """

    Log("hello world")
    context = GetContext()
    if operation == "get":
        v = Get(context, key)
        Log(v)
        return True
    elif operation == "put":
        Put(context, key, value)
        Log("Placed k,v")
        return True

    return False # Something went wrong