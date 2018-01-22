import base58
from neocore import Fixed8
from binascii import hexlify, unhexlify
from datetime import datetime
import pytz
from BinaryReader import BinaryReader
import io

f = io.BytesIO(b'\x97afZ')
reader = BinaryReader(f)


print(int(datetime.now().timestamp()))
print(datetime.fromtimestamp(reader.ReadUInt32()))

print(datetime.fromtimestamp(1516658660))
print(datetime.fromtimestamp(1516658961))
