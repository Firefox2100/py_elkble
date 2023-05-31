import asyncio
import json
import os

from GUI import GUI
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import InMemoryHistory

from audio import Audio
from elkble import ELKDevice, Effects, DynamicModes

week_days = {
    'monday': None,
    'tuesday': None,
    'wednesday': None,
    'thursday': None,
    'friday': None,
    'saturday': None,
    'sunday': None,
    'all': None,
    'week_days': None,
    'weekend_days': None,
    'none': None,
}


class CLI:
    device = ELKDevice()
    audio = Audio()
    live_task = None
    tasks = []
    clients = []
    history = InMemoryHistory()
    nested_dict = {
        'add': None,
        'autoconnect': None,
        'brightness': None,
        'color': None,
        'connect': None,
        'disconnect': None,
        'dynamic': {
            'colorful': None,
            'beat_on': None,
            'beat_color': None,
            'beat_on_fast': None,
        },
        'effect': {
            'red': None,
            'blue': None,
            'green': None,
            'cyan': None,
            'yellow': None,
            'magenta': None,
            'white': None,
            'jump_rgb': None,
            'jump_rgbycmw': None,
            'gradient_rgb': None,
            'gradient_rgbycmw': None,
            'gradient_r': None,
            'gradient_g': None,
            'gradient_b': None,
            'gradient_y': None,
            'gradient_c': None,
            'gradient_m': None,
            'gradient_w': None,
            'gradient_rg': None,
            'gradient_rb': None,
            'gradient_gb': None,
            'blink_rgbycmw': None,
            'blink_r': None,
            'blink_g': None,
            'blink_b': None,
            'blink_y': None,
            'blink_c': None,
            'blink_m': None,
            'blink_w': None,
        },
        'exit': None,
        'live': {
            'start': None,
            'stop': None,
        },
        'power': {
            'on': None,
            'off': None,
        },
        'schedule': {
            'on': {
                'enable': week_days,
                'disable': week_days,
            },
            'off': {
                'enable': week_days,
                'disable': week_days,
            },
        },
        'search': None,
        'speed': None,
        'time': None,
    }

    def __init__(self):
        config = json.load(open('../clients.json'))
        for client in config['clients']:
            self.clients.append(client)
        if len(self.clients) != 0:
            name_dic = {client['name']: None for client in self.clients}
            for key in self.nested_dict['dynamic']:
                self.nested_dict['dynamic'][key] = name_dic
            for key in self.nested_dict['effect']:
                self.nested_dict['effect'][key] = name_dic

        self.completer = NestedCompleter.from_nested_dict(self.nested_dict)
        self.session = PromptSession(
            history=self.history,
            completer=self.completer,
        )

    async def process_input(self):
        while True:
            cmd = await self.session.prompt_async('> ')
            await self.process_command(cmd)

    async def audio_to_rgb(self, device_index=None):
        try:
            loop = asyncio.get_event_loop()
            self.audio.open()
            while True:
                audio_data = await loop.run_in_executor(None, self.audio.get_audio)
                r, g, b = Audio.audio_to_rgb(audio_data)
                if device_index is None:
                    for client in self.device.clients:
                        await self.device.set_color(client, r, g, b)
                else:
                    await self.device.set_color(self.device.clients[device_index], r, g, b)
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
            print(
                "Available commands: add, autoconnect, brightness, color, connect, disconnect, dynamic, effect, exit, "
                "live, power, schedule, search, speed, time")

        if cmd_parts[0] == "power":
            if len(cmd_parts) != 2 and len(cmd_parts) != 3:
                print("Invalid power command. Usage: power <on|off> [device_index]")
            if cmd_parts[1] == "on":
                if len(cmd_parts) == 2:
                    for client in self.device.clients:
                        await self.device.power_on(client)
                elif len(cmd_parts) == 3:
                    names = [client['name'] for client in self.clients]
                    if cmd_parts[2] in names:
                        await self.device.power_on(self.device.clients[self.clients[names.index(cmd_parts[2])]['id']])
                    else:
                        await self.device.power_on(self.device.clients[int(cmd_parts[2])])
                else:
                    print("Invalid power command. Usage: power on [device_index]")
            elif cmd_parts[1] == "off":
                if len(cmd_parts) == 2:
                    for client in self.device.clients:
                        await self.device.power_off(client)
                elif len(cmd_parts) == 3:
                    names = [client['name'] for client in self.clients]
                    if cmd_parts[2] in names:
                        await self.device.power_off(self.device.clients[self.clients[names.index(cmd_parts[2])]['id']])
                    else:
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
                names = [client['name'] for client in self.clients]
                if cmd_parts[2] in names:
                    await self.device.set_color(self.device.clients[self.clients[names.index(cmd_parts[2])]['id']],
                                                int(cmd_parts[1]), int(cmd_parts[2]), int(cmd_parts[3]))
                else:
                    await self.device.set_color(self.device.clients[int(cmd_parts[4])], int(cmd_parts[1]),
                                                int(cmd_parts[2]), int(cmd_parts[3]))
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
            elif len(cmd_parts) == 3:
                try:
                    effect = Effects.from_string(cmd_parts[1])
                except AttributeError:
                    print("Invalid effect name. Possible effects: " + str(Effects.to_list()))
                    return
                names = [client['name'] for client in self.clients]
                if cmd_parts[2] in names:
                    await self.device.set_effect(self.device.clients[self.clients[names.index(cmd_parts[2])]['id']],
                                                 effect)
                else:
                    await self.device.set_effect(self.device.clients[int(cmd_parts[2])], effect)
            else:
                print("Invalid effect command. Usage: effect <effect_name>")
        elif cmd_parts[0] == "dynamic":
            if len(cmd_parts) == 2:
                try:
                    dynamic = DynamicModes.from_string(cmd_parts[1])
                except AttributeError:
                    print("Invalid dynamic name. Possible dynamics: " + str(DynamicModes.to_list()))
                    return
                for client in self.device.clients:
                    await self.device.set_dynamic(client, dynamic)
            elif len(cmd_parts) == 3:
                try:
                    dynamic = DynamicModes.from_string(cmd_parts[1])
                except AttributeError:
                    print("Invalid dynamic name. Possible dynamics: " + str(DynamicModes.to_list()))
                    return
                names = [client['name'] for client in self.clients]
                if cmd_parts[2] in names:
                    await self.device.set_dynamic(self.device.clients[self.clients[names.index(cmd_parts[2])]['id']], dynamic)
                else:
                    await self.device.set_dynamic(self.device.clients[int(cmd_parts[2])], dynamic)
            else:
                print("Invalid dynamic command. Usage: dynamic <dynamic_name>")
        elif cmd_parts[0] == "speed":
            if len(cmd_parts) == 2:
                for client in self.device.clients:
                    await self.device.set_effect_speed(client, int(cmd_parts[1]))
            elif len(cmd_parts) == 3:
                names = [client['name'] for client in self.clients]
                if cmd_parts[2] in names:
                    await self.device.set_effect_speed(self.device.clients[self.clients[names.index(cmd_parts[2])]['id']],
                                                  int(cmd_parts[1]))
                else:
                    await self.device.set_effect_speed(self.device.clients[int(cmd_parts[2])], int(cmd_parts[1]))
            else:
                print("Invalid speed command. Usage: speed <speed> [device_index]")
        elif cmd_parts[0] == "brightness":
            if len(cmd_parts) == 2:
                for client in self.device.clients:
                    await self.device.set_brightness(client, int(cmd_parts[1]))
            elif len(cmd_parts) == 3:
                names = [client['name'] for client in self.clients]
                if cmd_parts[2] in names:
                    await self.device.set_brightness(self.device.clients[self.clients[names.index(cmd_parts[2])]['id']],
                                                  int(cmd_parts[1]))
                else:
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
        elif cmd_parts[0] == 'time':
            if len(cmd_parts) == 2:
                if cmd_parts[1] == 'now':
                    now = datetime.now()
                    for client in self.device.clients:
                        await self.device.set_time(client, now.hour, now.minute, now.second, now.weekday() + 1)
                else:
                    print("Invalid time command. Usage: time <time in h m s d|now> [device_index]")
            elif len(cmd_parts) == 3:
                if cmd_parts[1] == 'now':
                    now = datetime.now()
                    await self.device.set_time(self.device.clients[int(cmd_parts[2])], now.hour, now.minute,
                                               now.second, now.weekday() + 1)
            elif len(cmd_parts) == 5:
                for client in self.device.clients:
                    await self.device.set_time(client, int(cmd_parts[1]), int(cmd_parts[2]), int(cmd_parts[3]),
                                               int(cmd_parts[4]))
            elif len(cmd_parts) == 6:
                await self.device.set_time(self.device.clients[int(cmd_parts[5])], int(cmd_parts[1]), int(cmd_parts[2]),
                                           int(cmd_parts[3]), int(cmd_parts[4]))
            else:
                print("Invalid time command. Usage: time <time in h m s d|now> [device_index]")
        elif cmd_parts[0] == 'schedule':
            if len(cmd_parts) == 6:
                if cmd_parts[1] == 'on':
                    for client in self.device.clients:
                        await self.device.set_schedule_on(client, cmd_parts[3], int(cmd_parts[4]), int(cmd_parts[5]),
                                                          cmd_parts[2] == 'enabled')
                elif cmd_parts[1] == 'off':
                    for client in self.device.clients:
                        await self.device.set_schedule_off(client, cmd_parts[3], int(cmd_parts[4]), int(cmd_parts[5]),
                                                           cmd_parts[2] == 'enabled')
                else:
                    print(
                        "Invalid schedule command. Usage: schedule <on|off> <enabled|disabled> <days> <h> <m> ["
                        "device_index]")
            elif len(cmd_parts) == 7:
                if cmd_parts[1] == 'on':
                    await self.device.set_schedule_on(self.device.clients[int(cmd_parts[6])], cmd_parts[3],
                                                      int(cmd_parts[4]), int(cmd_parts[5]), cmd_parts[2] == 'enabled')
                elif cmd_parts[1] == 'off':
                    await self.device.set_schedule_off(self.device.clients[int(cmd_parts[6])], cmd_parts[3],
                                                       int(cmd_parts[4]), int(cmd_parts[5]), cmd_parts[2] == 'enabled')
                else:
                    print("Invalid schedule command. Usage: schedule <on|off> <enabled|disabled> <days> <h> <m> ["
                          "device_index]")
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
            if len(self.clients) != 0:
                for client in self.clients:
                    client['id'] = self.device.device_address.index(client['mac']) if client[
                                                                                          'mac'] in self.device.device_address else -1
        elif cmd_parts[0] == 'live':
            if len(cmd_parts) == 2:
                if cmd_parts[1] == 'start':
                    self.live_task = asyncio.create_task(self.audio_to_rgb())
                    self.tasks.append(self.live_task)
                elif cmd_parts[1] == 'stop':
                    self.live_task.cancel()
                    await self.live_task
                    self.tasks.remove(self.live_task)
                    self.live_task = None
                else:
                    print("Invalid command. Usage: live <start|stop> [device_index]")
            elif len(cmd_parts) == 3:
                if cmd_parts[1] == 'start':
                    self.live_task = asyncio.create_task(self.audio_to_rgb(int(cmd_parts[2])))
                    self.tasks.append(self.live_task)
                elif cmd_parts[1] == 'stop':
                    self.live_task.cancel()
                    await self.live_task
                    self.tasks.remove(self.live_task)
                    self.live_task = None
                else:
                    print("Invalid command. Usage: live <start|stop> [device_index]")
        elif cmd_parts[0] == 'exit':
            await self.device.disconnect()
            exit(0)
        else:
            print("Invalid command.")


if __name__ == '__main__':
    # cli = CLI()
    gui = GUI()
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    gui.open()
    # asyncio.run(cli.run())
