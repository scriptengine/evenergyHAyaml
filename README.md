# evenergyHAyaml
## Introduction

This code is a fully functioning prototype that creates sensors in Home Assistant from the [ev.energy](https://www.ev.energy/) API. With these sensors in Home Assistant you can check or see:
- If the EV is, or is not, plugged in to your charger
- The status of your charger in general
- The energy used and cost of the last charge
- When the car will start charging 
- The current or historical charge rate

[ev.energy](https://www.ev.energy/) is a cloud based service that manages  EV charging. In the UK the popular [ROLEC](https://www.rolecserv.com/) EV chargers are managed by ev.energy. 

The ev.energy API is currently read only for home users, so you can not control charging via Home Assistant, changing charging settings has to be done though the ev.energy app. The purpose of the API is to allow HA users to monitor charging of their car and alert when there are conditions that would stop the car charging.

In the long term this code needs to rewritten in Python as a Home Assistant integration. The purpose of this prototype was to quickly allow the Home Assistant community to start using the ev.energy API and to discuss what features/ sensors would be required in a full featured integration. And to allow ev.energy to see home users using the API and gain more of an understanding of the requirements, system impact and use cases.

**BUG** Need picture here 

## Installation
This code is only suitable for HA users that are happy to and know how to create and edit files in HA's config. Users new to HA or with limited experience should wait for HA integration.

### Prerequisites
**To use the ev.energy API with Home Assistant you need an API key from ev.energy**.
To get your API key email ev.energy support ( **support@ev.energy** ) with your **account name** (normally the email address you use to login to ev.energy)

**BUG** Work in Progress 24/01

### Installation

## Sensors

- list of sensors

## Use cases
- quick summary of use cases

## Interface components
- examples

