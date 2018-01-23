"""
Builds on voting.py to use an online voting algorithm.
By that I mean that it is iteratively figuring out the winner after each submission.
All Judge does is lock down the selection.
0.6 - change to Notify for the New Game success
"""

from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer,GetExecutingScriptHash
from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Header import GetTimestamp, GetNextConsensus, GetHash
from boa.blockchain.vm.Neo.Transaction import GetReferences, GetUnspentCoins
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.code.builtins import concat,take, substr, range, list
from boa.blockchain.vm.Neo.Output import GetScriptHash

def Main(operation, args):
    """
    :param operation: new, submit, judge, getvalue
    :param args: optional arguments
    :return: Bool
    """

    trigger = GetTrigger()
    if trigger == Application:
        Log("trigger: Application")
        context = GetContext()

        if operation == 'getvalue':
            Log("op: getvalue")
            key = args[0]
            return Get(context, key)

        if operation == 'new':
            Log("op: new")
            id = args[0]
            Put(context,"current_game", id)
            Put(context, "max", 0)
            Log("Created a new game")
            Notify(id)

        elif operation == 'submit':
            id = args[0]
            price = args[1]
            sender = args[2]
            Log(id)
            Log(price)
            Log(sender)

            # Only allow submissions for the current game
            current_game = Get(context, "current_game")
            if current_game != id:
                Log("Not the correct game")
                return False

            if not CheckWitness(sender):
                Log("Oracle is not the right person")
                return False

            Log(sender)
            key = concat(sender,id)
            Log(key)
            oldprice = Get(context, key)
            if oldprice != 0:
                # Too late you've already submitted
                Log("Error: cannot submit twice for the same game")
                return False
            Append(context, sender, id)
            Put(context,key,price) # Update if already exists
            max = Get(context, 'max')
            price_key = concat(id, price)
            count = Increment(context, price_key)
            if count > max:
                Put(context, 'max', count)
                Put(context, id, price)
                Log("Updated best price")
            return True

        elif operation == 'judge':
            id = args[0]
            playerkey = concat("players::", id)
            curr_list = Get(context, playerkey)
            nplayers = len(curr_list) // 20
            decided_price = Get(context, id)
            for i in range(0, nplayers):
                start = 20 * i
                player = substr(curr_list,start, 20)
                Log(player)
                Log("Checking if player lied")
                key = concat(player, id)
                price = Get(context, key)
                if decided_price != price:
                    Log("Player did LIE!")
                else:
                    Log("Player told the TRUTH!")
            return True
        return True
    return False


def Increment(context, price_key):
    count = Get(context, price_key)
    if count == 0:
        count = 1
    else:
        count = count + 1
    Put(context, price_key, count)
    return count

def Append(context, sender, id):
    playerkey = concat("players::",id)
    curr_list = Get(context,playerkey)
    if curr_list == 0:
        curr_list = sender
    else:
        curr_list = concat(curr_list,sender)
    Log(curr_list)
    Put(context,playerkey,curr_list)