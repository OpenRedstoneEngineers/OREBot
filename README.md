# OREBot
OREBot is a Python 3 IRC bot written primarily for the Open Redstone Engineers community. It contains important features such as spam detection, and also provides hook and command APIs to customize the feature set.

## Package Overview
The bot has two main sections: official runtime code and a library.
- The library package may be used by custom-written code to create one's own IRC bot. It contains packages for the core classes, utilities, hooks and commands.
- The runtime package simply consists of a main script. This script is the code that is officially run by ORE, but is not required.

## Installation
The library package can be installed to your local machine using the `setup.py` script in the root of the repository. To install for all of the users on a machine, type `sudo python3 setup.py install` at a shell. If you do not have root privileges, you may install it for a single user with `python3 setup.py install --user`.

## Configuring and Running the Main Script
*Make sure you [install the libraries](#installation) before attempting to run the bot!*

Aside from the IRC libraries, the official script is written with Raygun compatibility. If you wish to use that, you will have to install the Raygun library with `sudo pip3 install raygun4py` or if you don't have root access: `pip3 install --user raygun4py`

The bot needs to be configured before first-time usage. Create a new file titled `config.json` in the bot's working directory, and put configuration parameters there. It must follow the same format as the `config.default.json` file provided with this repository; however, each parameter is optional and will default to the value in `config.default.json` if omitted.

After you are finished with the configuration process, you can now run the bot! Simply enter `python3 bin/main.py` into a shell, and the bot will connect to the server defined in the configuration file.

## Bugs and Feature Requests
This project is still in development, and there may be problems with our current codebase. If such errors are discovered, we ask that you [submit an issue](http://github.com/OpenRedstoneEngineers/OREBot/issues/new) describing the problem. We would also appreciate ideas for more official features; you can submit those using the same issue tracker.
