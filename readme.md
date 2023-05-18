# Python ELK BLE Device Controller

This is a simple Python script that can be used to control a BLE device. It is designed to work with the ELK-BLE module, specifically a RGB-LED light strip controller.

## Requirements

These are the requirements of using this tool:

- One or more ELK-BLE light strips
- A computer with a BLE adapter
- A user with access to the BLE adapter
- Python 3.6 or higher
- Internet access to download the required Python libraries

## Installation

First, make sure you have Python and pip installed. Then, install the required libraries:

```bash
pip install -r requirements.txt
```

## Usage

Simply run the script with Python:

```bash
python3 main.py
```

## Features

This tool features:

- Scanning for compatible devices
- Automatic connection to the acquired devices
- Simultaneous control of multiple devices
- User-friendly CLI, with history and auto-completion enabled
- Full control over the BLE device, including color, effect, brightness and speed control, as well as scheduled on/off times
- Ability to sync the light with microphone input (Work in progress)

## Plans for the future

The following features are planned for the future:

- A GUI or TUI for easier control
- A web interface for remote control
- Synchronization with web resources, like calendars or weather
- Finish the microphone sync feature
