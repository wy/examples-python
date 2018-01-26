"""
Simply watches out for notify events from the smart contract
and pretty print out the latest price

"""

'''
NEO Listening and Submitter
This python node will listen on the blockchain for changes to the smart contract (i.e. a new game)
It will then submit a random number between 1 and 3
Note: you do need a tiny amount of gas each time 0.001
Hence, you need to use the coz faucet somehow
'''

import threading
from time import sleep
import sys
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
import coinmarketcap
from neocore.BigInteger import BigInteger
from neo.Core.Helper import Helper

import random

# If you want the log messages to also be saved in a logfile, enable the
# next line. This configures a logfile with max 10 MB and 3 rotations:
# settings.set_logfile("/tmp/logfile.log", max_bytes=1e7, backup_count=3)

# Setup the smart contract instance
# This is online voting v0.5

#smart_contract_hash = "ef254dc68e36de6a3a5d2de59ae1cdff3887938f"
global smart_contract

def custom_background_code():
    """ Custom code run in a background thread. Prints the current block height.
    This function is run in a daemonized thread, which means it can be instantly killed at any
    moment, whenever the main thread quits. If you need more safety, don't use a  daemonized
    thread and handle exiting this thread in another way (eg. with signals and events).
    """
    global buffer
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
    Wallet = UserWallet.Open(path="infinitewallet", password="0123456789")
    logger.info("Created the Wallet")
    logger.info(Wallet.AddressVersion)
    walletdb_loop = task.LoopingCall(Wallet.ProcessBlocks)
    walletdb_loop.start(1)
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
    global smart_contract_hash
    global smart_contract
    smart_contract_hash = sys.argv[1]
    smart_contract = SmartContract(smart_contract_hash)
    main()

# Register an event handler for Runtime.Notify events of the smart contract.
@smart_contract.on_notify
def sc_log(event):
    logger.info(Wallet.AddressVersion)
    logger.info("SmartContract Runtime.Notify event: %s", event)

    # Make sure that the event payload list has at least one element.
    if not len(event.event_payload):
        return

    # Make sure not test mode
    if event.test_mode:
        return

    # The event payload list has at least one element. As developer of the smart contract
    # you should know what data-type is in the bytes, and how to decode it. In this example,
    # it's just a string, so we decode it with utf-8:
    logger.info("- payload part 1: %s", event.event_payload[0])
    price = BigInteger.FromBytes(event.event_payload[0])
    USD_price = float(price)/1000.0
    print(USD_price)
