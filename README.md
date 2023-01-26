# evenergyHAyaml
## Introduction

This code is a fully functioning prototype that creates sensors in Home Assistant from the [ev.energy](https://www.ev.energy/) API. With these sensors in Home Assistant you can check or see:
- If the EV is, or is not, plugged in to your charger
- The status of your charger in general
- The energy used and cost of the last charge
- When the car will start charging 
- The current or historical charge rate

[ev.energy](https://www.ev.energy/) is a cloud based service that manages  EV charging. In the UK the popular [ROLEC](https://www.rolecserv.com/) EV chargers are managed by ev.energy. 

The ev.energy API is currently read only for home users, so you can not control charging via Home Assistant, changing charging settings has to be done though the ev.energy app. The purpose of this code is to allow HA users to monitor charging of their car and alert when there are conditions that would stop the car charging.

In the long term this code needs to rewritten in Python as a Home Assistant integration. The purpose of this prototype was:
- to quickly allow the Home Assistant community to start using the ev.energy API.
- with that experience discuss what features/ sensors would be required in a full featured integration.
- to allow ev.energy to see home users using the API and gain more of an understanding of the requirements, system impact and use cases.

![Snippet of ev.energy status in Home Assistant](/images/StatusSummary.jpg "ev.energy Status example")
![Charging rate graph](/images/ChargeRate.jpg "EV charging rate from ev.energy")

## Installation
This code is only suitable for HA users that are happy to, and know how to, create and edit files in HA's config. Users new to HA or with limited experience should wait for a HA integration.

### Prerequisites
**To use the ev.energy API with Home Assistant you need an API key from ev.energy**.
To get your API key email ev.energy support (**<support@ev.energy>**) with your **account name** (normally the email address you use to login to ev.energy).

To add the code you can probably use the basic [File editor](https://www.home-assistant.io/getting-started/configuration/#:~:text=To%20get%20to%20the%20add,Editor%20and%20click%20on%20Install) add-on in Home Assistant, I personally use the [Visual Studio Code](https://community.home-assistant.io/t/install-vscode-community-addon/322570) and [Filebrowser](https://github.com/alexbelgium/hassio-addons) add-ons.

### Installation
Getting the code working requires 3 steps:

**Add your API Key as a secret**

1 If you do not have a *secrets.yaml* create *secrets.yaml* file in the HA *config* directory

2 Add your API key in secrets.yaml for example:

    evenergy_Auth: "U7Y36IhIL5s6ofFPoeHjwGxYxBVApu"
(this is an example only, the key above will not work for you; you need to get your own API key from ev.energy, see above. )

**Add evenergy.yaml**

The main logic is in the file *evenergy.yaml*
I recommend you:

1 Create or copy *evenergy.yaml* into HA's *config* directory.

2 Add *evenergy.yaml* as a package that HA runs from *configuration.yaml*. For example, edit *configuration.yaml* and add the lines:

    packages:
        pack_1: !include evenergy.yaml

**Add evenergycs.py**

*evenergy.py* is a small script that parses the charging schedule. If it's missing it won't be a problem; only the charging schedule sensors will not be populated (and their will be errors in the log file).

*evenergy.py* needs to be located in a directory name *python_scripts* in *config*. That is you need the folder structure:

    config/python_scripts

(You can create the directory and file from both File editor and Visual Studio Code.)

**Check (before restart)**
Before restarting Home Assistant check your edits have not created configuration issues.

(Developer Tools / YAML / **Check Configuration** )

**Restart Home Assistant**

Use your favourite method to restart Home Assistant.

## Sensors

### Headline Status
There is a single sensor summerising the chargers status:
| Name      | Purpose & Values |
| ----------- | ----------- |
| sensor.evenergy_status      | One of:
|| Plugged In
|| NOT Plugged In
|| Fault - Charger OFFLine
|| Error-StateUndefined

There are also binary sensors that can be tested directly:
| Name      | Purpose & Values |
| ----------- | ----------- |
|binary_sensor.evenergy_api_online| true/false
|binary_sensor.evenergy_api_loggedin| true/false
|binary_sensor.evenergy_charger_online| true/false
|binary_sensor.evenergy_ev_pluggedin| true/false
|binary_sensor.evenergy_charging_inprogress| true/false

The binary sensors are related in the order above.
For example if: 

    evenergy_ev_pluggedin

is true

each of:

    evenergy_api_online
    evenergy_api_loggedin
    evenergy_charger_online

will also be true.


- list of sensors

## Use cases
- quick summary of use cases

## Interface components
- examples
