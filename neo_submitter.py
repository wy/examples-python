'''
NEO Listening and Submitter
This python node will listen on the blockchain for changes to the smart contract (i.e. a new game)
It will then submit a random number between 1 and 3
Note: you do need a tiny amount of gas each time 0.001
Hence, you need to use the coz faucet somehow
'''

import threading
from time import sleep

from logzero import logger
from twisted.internet import reactor, task

from neo.contrib.smartcontract import  SmartContract
from neo.Network.NodeLeader import NodeLeader
from neo.Core.Blockchain import Blockchain
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Settings import settings
from Invoke_Debug import InvokeContract, TestInvokeContract, test_invoke
from neo.Implementations.Wallets.peewee.UserWallet import UserWallet
from neocore.KeyPair import KeyPair

from random import Random

# If you want the log messages to also be saved in a logfile, enable the
# next line. This configures a logfile with max 10 MB and 3 rotations:
# settings.set_logfile("/tmp/logfile.log", max_bytes=1e7, backup_count=3)

# Setup the smart contract instance
# This is online voting v0.5
smart_contract = SmartContract("ef254dc68e36de6a3a5d2de59ae1cdff3887938f ")
wallet_hash = 'AKgM1UKH1yaqWXZ24ro3woaxbkXnwGJPnP'
#wif = 'L5Cp8JMBuLQXvsY5Gijj7oPXkit9skMpsJu7ECyyrnvBmJcgGa7v'
Wallet = None


def test_invoke_contract(args):
    if not Wallet:
        print("where's the wallet")
        return
    if args and len(args) > 0:
        print(args)
        print(args[1:])
        tx, fee, results, num_ops= TestInvokeContract(Wallet, args)

        print("Results %s " % [str(item) for item in results])

        if tx is not None and results is not None:
            print("Invoking for real")
            result = InvokeContract(Wallet, tx, fee)
            return
    return


# Register an event handler for Runtime.Notify events of the smart contract.
@smart_contract.on_notify
def sc_log(event):
    logger.info(Wallet.AddressVersion)
    logger.info("SmartContract Runtime.Notify event: %s", event)

    # Make sure that the event payload list has at least one element.
    if not len(event.event_payload):
        return

    # The event payload list has at least one element. As developer of the smart contract
    # you should know what data-type is in the bytes, and how to decode it. In this example,
    # it's just a string, so we decode it with utf-8:
    logger.info("- payload part 1: %s", event.event_payload[0])
    game = event.event_payload[0]
    #args = ['ef254dc68e36de6a3a5d2de59ae1cdff3887938f','submit',[game,2,wallet_hash]]
    x = Random.randint(1, 9)

    args = ['ef254dc68e36de6a3a5d2de59ae1cdff3887938f', 'new', [x]]
    test_invoke_contract(args)



def custom_background_code():
    """ Custom code run in a background thread. Prints the current block height.
    This function is run in a daemonized thread, which means it can be instantly killed at any
    moment, whenever the main thread quits. If you need more safety, don't use a  daemonized
    thread and handle exiting this thread in another way (eg. with signals and events).
    """
    while True:
        logger.info("Block %s / %s", str(Blockchain.Default().Height), str(Blockchain.Default().HeaderHeight))
        sleep(15)




def main():

    settings.setup('protocol.coz.json')
    # Setup the blockchain
    blockchain = LevelDBBlockchain(settings.LEVELDB_PATH)
    Blockchain.RegisterBlockchain(blockchain)
    dbloop = task.LoopingCall(Blockchain.Default().PersistBlocks)
    dbloop.start(.1)
    NodeLeader.Instance().Start()

    # Disable smart contract events for external smart contracts
    settings.set_log_smart_contract_events(False)

    global Wallet
    Wallet = UserWallet.Open(path="testwallet", password="0123456789")
    logger.info("Created the Wallet")
    logger.info(Wallet.AddressVersion)
    #Wallet.CreateKey(KeyPair.PrivateKeyFromWIF(wif))

    # Start a thread with custom code
    d = threading.Thread(target=custom_background_code)
    d.setDaemon(True)  # daemonizing the thread will kill it when the main thread is quit
    d.start()

    # Run all the things (blocking call)
    logger.info("Everything setup and running. Waiting for events...")
    reactor.run()
    logger.info("Shutting down.")


if __name__ == "__main__":
    main()