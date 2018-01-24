import base58
from neocore import Fixed8
from binascii import hexlify, unhexlify
from datetime import datetime
import pytz
from BinaryReader import BinaryReader
import io
from neocore.BigInteger import BigInteger

#f = io.BytesIO(b'\x97afZ')
f = io.BytesIO(b'p\\x15\\x02')
reader = BinaryReader(f)

b = BigInteger.FromBytes(b'\xad\x13\x02')
print(BigInteger(136854).ToByteArray())
print("Yo")
print(b)

print(int(datetime.now().timestamp()))
#print(datetime.fromtimestamp(reader.ReadUInt32()))

print(datetime.fromtimestamp(1516658660))
print(datetime.fromtimestamp(1516658961))

print(reader.ReadInt32())