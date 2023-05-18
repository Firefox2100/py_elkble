import asyncio
from elkble import ELKDevice, Effects
from audio import Audio
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

history = InMemoryHistory()
session = PromptSession(history=history)


async def async_input(prompt: str = ""):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, session.prompt, prompt)


class CLI:
    device = ELKDevice()
    audio = Audio()
    live_task = None
    tasks = []

    async def process_input(self):
        while True:
            cmd = await async_input('> ')
            await self.process_command(cmd)

    async def audio_to_rgb(self):
        try:
            loop = asyncio.get_event_loop()
            self.audio.open()
            while True:
                audio_data = await loop.run_in_executor(None, self.audio.get_audio)
                r, g, b = Audio.audio_to_rgb(audio_data)
                for client in self.device.clients:
                    await self.device.set_color(client, r, g, b)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        finally:
            self.audio.close()

    async def run(self):
        self.tasks.append(asyncio.create_task(self.process_input()))
        await asyncio.gather(*self.tasks)

    async def process_command(self, cmd: str):
        cmd_parts = cmd.split()

        if len(cmd_parts) == 0:
            print("Available commands: power, brightness, color, live, search, connect, autoconnect, disconnect, add, "
                  "exit")

        if cmd_parts[0] == "power":
            if len(cmd_parts) != 2 and len(cmd_parts) != 3:
                print("Invalid power command. Usage: power <on|off> [device_index]")
            if cmd_parts[1] == "on":
                if len(cmd_parts) == 2:
                    for client in self.device.clients:
                        await self.device.power_on(client)
                elif len(cmd_parts) == 3:
                    await self.device.power_on(self.device.clients[int(cmd_parts[2])])
                else:
                    print("Invalid power command. Usage: power on [device_index]")
            elif cmd_parts[1] == "off":
                if len(cmd_parts) == 2:
                    for client in self.device.clients:
                        await self.device.power_off(client)
                elif len(cmd_parts) == 3:
                    await self.device.power_off(self.device.clients[int(cmd_parts[2])])
                else:
                    print("Invalid power command. Usage: power off [device_index]")
            else:
                print("Invalid power command. Usage: power <on|off> [device_index]")
        elif cmd_parts[0] == "color":
            if len(cmd_parts) == 4:
                for client in self.device.clients:
                    await self.device.set_color(client, int(cmd_parts[1]), int(cmd_parts[2]), int(cmd_parts[3]))
            elif len(cmd_parts) == 5:
                await self.device.set_color(self.device.clients[int(cmd_parts[4])], int(cmd_parts[1]), int(cmd_parts[2]), int(cmd_parts[3]))
            else:
                print("Invalid color command. Usage: color <r> <g> <b> [device_index]")
        elif cmd_parts[0] == "effect":
            if len(cmd_parts) == 2:
                try:
                    effect = Effects.from_string(cmd_parts[1])
                except AttributeError:
                    print("Invalid effect name. Possible effects: " + str(Effects.to_list()))
                    return
                for client in self.device.clients:
                    await self.device.set_effect(client, effect)
            else:
                print("Invalid effect command. Usage: effect <effect_name>")
        elif cmd_parts[0] == "brightness":
            if len(cmd_parts) == 2:
                for client in self.device.clients:
                    await self.device.set_brightness(client, int(cmd_parts[1]))
            elif len(cmd_parts) == 3:
                await self.device.set_brightness(self.device.clients[int(cmd_parts[2])], int(cmd_parts[1]))
            else:
                print("Invalid brightness command. Usage: brightness <brightness> [device_index]")
        elif cmd_parts[0] == 'connect':
            await self.device.connect()
        elif cmd_parts[0] == 'disconnect':
            await self.device.disconnect()
        elif cmd_parts[0] == 'add':
            for address in cmd_parts[1:]:
                self.device.add_address(address)
        elif cmd_parts[0] == 'search':
            devices = await self.device.search()
            for i, dev in enumerate(devices):
                print(f"{i}: {dev.address}")
        elif cmd_parts[0] == 'autoconnect':
            devices = await self.device.search()
            for dev in devices:
                self.device.add_address(dev.address)
                print(f"Added {dev.address} to autoconnect list.")
            await self.device.connect()
        elif cmd_parts[0] == 'live':
            self.live_task = asyncio.create_task(self.audio_to_rgb())
            self.tasks.append(self.live_task)
        elif cmd_parts[0] == 'stop':
            self.live_task.cancel()
            await self.live_task
        elif cmd_parts[0] == 'exit':
            await self.device.disconnect()
            exit(0)
        else:
            print("Invalid command.")


if __name__ == '__main__':
    cli = CLI()
    asyncio.run(cli.run())
