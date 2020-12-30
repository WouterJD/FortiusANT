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

On macOS, on-board bluetooth is used, no need for an external dongle.

On Windows a bluetooth dongle is required, there is a limited set of supported hardware. It is important that your bluetooth dongle has one of the supported chipsets. See [node-bluetooth-hci-socket](https://github.com/noble/node-bluetooth-hci-socket#windows).

## Installation

### macOS

1. Install Xcode: [App Store](https://apps.apple.com/nl/app/xcode/id497799835?l=en&mt=12)
1. Install NodeJS: `brew install node`
1. Install dependencies: `cd node && npm install`

### Windows
1. Install Git for Windows (https://git-scm.com/downloads)
    * Only needed if not installed yet.
1. Install NodeJS LTS version (https://nodejs.org)
    * During installation, **check the box which installs the necessary tools for native modules**.
    * After NodeJS installation completes, a command prompt will appear which will install the necessary tools. This will take a while, grab a drink in the mean time.
1. Install Zadig (https://zadig.akeo.ie)
1. Insert the bluetooth dongle
1. Replace the driver for your bluetooth dongle using Zadig
    * Note that you cannot use the bluetooth dongle for windows itself when you perform this step. Using the exact same steps as mentioned below you can restore the old driver if you want.
    1. Start Zadig
    1. Select options, list all devices
    1. Select the bluetooth dongle
        * Note: It may be difficult to know which device is the correct BLE dongle in case your machine also has BLE on-board. Disable the on-board BLE device before inserting the BLE dongle so Zadig will see only one.
    1. Remember the current driver, in case you want to restore the driver later on.
    1. Check if WinUSB driver is set as target driver, this should be the default. (Choose the old driver when reverting)
    1. press Replace Driver

1. Install dependencies
    1. Start the windows command prompt
        1. Click start
        1. Type: `cmd`
        1. Press enter
    1. Go to the FortiusANT folder
        1. Type: `cd <FortiusANT location>\node`
            * `<FortiusANT location>` is the location where you downloaded FortiusANT to.
        1. Press enter
    1. Type: `npm install`
    1. Press enter

### Linux
TODO

## Run FortiusANT with BLE support

To use BLE support in FortiusANT it should be started from the command line with the `-b` option. When [Start] is pressed the BLE interface will be started until [Stop] is pressed. FortiusANT will start advertising as 'FortiusANT Trainer' on Windows and Linux systems. On macOS, it will start advertising as your computer name.
