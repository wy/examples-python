"""
Full Featured Oracle Judge
>> register {prediction_name} --attach-gas=5
# Registers Oracle (address of sender) for sending in predictions for {prediction_name}
e.g. NEO_USD_CMC

>> cash_out {prediction_name} {sender_hash}
# Get GAS and any payouts due

>> submit_prediction {prediction_name} {normalised_timestamp} {price} {sender}
# Submits prediction. Normalised Timestamp is the timestamp that OJ will understand

>> {owner} create_new_prediction_game {prediction_name}

>> {owner} remove_prediction {prediction_name}

>> {owner} force_judge {prediction_name}

>> {owner} force_set_new_timestamp {prediction_name} {timestamp}

>> {client} get_latest_prediction {prediction_name}

>> {client} get_prediction {prediction_name} {normalised_timestamp}

Timescales
T_n = Normalised Timestamp
T_n+ = Timestamp of CMC price change (T_n+ > T_n)
T_j = 8 minutes after T_n

OJ maintains a state which is the current T_n (initially it's right now)
If anyone submits a message and OJ checks the current timestamp and it's >= T_j
Then its time to make a judgement
After the judgement is done, it then updates T_n and T_j.
It also maintains {prediction_name}::{T_n} => {price} for any T_n in its record
As well as {prediction_name} => {price} for latest price

KEYS:
prediction_live{prediction_name} => 1 or 0
balance{sender_hash}{prediction_name} => GAS Balance
timestamp{prediction_name} => timestamp_normalised
latest_prediction{prediction_name} => latest_prediction
specific_prediction{prediction_name}{timestamp_normalised} => prediction
submission{sender_hash}{prediction_name}{timestamp_normalised} => prediction
max_votes{prediction_name}{timestamp_normalised} => count
prediction_count{prediction_name}{timestamp_normalised}{prediction} => count
oracles{prediction_name}{timestamp_normalised} => {oracle1}{oracle2}{...}
winning_oracles{prediction_name}{timestamp_normalised} => {oracle1}{oracle2}{...}


"""

from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer,GetExecutingScriptHash
from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
#from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.Transaction import *
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.blockchain.vm.Neo.Output import GetScriptHash,GetValue,GetAssetId
from boa.code.builtins import concat,take, substr, range, list
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Header import GetTimestampte

owner = 'ASvsbeHUiYfLj8NFEwgW88QPegnitBU2Mv'
GAS_ASSET_ID = b'\xe7\x2d\x28\x69\x79\xee\x6c\xb1\xb7\xe6\x5d\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8e\x77\x58\xde\x42\xe4\x16\x8b\x71\x79\x2c\x60';

def Main(operation, args):
    """
    :param operation
    :param args: optional arguments (up to 3 max)
    :return: Bool (success or failure) or Prediction
    """

    Log("ORACLE JUDGE")
    trigger = GetTrigger()
    arg_len = len(args)
    if arg_len > 4:
        # Only 4 args max
        return False

    if trigger == Verification:
        Log("trigger: Verification")
        is_owner = CheckWitness(owner)
        if is_owner:
            return True
    elif trigger == Application:
        Log("trigger: Application")
        context = GetContext()

        if operation == 'register':
            Log("op: register")
            if arg_len != 1:
                Log("Wrong arg length")
                return False
            prediction_name = args[0]
            return Register(prediction_name, context)

        elif operation == 'cash_out':
            Log("op: Cash Out")
            if arg_len != 2:
                Log("Wrong arg length")
                return False
            prediction_name = args[0]
            sender_hash = args[1]
            if not CheckWitness(sender_hash):
                Log("Sender Hash not Verified")
                return False
            return CashOut(prediction_name, sender_hash, context)

        elif operation == 'submit_prediction':
            Log("op: Submit Prediction")
            if arg_len != 4:
                Log("Wrong arg length")
                return False
            prediction_name = args[0]
            normalised_timestamp = args[1]
            price = args[2]
            sender_hash = args[3]
            if not CheckWitness(sender_hash):
                Log("Sender Hash not Verified")
                return False
            return SubmitPrediction(prediction_name, normalised_timestamp, price, sender_hash, context)
        elif operation == 'create_new_prediction_game':
            Log("op: Create New Prediction Game")
            if not CheckWitness(owner):
                Log("Not owner")
                return False
            prediction_name = args[0]
            return CreateNewPredictionGame(prediction_name, context)
        elif operation == 'remove_prediction':
            Log("op: Remove Prediction")
            if not CheckWitness(owner):
                Log("Not owner")
                return False
            prediction_name = args[0]
            return RemovePrediction(prediction_name, context)
        elif operation == 'force_judge':
            Log("op: Force Judge")
            if not CheckWitness(owner):
                Log("Not owner")
                return False
            prediction_name = args[0]
            return ForceJudge(prediction_name, context)
        elif operation == 'force_set_new_timestamp':
            Log("op: Force Set New Timestamp")
            if not CheckWitness(owner):
                Log("Not owner")
                return False
            prediction_name = args[0]
            normalised_timestamp = args[1]
            return ForceSetNewTimestamp(prediction_name, normalised_timestamp, context)
        elif operation == 'get_latest_prediction':
            Log("op: Get Latest Prediction")
            prediction_name = args[0]
            return GetLatestPrediction(prediction_name, context)
        elif operation == 'get_prediction':
            Log("op: Get Prediction")
            prediction_name = args[0]
            normalised_timestamp = args[1]
            return GetPrediction(prediction_name, normalised_timestamp, context)
        else:
            Log(operation)
            Log("op: Unknown operation")
            return False
    return False


def CheckPredictionGameLive(prediction_name, context):
    key = concat("prediction_live", prediction_name)
    live = Get(context, key)
    return live == 1

def GetBalance(prediction_name, sender_hash, context):
    k0 = concat("balance", sender_hash)
    key = concat(k0, prediction_name)
    balance = Get(context, key)
    return balance

def CheckBalance(prediction_name, sender_hash, context):
    k0 = concat("balance", sender_hash)
    key = concat(k0, prediction_name)
    balance = Get(context, key)
    return balance > 0

def ZeroBalance(prediction_name, sender_hash, context):
    k0 = concat("balance", sender_hash)
    key = concat(k0, prediction_name)
    Put(context, key, 0)


def Register(prediction_name, context):
    if CheckPredictionGameLive(prediction_name, context):
        tx = GetScriptContainer()
        refs = tx.References
        if len(refs) < 1:
            Log("No payment sent in transaction")
            return False
        ref = refs[0]
        sentAsset = GetAssetId(ref)
        sender_hash = GetScriptHash(ref)

        k1 = concat("balance", sender_hash)
        key = concat(k1, prediction_name)

        balance = Get(context, key)
        if balance >= 5:
            Log("Already registered")
            return False
        else:
            if sentAsset == GAS_ASSET_ID:
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
                    Log("Correct GAS Received")
                    Put(context, key, 5)
                    return True
                else:
                    Log("Wrong amount of GAS")
                    return False
            else:
                Log("Not GAS")
                return False
    else:
        Log("Prediction Game not live")
    return False


def CashOut(prediction_name, sender_hash, context):
    k1 = concat("balance",sender_hash)
    key = concat(k1, prediction_name)
    balance = Get(context, key)
    ###Transfer balance to sender_hash
    return False

def GetMaxVotes(prediction_name, normalised_timestamp, context):
    k0 = concat("max_votes", prediction_name)
    key = concat(k0, normalised_timestamp)
    return Get(context, key)

def UpdateMaxVotes(prediction_name, normalised_timestamp, count, context):
    k0 = concat("max_votes", prediction_name)
    key = concat(k0, normalised_timestamp)
    Put(context, key, count)


def UpdatePrice(prediction_name, normalised_timestamp, price, context):
    key = concat("latest_prediction", prediction_name)
    Put(context, key, price)
    k0 = concat("specific_prediction", prediction_name)
    key = concat(k0, normalised_timestamp)
    Put(context, key, price)

def IncrementCount(prediction_name, normalised_timestamp, price, context):
    k0 = concat("prediction_count", prediction_name)
    k1 = concat(k0, normalised_timestamp)
    k2 = concat(k1, price)
    count = Get(context,k2)
    if count == 0:
        Put(context, k2, 1)
        return 1
    else:
        count = count + 1
        Put(context, k2 , count)
        return count

def GetCurrentTimestamp(prediction_name, context):
    key = concat("timestamp", prediction_name)
    TS = Get(context, key)
    return TS

def UpdateTimestamp(prediction_name, timestamp, context):
    key = concat("timestamp", prediction_name)
    Put(context, key, timestamp)

def GetOracles(prediction_name, normalised_timestamp, context):
    k0 = concat("oracles", prediction_name)
    key = concat(k0, normalised_timestamp)
    oracles = Get(context, key)
    return oracles

def AddOracle(prediction_name, normalised_timestamp, oracle, context):
    k0 = concat("oracles", prediction_name)
    key = concat(k0, normalised_timestamp)
    oracles = Get(context, key)
    new_oracles = concat(oracles, oracle)
    Put(context, key, new_oracles)

def GetSubmission(prediction_name, normalised_timestamp, sender_hash, context):
    k0 = concat("submission", sender_hash)
    k1 = concat(k0, prediction_name)
    key = concat(k1, normalised_timestamp)
    prediction = Get(context, key)
    return prediction

def SubmitPrediction(prediction_name, normalised_timestamp, price, sender_hash, context):
    if CheckPredictionGameLive(prediction_name, context):
        if CheckBalance(prediction_name, sender_hash, context):
            ### Do Prediction Submission
            # Check no duplicate submissions
            k0 = concat("submission", sender_hash)
            k1 = concat(k0,prediction_name)
            key = concat(k1,normalised_timestamp)
            prediction = Get(context, key)
            if prediction != 0:
                # Already submitted
                Log("Already submitted a price")
                return False
            else:
                AddOracle(prediction_name, normalised_timestamp, sender_hash, context)
                Put(context, key, price)
                max = GetMaxVotes(prediction_name, normalised_timestamp, context)
                count = IncrementCount(prediction_name, normalised_timestamp, price, context)
                if count > max:
                    UpdateMaxVotes(prediction_name, normalised_timestamp, count, context)
                    UpdatePrice(prediction_name, normalised_timestamp, price, context)
                return True

        else:
            Log("No balance")
    else:
        Log("Prediction Game not live")
    return False


def CreateNewPredictionGame(prediction_name, context):
    # Check if Prediction Live
    if CheckPredictionGameLive(prediction_name, context):
        Log("Prediction Game is live")
    else:
        key = concat("prediction_live", prediction_name)
        Put(context, key, 1)
        return True
    return False


def RemovePrediction(prediction_name, context):
    # Check if Prediction Live
    if CheckPredictionGameLive(prediction_name, context):
        key = concat("prediction_live", prediction_name)
        Put(context, key, 0)
        return True
    else:
        Log("Prediction Game not live")
    return False

def AddWinner(prediction_name, normalised_timestamp, oracle, context):
    k0 = concat("winning_oracles", prediction_name)
    key = concat(k0, normalised_timestamp)
    winners = Get(context, key)
    if winners == "":
        winners = oracle
    else:
        winners = concat(winners, oracle)
    Put(context, key, winners)

def GetWinners(prediction_name, normalised_timestamp, context):
    k0 = concat("winning_oracles", prediction_name)
    key = concat(k0, normalised_timestamp)
    winners = Get(context, key)
    return winners

def AddBalance(prediction_name, sender_hash, winnings, context):
    k0 = concat("balance", sender_hash)
    key = concat(k0, prediction_name)
    balance = Get(context, key)
    balance = balance + winnings
    Put(context, key, balance)

def CheckTimestamp(timestamp_normalised):
    # Checks if TS() > T_n + 8 minutes
    height = GetHeight()
    hdr = GetHeader(height)
    ts = GetTimestamp(hdr)
    if ts > timestamp_normalised + 480:
        return True
    return False

def NextTimestamp(timestamp_normalised):
    return timestamp_normalised + 300

def ForceJudge(prediction_name, context):
    # Find Losers and Collect GAS
    # Find Winners
    # Distribute GAS to Winners
    # Move onto next timestamp

    winning_prediction = GetLatestPrediction(prediction_name, context)
    current_timestamp = GetCurrentTimestamp(prediction_name, context)
    oracles = GetOracles(prediction_name, current_timestamp, context)

    nOracles = len(oracles) // 20
    LoserBalance = 0
    nWinners = 0
    for i in range(0, nOracles):
        start = 20 * i
        oracle = substr(oracles, start, 20)
        Log(oracle)
        Log("Checking if oracle lied")
        submitted_price = GetSubmission(prediction_name, current_timestamp, oracle, context)
        if winning_prediction != submitted_price:
            Log("Player did LIE!")
            LoserBalance = LoserBalance + GetBalance(prediction_name, oracle, context)
            ZeroBalance(prediction_name, oracle, context)
        else:
            Log("Player told the TRUTH!")
            AddWinner(prediction_name, current_timestamp, oracle, context)
            nWinners = nWinners + 1
    # Now distribute winnings to Winners
    if nWinners > 0:
        winnings = LoserBalance // nWinners
        winners = GetWinners(prediction_name, current_timestamp, context)
        for i in range(0, nWinners):
            start = 20 * i
            winner = substr(winners, start, 20)
            AddBalance(prediction_name, winner, winnings, context)

    # Move onto next timestamp
    next_ts = NextTimestamp(current_timestamp)
    UpdateTimestamp(prediction_name, next_ts, context)
    return True


def ForceSetNewTimestamp(prediction_name, normalised_timestamp, context):
    if CheckPredictionGameLive(prediction_name, context):
        key = concat("timestamp", prediction_name)
        Put(context, key, normalised_timestamp)
        return True
    else:
        Log("Prediction Game not live")
    return False


def GetLatestPrediction(prediction_name, context):
    if CheckPredictionGameLive(prediction_name, context):
        key = concat("latest_prediction", prediction_name)
        prediction = Get(context, key)
        return prediction
    else:
        Log("Prediction Game not live")
    return False


def GetPrediction(prediction_name, normalised_timestamp, context):
    if CheckPredictionGameLive(prediction_name, context):
        k0 = concat("spcific_prediction", prediction_name)
        key = concat(k0, normalised_timestamp)
        prediction = Get(context, key)
        return prediction
    else:
        Log("Prediction Game not live")
    return False