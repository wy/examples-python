"""
This version of Oracle Judge simply allows a few commands:
- Register Oracle: Send 5 GAS in along with a string that represents what you want to be an Oracle for
e.g. register-oracle today_date_YYYYMMDD --attach-gas=5
- Withdraw Oracle: receive back your 5 GAS if you are registered along with the string of what you were an oracle for
e.g. withdraw-oracle today_date_YYYYMMDD

"""

from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer,GetExecutingScriptHash
from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
#from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.Transaction import *
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.blockchain.vm.Neo.Output import GetScriptHash,GetValue,GetAssetId
from boa.code.builtins import concat,take


owner = b'02a9261dc15afdc57c292c097858b11e2385572b394859b39953629daf2e5a9fc3'
GAS_ASSET_ID = b'\xe7\x2d\x28\x69\x79\xee\x6c\xb1\xb7\xe6\x5d\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8e\x77\x58\xde\x42\xe4\x16\x8b\x71\x79\x2c\x60';


def Main(operation, args):
    """
    :param operation: get or put
    :param args: optional arguments
    :return: Bool
    """

    Log("Running Main Loop")
    trigger = GetTrigger()
    if trigger == Verification:
        Log("trigger: Verification")
        is_owner = CheckWitness(owner)
        if is_owner:
            return True
    elif trigger == Application:
        Log("trigger: Application")
        context = GetContext()
        if operation == 'getvalue':
            Log("op: getvalue")
            key = args[0]
            return Get(context, key)
        if operation == 'register-oracle':
            Log("op: register-oracle")
            nArgs = len(args)
            Log(nArgs)
            if len(args) != 1:
                return False
            tx = GetScriptContainer()
            refs = tx.References
            if len(refs) < 1:
                Log("No payment sent in transaction")
                return False
            ref = refs[0]
            sentAsset = GetAssetId(ref)
            sender = GetScriptHash(ref)
            oracle_app = args[0]
            k = concat(sender,oracle_app)
            amount = Get(context, k)
            if amount == 5:
                Log("Already registered")
                return False
            if sentAsset == GAS_ASSET_ID:
                Log("Ok it is GAS")
                receiver = GetExecutingScriptHash()
                totalGasSent = 0
                cOutputs = len(tx.Outputs)
                Log(cOutputs)
                for output in tx.Outputs:
                    Log(output.Value)
                    shash = GetScriptHash(output)
                    if shash == receiver:
                        totalGasSent = totalGasSent + output.Value

                Log("Total GAS sent:")
                Log(totalGasSent)
                if totalGasSent == b'\x00e\xcd\x1d':
                    Log("That's what we wanted")
                    Notify("We received the GAS")

                    Put(context, k, 5)
                    return True
                else:
                    Log("We didn't want this.")
                    return False
            else:
                Log("Not Gas")
                return False
    return False