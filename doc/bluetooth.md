# FortiusANT with Bluetooth LE

FortiusANT was originally designed to provide an ANT+ interface to a Tacx Fortius. This requires the user to use ANT+ dongles in order to connect to applications such as Zwift.

On request of several users of FortiusANT support for BLE (Bluetooth Low Energy) has been added. When using the BLE interface the use of an ANT+ dongle is not mandatory anymore if you have supported BLE hardware.

## Design

The BLE support for FortiusANT is implemented in NodeJS, unlike FortiusANT itself which is written in Python. The implementation makes use of the very well working Bluetooth LE library [abandonware/bleno](https://github.com/abandonware/bleno).

Using this library FortiusANT is advertising the following services which can be discovered:
* FTMS (FiTness Machine Service)
* HRS (Heart Rate Service)

Communication between FortiusANT and the BLE server happens internally via a local http server where FortiusANT acts as the client and the BLE server as the server.

## Supported Hardware

Since BLE support in FortiusANT depends on the bleno library, hardware support is also limited to what bleno supports.

For Windows, there is a limited set of supported hardware, see [node-bluetooth-hci-socket](https://github.com/noble/node-bluetooth-hci-socket#windows).

## Installation

### macOS

1. Install Xcode: [App Store](https://apps.apple.com/nl/app/xcode/id497799835?l=en&mt=12)
2. Install NodeJS: `brew install node`
3. Install dependencies: `cd node && npm install`

### Windows
1. Follow steps in [this](https://youtu.be/mL9B8wuEdms?t=80) youtube video to install:
    1. NodeJS
    2. Replace Bluetooth driver using Zadig tool
2. Install dependencies: `cd node && npm install`

### Linux
TODO

## Run FortiusANT with BLE support

To use BLE support in FortiusANT it should be started from the command line with the `-b` option.
