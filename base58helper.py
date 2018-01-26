from base58 import *
from neocore import Fixed8
from binascii import hexlify, unhexlify
from datetime import datetime
import pytz
from BinaryReader import BinaryReader
import io
from neocore.BigInteger import BigInteger
#from neo.Settings import settings
from neocore.Cryptography.Crypto import *
from neocore import UIntBase

#f = io.BytesIO(b'\x97afZ')
f = io.BytesIO(b'p\\x15\\x02')
#f =  io.BytesIO(b'\xa1\x16\x02')
reader = BinaryReader(f)


print(BigInteger.FromBytes(b'$pkZ'))

print(BigInteger.FromBytes(b'\xd8\x9dkZ'))
print(BigInteger.FromBytes(b'\xd8\x9dkZ'))
print(BigInteger.FromBytes(b'\x04\x9fkZ'))

b = BigInteger.FromBytes(b'\x04\x9fkZ')
print(BigInteger(136854).ToByteArray())
print("Yo")
print(b)

print(int(datetime.now().timestamp()))
#print(datetime.fromtimestamp(reader.ReadUInt32()))

print(datetime.fromtimestamp(1516658660))
print(datetime.fromtimestamp(1516658961))

#print(reader.ReadInt32())


def AddrStrToScriptHash(address):
    """
    Convert a public address to a script hash.
    Args:
        address (str): base 58 check encoded public address.
    Raises:
        ValueError: if the address length of address version is incorrect.
        Exception: if the address checksum fails.
    Returns:
        UInt160:
    """
    data = b58decode(address)
    if len(data) != 25:
        raise ValueError('Not correct Address, wrong length.')
    #if data[0] != settings.ADDRESS_VERSION:
        #raise ValueError('Not correct Coin Version')

    checksum = Crypto.Default().Hash256(data[:21])[:4]
    if checksum != data[21:]:
        raise Exception('Address format error')
    return UInt160(data=data[1:21])

hash = AddrStrToScriptHash('Aaaapk3CRx547bFvkemgc7z2xXewzaZtdP')
print(hash)

print(hash.ToArray())
