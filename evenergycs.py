#EvenergyCS.py (ChargeSchedule)
#Using Ev.Energy API: https://app.ev.energy/external-api.html

#Author: Jeremy Pack, (scriptengine) December, 2022

#LICENSE
#  Apache License
#  Version 2.0, January 2004
#  https://www.apache.org/licenses/LICENSE-2.0

#Purpose:
#   Using REST fetch an EV.Energy charging log and parse the schedule to 
#   Determine when charging will start and finish, and check for contigous
#   charging

#Inputs:
#   Token - Current EvEnergy Token
#   Session - Charging session ID

#Output:
#   Json sctructure of start-time, end-time and whether contiguous charge
#   Sample:
#            {
#                "startTime": "2022-11-23 00:30:00+00:00",
#                "endTime": "2022-11-23 04:30:00+00:00",
#                "contiguous": true,
#                "parsed": "09:14:44 23Nov"
#            }

#Sample Data: For sample of EV.Energy data see send of script

#Script name and strVersion strings
strScriptName = "EvEnergyChargeSchedule"
strVersion = "V1.2 23/11/2022"
blRunningOnWindows = False  # Set to true when debugging/ testing on Windows

#Logging level PICK One!
#logginglevel = 10 #Debug
#logginglevel = 20 #Info
logginglevel = 30 #Warning
#logginglevel = 40 #Error
#Possible logging levels in Home Assistant
#(in order from most severe to least severe)
#critical, fatal, error, warning, warn, info, debug, notset
#fatal, warn and notset do not have methods in Python's logger 

#------------------------------------------------------------------------------
#Functions

def WindowsPrint(strMessage):
    #Print message when running on Windows
    if blRunningOnWindows:
        #Copy message to Windows when developing on PC
        print(strMessage)

def Debug(strMessage):
    #Log message at debug level and print
    _LOGGER.debug(f'ERROR {strScriptName} {strMessage}')
    WindowsPrint(strMessage)

def Log(strMessage):
    #Log message at info level and print
    _LOGGER.info(f'{strScriptName} {strMessage}')
    WindowsPrint(strMessage)

#Function FatalExit
def FatalExit(strErrorMessage,err=None):
    # All errors causing program to end should terminate through FatalExit
    _LOGGER.error(f'FATAL ERROR: {strScriptName} {strErrorMessage}')
    if err is None :
        _LOGGER.error(err) #Only print error if one was passed
    _LOGGER.fatal(f'!!! {strScriptName} Fatal Error, terminating !!!')
    if err is None :
        exit(f'FATAL ERROR: {strErrorMessage}')
    else:
        exit(f'FATAL ERROR: {err}')
#------------------------------------------------------------------------------


#Try to start logging
try:
    import logging
except Exception as err:
    #FatalExit can't be used as logging has not started
    exit(f'ERROR {strScriptName} {err}') #Something is badly wrong, exit.
    #Messager will be returned into Home Assistant as result

#Starting logging
try:
    logging.basicConfig(filename=f'{strScriptName}.log',
                        level=max(10,(logginglevel or 0)),
                        format='%(asctime)s %(message)s')
    _LOGGER = logging.getLogger(__name__)
except Exception as err:
    exit(f'ERROR {strScriptName} {err}') #Logging failed!?

#Log Startup message at debug level (will be ignored normally)
Debug(f'*** {strScriptName} started (v: {strVersion}) ***')

#Python imports/ modules
Debug("Importing Python Modules")
try:
    import requests
    from requests.exceptions import HTTPError
    import json
    import sys
    from datetime import datetime
except Exception as err:
    FatalExit("Imports failed",err)

#Handle command line arguments
Debug("Command line arguments")
#Token and Charging strSessionID expected (and required)
numberofarguments = len(sys.argv) - 1
if numberofarguments == 0:
    FatalExit(f"Wrong number of arguments no aruguments passed/ found")
elif numberofarguments != 2:
    FatalExit(f"Wrong number of arguments, two required, {numberofarguments} found")

#Accept token
if None != sys.argv[1]:
    token = sys.argv[1]
    Debug("Token: " + token)

#Accept session id
if None != sys.argv[2]:
    strSessionID = sys.argv[2] #argv passed as a string
    if strSessionID.isnumeric() and int(strSessionID)>0:
        #strSessionID should be all digits
        Debug("Session Id: " + strSessionID)
    else:
        FatalExit(f'Session Id is not numeric ({strSessionID})')


#Setup the REST header with the token
strHeader = { 'Authorization' : f'Bearer {token}'}
Debug(f'header: {strHeader}')

#Setup URL
strURL = f'https://app.ev.energy/api/v1/charging-sessions/{strSessionID}/logs/'
Debug(f'header: {strURL}')

#Attempt REST call to Ev.Energy
Debug('Making REST/http request')
try: 
    response = requests.get(strURL, headers=strHeader)
                    #SSL issue: verify=False)
except Exception as err:
    FatalExit("Getting URL",err)

Debug('Checking for response for errors')
try:
    response.raise_for_status()
except HTTPError as err:
    FatalExit('HTTP error occurred', err)
except Exception as err:
    FatalExit('Other error occurred (raise_for_status)', err)

Debug('Converting JSON')
try:
    jsonResponse = response.json()
except Exception as err:
    FatalExit('Error converting json', err)


#Check REST status code and process data
Debug('Checking returned data')
if response.status_code != 200:
    #Bad status code
    FatalExit("REST return a Bad status", response.status_code) 
elif 'schedule' not in jsonResponse:
    #Data needs to have .schedule
    FatalExit("No schedule returned in JSON", "") 
else:
    #We have good data
    #Prepare to process the JSON
    Debug('Processing JSON')
    strStartTime = None
    strEndTime = None
    blALastChargeFound = False
    blContiguous = True #Is the charging contigous
                        #  or does it start, stop and restart
    blWasCharging = False

    #Work though each charge period
    #Note: The data gives the start of a period
    #      So the start of the first period where charging stops
    #      Is the time charging ends
    for schedule in jsonResponse["schedule"]:
        if (strStartTime is None) and (schedule["current"] > 0):
            #First time with charge current >0
            strStartTime = schedule["datetime"]
            strEndTime = strStartTime
            blWasCharging = True
        elif (strStartTime is not None) and (schedule["current"]!= 0):
            #strStartTime found previously and this is a charging period
            if blALastChargeFound:
                #Charge schedule previously ended charging and has now
                #restarted, signal charge is not blContiguous 
                blContiguous = False
            strEndTime = schedule["datetime"]
            blWasCharging = True
        elif (strEndTime is not None) and (schedule["current"]== 0):
            #Charge period has ended
            #Check if charging has just ended (this is the end time)
            if blWasCharging:
                strEndTime = schedule["datetime"]
            blWasCharging = False
            blALastChargeFound = True
        elif (strStartTime is None) and (schedule["current"]== 0):
            #Charge has not started yet
            pass
        else:
            #Unanticpiated combination
            FatalExit("Error in if elif else")
    #Print results when debugging
    Debug(f"     Start: {strStartTime}")
    Debug(f"       End: {strEndTime}")
    Debug(f"blContiguous: {blContiguous}")

#Put the results into JSON ready to pass back to HA
try:
    Debug('Creating JSON of results')
    strOutputData = {
        'startTime': strStartTime,
        'endTime': strEndTime,
        'contiguous': blContiguous,
        'parsed': datetime.now().strftime("%H:%M:%S %d%b") }
    jsonData = json.dumps(strOutputData, indent=4)
except Exception as err:
    FatalExit('Error occurred creating JSON', err)
Debug(jsonData)

#Log completetion and exit returning the JSON data
Log(f'--- {strScriptName} Exiting with data ---')
print(jsonData) #Data has to be printed to reach Home Assistant
#sys.exit(jsonData) #Does not work wiht Home Assistant Command_Line Sensor


#Sample Data:

# "schedule": [
#     {"datetime":"2022-11-22 21:30:00+00:00","current":0.0},
#     {"datetime":"2022-11-22 22:00:00+00:00","current":0.0},
#     {"datetime":"2022-11-22 22:30:00+00:00","current":32.0},
#     {"datetime":"2022-11-22 23:00:00+00:00","current":32.0},
#     {"datetime":"2022-11-22 23:30:00+00:00","current":32.0},
#     {"datetime":"2022-11-23 00:00:00+00:00","current":32.0},
#     {"datetime":"2022-11-23 00:30:00+00:00","current":0.0}
#   ]
