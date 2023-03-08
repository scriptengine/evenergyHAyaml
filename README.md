# evenergyHAyaml

![Snippet of ev.energy status in Home Assistant](/images/StatusSummary.jpg "ev.energy Status example")

## Introduction

This code is a fully functioning prototype that creates sensors in Home Assistant from the [ev.energy](https://www.ev.energy/) API. With these sensors in Home Assistant you can check or see:
- If your EV is (or is not) plugged in to your charger
- When the car will start charging 
- The current or historical charge rate
- The status of your charger in general
- The energy used and cost of the last charge

![Charging rate graph](/images/ChargeRate.jpg "EV charging rate from ev.energy")

[ev.energy](https://www.ev.energy/) is a cloud based service that manages  EV charging. In the UK the popular [ROLEC](https://www.rolecserv.com/) EV chargers are managed by ev.energy. 

The ev.energy API is currently read only for home users, so you can not control charging via Home Assistant; changing charging settings has to be done though the ev.energy app. The purpose of this code is to allow HA users to monitor charging of their car and alert when there are conditions that would stop the car charging.

In the long term this code needs to rewritten in Python as a Home Assistant integration. The purpose of this prototype was:
- to quickly allow the Home Assistant community to start using the ev.energy API.
- with that experience discuss what features/ sensors would be required in a full featured integration.
- to allow ev.energy to see home users using the API and gain more of an understanding of the requirements, system impact and use cases.



## Use cases
I'd be very interested to know what other HA users use the ev.energy API for. My use cases are:

- Alerts at 6,8,9 & 10pm that the car is home and not plugged in. (We use a BLE sensor to detect the car is home. Alerts are via a HA display on our landing and turning our lounge lamp red.)
- Alert (with 5 minutes grace) if the car returns home and is not plugged in
- Alert, on a display, if ev.energy or the charger is offline or locked
- How much the car charged (kWh) and the cost of the overnight charge in our wall display(s) of home energy use
- Charger/ EV status summerised in HA wall display
- Historical analysis of EV charging

## Installation
**This code is only suitable for HA users that are happy to, and know how to, create and edit files in HA's config.** Users new to HA or with limited experience should wait for a HA integration.

### Prerequisites
**To use the ev.energy API with Home Assistant you need an API key from ev.energy**.
To get your API key email ev.energy support (**<support@ev.energy>**) with your **account name** (normally the email address you use to login to ev.energy).

To add the code you can probably use the basic [File editor](https://www.home-assistant.io/getting-started/configuration/#:~:text=To%20get%20to%20the%20add,Editor%20and%20click%20on%20Install) add-on in Home Assistant, I personally use the [Visual Studio Code](https://community.home-assistant.io/t/install-vscode-community-addon/322570) and [Filebrowser](https://github.com/alexbelgium/hassio-addons) add-ons.

### Installation
Getting the code working requires 5 steps and will involve you creating or editing a directory and 4 files:

    ├── config
        ├── configuration.yaml
        ├── secrets.yaml
        ├── evenergycs.yaml
        └──  python_scripts
            └──  evenergy.py
    ├── other existing files and folders in config)
**Add your API Key as a secret**

1 If you do not have a *secrets.yaml* create *secrets.yaml* file in the HA *config* directory

2 Add your API key in secrets.yaml for example:

    evenergy_Auth: "U7Y36IhIL5s6ofFPoeHjwGxYxBVApu"
(this is an example only, the key above will not work for you; you need to get your own API key from ev.energy, see above. )

**Add evenergy.yaml**

The main logic is in the file *evenergy.yaml*
I recommend you:

1 Create, or copy, *evenergy.yaml* into HA's *config* directory.

2 Add *evenergy.yaml* as a package that HA runs from *configuration.yaml*. For example, edit *configuration.yaml* and add the lines:

    packages:
        pack_1: !include evenergy.yaml

**Add evenergycs.py**

*evenergycs.py* is a small script that parses the charging schedule. If it's missing it won't be a problem; only the charging schedule sensors will not be populated (and their will be errors in the log file).

*evenergycs.py* needs to be located in a directory name *python_scripts* in *config*. That is you need the following folder structure:

    config/python_scripts

(You can create the directory and file from both File editor and Visual Studio Code.)

**Check (before restart)**

Before restarting Home Assistant check your edits have not created configuration issues. (Do not restart HA until the issues are fixed.)


(Developer Tools / YAML / **Check Configuration** )

**Restart Home Assistant**

Restart Home Assistant.

After HA has fully restated you can quickly check if the code is working by looking for any sensors with evenergy in the name in the Developer Tools/ States interface.

![Filtered Sensors](/images/FilterSesnsors.jpg "Filtered Sensors")

## Sensors

### Headline Status
There is a single sensor summarising the charger's status:
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
For example if the sensor: 

    evenergy_ev_pluggedin

is *true*, each of the preceding sensors:

    evenergy_api_online
    evenergy_api_loggedin
    evenergy_charger_online

will also be *true*.

### Charger Configuration
The following sensors are related to the status of the charger:
| Name      | Purpose & Expected Values |
| ----------- | ----------- |
sensor.evenergy_charger_chargerstatus|CONNECTED CHARGING or DISCONNECTED
sensor.evenergy_charger_connectivity| Online
sensor.evenergy_charger_lockmode| UNLOCKED SMART (ie Smart locked) LOCKED (holiday lock)

Additionally the following values are made available by the API but are more related to the installation of the charger than its use.

- sensor.evenergy_charger_chargerstage
- sensor.evenergy_charger_chargerstage_date
- sensor.evenergy_charger_controllable
- sensor.evenergy_evse

### Charging Session
The ev.energy API uses the concept of a charging *session*. Each time the EV is plugged in or the charging configuration is changed, for example the charge mode is changed from SMART to unmanaged, a new charging session is created.

The code creates sensors for the current session and the previous session. When the car is plugged in the current session probably contains the values you will be interested in. When the car has been unplugged you can use the previous session to check data such of energy used and cost.

The ev.energy session id for the current and previous charging sessions are available from:
- sensor.evenergy_currentsession_id
- sensor.evenergy_previoussession_id


| Name      | Purpose or Expected Values |
| ----------- | ----------- |
sensor.evenergy_currentsession_chargerate | EV charging rate
sensor.evenergy_currentsession_chargingstatus| *connected*, *charging*, *none*
sensor.evenergy_currentsession_chargingtype| *smart* or unmanaged(*)
sensor.evenergy_currentsession_schedule_begin | For smart charging the time the schedule for Smart charging is defined from
sensor.evenergy_currentsession_schedule_end| For smart charging the last period the schedule is defined to (normally the time you have set your car needs to be charged by)
sensor.evenergy_currentsession_schedule_chargingcontiguous| *true* if the smart charging schedule is for a contiguous charging period. *false* if the charging is scheduled to stop and later restart
sensor.evenergy_currentsession_schedule_chargingstart|For smart charging when charging will start
sensor.evenergy_currentsession_schedule_chargingend|For smart charging when charging will end 
sensor.evenergy_currentsession_start| The time the car was plugged in
sensor.evenergy_currentsession_startpretty| The time the car was plugged in formatted for display
sensor.evenergy_currentsession_totalaltcost| see ev.energy documentation
sensor.evenergy_currentsession_totalcarbonemissions| see ev.energy documentation
sensor.evenergy_currentsession_totalcost| see ev.energy documentation
sensor.evenergy_currentsession_totalcost_currency| In the UK GBP, USD is an option
sensor.evenergy_currentsession_totalenergydelivered| Total energy delivered during this session. The value updates whilst the EV is charging

Less Interesting sensors:
| Name      | Purpose |
| ----------- | ----------- |
sensor.evenergy_currentsession| Stub for information not picked up in any other sensor
sensor.evenergy_currentchargesession_id| Id of the current charging session
sensor.evenergy_currentsession_chargesensor| The sensor measuring the charging rate. *EVSE* is the charger, for other values see eve.energy documentation

The following values are less useful for the current charging session as they are not set until the session has ended.
- sensor.evenergy_currentsession_duration
- sensor.evenergy_currentsession_end
- sensor.evenergy_currentsession_endpretty 

Note:
- For values marked * check the exact value returned.
- The charging schedule values are populated by the Python script and generally update after the session values. 

### Previous Charging Session
The sensors and values for the previous charging session are similar to those above for the current session. Note:
Sensor names are prefixed:

    sensor.evenergy_previoussession
For example cost of charging is:

    sensor.evenergy_previoussession_totalcost

For the previous session the values for duration and end time are populated by the API.

### Overnight charging values
For my own purposes the code attempts to calculate the energy used and the cost of charging the car overnight. These values are not calculated or defined by ev.energy there are calculated in the code. The calculation is based on a bunch of assumptions about when the car is plugged in and when it should charge. The code will break and return none if these assumptions are invalid or something unexpected happens and often when HA is restarted. If you are on Octopus GO this calculation is probably what you want. If you are on other tariffs you may want to ignore these values or look at the logic and adapt it (and share it?)
| Name      | Purpose |
| ----------- | ----------- |
sensor.evenergy_energy_overnight|Total energy used charging EV overnight (kWh)
sensor.evenergy_energy_overnightcost|Cost of charging overnight


### Private values
There are a small number of sensors prefixed *private* which are required and used by the code internally, or intended for support. These are not intended to be displayed or modified. 

## Documentation
The ev.energy API is documented at: https://app.ev.energy/external-api.html

Currently (Jan2023) while ev.energy is testing and developing access for individual users the API Key access method is not documented. Additionally the API key for home users only gives access to a subset of the API. The parts we don't have access to are generally related to fleet operations and are of no interest to uses of HA. 

If you are interested in developing or modifying the code, or need to know more about each values I recommend you dive into the openAPI specification:
https://app.ev.energy/external-api-docs-schema

Finally, there are significant volumes of comments in the code documenting its operation.

## Limitations
Currently the code does not support:
- Solar charging (I don't use ev.energy solar charging to be able to test it)
- Reading the charge state of the car (nissan don't have an API for ev.energy to use )

## Interface Examples 
There are code snippets for the interface display in examples

### examples\OvernightChargeAndCost.yaml
![Overnight Charge](/images/ChargeAndCost.jpg "Snippet showing energy used and cost of overnight charge")
