import asyncio
from elkble import ELKDevice, Effects

device = ELKDevice()


async def process_command(cmd: str):
    cmd_parts = cmd.split()

    if len(cmd_parts) == 0:
        print("Available commands: power, brightness, color, search, connect, autoconnect, disconnect, add, exit")

    if cmd_parts[0] == "power":
        if len(cmd_parts) != 2 and len(cmd_parts) != 3:
            print("Invalid power command. Usage: power <on|off> [device_index]")
        if cmd_parts[1] == "on":
            if len(cmd_parts) == 2:
                for client in device.clients:
                    device.power_on(client)
            elif len(cmd_parts) == 3:
                device.power_on(device.clients[int(cmd_parts[2])])
            else:
                print("Invalid power command. Usage: power on [device_index]")
        elif cmd_parts[1] == "off":
            if len(cmd_parts) == 2:
                for client in device.clients:
                    device.power_off(client)
            elif len(cmd_parts) == 3:
                device.power_off(device.clients[int(cmd_parts[2])])
            else:
                print("Invalid power command. Usage: power off [device_index]")
        else:
            print("Invalid power command. Usage: power <on|off> [device_index]")
    elif cmd_parts[0] == "color":
        if len(cmd_parts) == 4:
            for client in device.clients:
                device.set_color(client, int(cmd_parts[1]), int(cmd_parts[2]), int(cmd_parts[3]))
        if len(cmd_parts) == 5:
            device.set_color(device.clients[int(cmd_parts[4])], int(cmd_parts[1]), int(cmd_parts[2]), int(cmd_parts[3]))
        else:
            print("Invalid color command. Usage: color <r> <g> <b> [device_index]")
    elif cmd_parts[0] == "effect":
        if len(cmd_parts) == 2:
            try:
                effect = Effects.from_string(cmd_parts[1])
            except AttributeError:
                print("Invalid effect name. Possible effects: " + str(Effects.to_list()))
                return
            for client in device.clients:
                await device.set_effect(client, effect)
        else:
            print("Invalid effect command. Usage: effect <effect_name>")
    elif cmd_parts[0] == "brightness":
        if len(cmd_parts) == 2:
            for client in device.clients:
                device.set_brightness(client, int(cmd_parts[1]))
        if len(cmd_parts) == 3:
            device.set_brightness(device.clients[int(cmd_parts[2])], int(cmd_parts[1]))
        else:
            print("Invalid brightness command. Usage: brightness <brightness> [device_index]")
    elif cmd_parts[0] == 'connect':
        await device.connect()
    elif cmd_parts[0] == 'disconnect':
        await device.disconnect()
    elif cmd_parts[0] == 'add':
        for address in cmd_parts[1:]:
            device.add_address(address)
    elif cmd_parts[0] == 'search':
        devices = await device.search()
        for i, dev in enumerate(devices):
            print(f"{i}: {dev.address}")
    elif cmd_parts[0] == 'autoconnect':
        devices = await device.search()
        for dev in devices:
            device.add_address(dev.address)
            print(f"Added {dev.address} to autoconnect list.")
        await device.connect()
    elif cmd_parts[0] == 'exit':
        await device.disconnect()
        exit(0)
    else:
        print("Invalid command.")


async def main():
    while True:
        cmd = input('> ')
        await process_command(cmd)

if __name__ == '__main__':
    asyncio.run(main())
