import asyncio
from uuid import UUID
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import time
from datetime import datetime

from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError

ibeacon_format = Struct(
    "type_length" / Const(b"\x02\x15"),
    "uuid" / Array(16, Byte),
    "major" / Int16ub,
    "minor" / Int16ub,
    "power" / Int8sl,
)

def device_found(
    device: BLEDevice, advertisement_data: AdvertisementData
):
    """Decode iBeacon."""
    formattedDate = ""
    try:
        apple_data = advertisement_data.manufacturer_data[0x004C]
        ibeacon = ibeacon_format.parse(apple_data)
        uuid = UUID(bytes=bytes(ibeacon.uuid))
        print(f"UUID : {uuid} TxPower : {ibeacon.power} dBm RSSI : {advertisement_data.rssi} dBm ({datetime.now()} second) MAJOR: {ibeacon.major} MINOR: {ibeacon.minor}")
        # if ibeacon.major == 41564 and ibeacon.minor == 24860:
        #     uuid = UUID(bytes=bytes(ibeacon.uuid))
        #     print(f"UUID : {uuid} TxPower : {ibeacon.power} dBm RSSI : {advertisement_data.rssi} dBm ({datetime.now()} second)")
            # print(f"Major    : {ibeacon.major}")
            # print(f"Minor    : {ibeacon.minor}")
            # print(f"TX power : {ibeacon.power} dBm")
            # print(f"RSSI     : {device.rssi} dBm")
    except KeyError:
        # Apple company ID (0x004c) not found
        pass
    except ConstError:
        # No iBeacon (type 0x02 and length 0x15)
        pass

async def main():
    """Scan for devices."""
    while True:
        resu = await BleakScanner().discover(return_adv=True)
        for deviceName, (device, AdvertisementData) in resu.items():
            device_found(device=device, advertisement_data=AdvertisementData)
        await asyncio.sleep(0.2)
asyncio.run(main())