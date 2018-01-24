"""
Simply Logs out and runs Notify for the Header Timestamp
"""


from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Header import GetTimestamp, GetNextConsensus, GetHash
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.code.builtins import concat,take


def Main(operation):
    """
    :param operation: get or put
    :param args: optional arguments
    :return: Bool
    """

    trigger = GetTrigger()
    if trigger == Application:
        Log("trigger: Application")
        height = GetHeight()
        hdr = GetHeader(height)
        ts = GetTimestamp(hdr)
        Log(ts)
        return True
    return False

