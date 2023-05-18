from bleak import BleakClient, BleakScanner, BLEDevice

CHARACTERISTIC_UUID = '0000fff3-0000-1000-8000-00805f9b34fb'


class Effects:
    red = b'\x80'
    blue = b'\x81'
    green = b'\x82'
    cyan = b'\x83'
    yellow = b'\x84'
    magenta = b'\x85'
    white = b'\x86'
    jump_rgb = b'\x87'
    jump_rgbycmw = b'\x88'
    gradient_rgb = b'\x89'
    gradient_rgbycmw = b'\x8a'
    gradient_r = b'\x8b'
    gradient_g = b'\x8c'
    gradient_b = b'\x8d'
    gradient_y = b'\x8e'
    gradient_c = b'\x8f'
    gradient_m = b'\x90'
    gradient_w = b'\x91'
    gradient_rg = b'\x92'
    gradient_rb = b'\x93'
    gradient_gb = b'\x94'
    blink_rgbycmw = b'\x95'
    blink_r = b'\x96'
    blink_g = b'\x97'
    blink_b = b'\x98'
    blink_y = b'\x99'
    blink_c = b'\x9a'
    blink_m = b'\x9b'
    blink_w = b'\x9c'

    @classmethod
    def from_string(cls, string: str) -> bytes:
        return getattr(cls, string)

    @classmethod
    def to_list(cls) -> list[str]:
        return [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")]


class Days:
    monday = b'\x01'
    tuesday = b'\x02'
    wednesday = b'\x04'
    thursday = b'\x08'
    friday = b'\x10'
    saturday = b'\x20'
    sunday = b'\x40'
    all = b'\x7f'
    week_days = b'\x1f'
    weekend_days = b'\x60'
    none = b'\x00'

    @classmethod
    def from_string(cls, string: str) -> bytes:
        return getattr(cls, string)

    @classmethod
    def to_list(cls) -> list[str]:
        return [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")]


class ELKDevice:
    device_address = []
    clients: list[BleakClient] = []

    async def connect(self):
        for address in self.device_address:
            client = BleakClient(address)
            await client.connect()
            self.clients.append(client)

    async def disconnect(self):
        for client in self.clients:
            await client.disconnect()
            self.clients.remove(client)

    def add_address(self, address: str):
        self.device_address.append(address)

    @staticmethod
    async def search() -> list[BLEDevice]:
        scanner = BleakScanner()
        devices = await scanner.discover()

        target_devices = [dev for dev in devices if 'ELK-BLEDOM' in dev.name]
        return target_devices

    @staticmethod
    async def power_on(client: BleakClient):
        await client.write_gatt_char(CHARACTERISTIC_UUID, b'\x7e\x00\x04\xf0\x00\x01\xff\x00\xef')

    @staticmethod
    async def power_off(client: BleakClient):
        await client.write_gatt_char(CHARACTERISTIC_UUID, b'\x7e\x00\x04\x00\x00\x00\xff\x00\xee')

    @staticmethod
    async def set_brightness(client: BleakClient, brightness: int):
        command = b'\x7e\x00\x01'
        command += bytes([min(brightness, 0x64)])
        command += b'\x00\x00\x00\x00\xef'

        await client.write_gatt_char(CHARACTERISTIC_UUID, command)

    @staticmethod
    async def set_color(client: BleakClient, r: int, g: int, b: int):
        command = b'\x7e\x00\x05\x03'
        command += bytes([r, g, b])
        command += b'\x00\xef'

        await client.write_gatt_char(CHARACTERISTIC_UUID, command)

    @staticmethod
    async def set_effect(client: BleakClient, effect: bytes):
        command = b'\x7e\x00\x03'
        command += effect
        command += b'\x03\x00\x00\x00\xef'

        await client.write_gatt_char(CHARACTERISTIC_UUID, command)

    @staticmethod
    async def set_effect_speed(client: BleakClient, speed: int):
        command = b'\x7e\x00\x02'
        command += bytes([speed])
        command += b'\x00\x00\x00\x00\xef'

        await client.write_gatt_char(CHARACTERISTIC_UUID, command)

    @staticmethod
    async def set_time(client: BleakClient, hour: int, minute: int, second: int, day_of_week: int):
        command = b'\x7e\x00\x83'
        command += bytes([hour, minute, second, day_of_week])
        command += b'\x00\xef'

        await client.write_gatt_char(CHARACTERISTIC_UUID, command)

    @staticmethod
    async def set_schedule_on(client: BleakClient, days: str, hour: int, minute: int, enable: bool):
        if enable:
            value = bytes([int(Days.from_string(days)) + 0x80])
        else:
            value = Days.from_string(days)

        command = b'\x7e\x00\x82'
        command += bytes([hour, minute])
        command += b'\x00\x00'
        command += value
        command += b'\xef'

        await client.write_gatt_char(CHARACTERISTIC_UUID, command)

    @staticmethod
    async def set_schedule_off(client: BleakClient, days: str, hour: int, minute: int, enable: bool):
        if enable:
            value = bytes([int(Days.from_string(days)) + 0x80])
        else:
            value = Days.from_string(days)

        command = b'\x7e\x00\x82'
        command += bytes([hour, minute])
        command += b'\x00\x01'
        command += value
        command += b'\xef'

        await client.write_gatt_char(CHARACTERISTIC_UUID, command)


if __name__ == "__main__":
    device = ELKDevice()
    device.add_address("BE:59:2B:01:22:53")
    device.connect()
    print(device.clients)
