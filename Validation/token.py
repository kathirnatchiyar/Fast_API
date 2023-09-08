
import traceback
from Crypto.Cipher import AES
from datetime import datetime
import time
from base64 import b64decode,b64encode
import base64
import pytz
import json
from Database.Connection import createsysdbConnectionPooling

def tokenValidation(privilegeName,requestJson,rheaders):
    try:
        sysdbPoolingObject = createsysdbConnectionPooling()
        sysdbConnection = sysdbPoolingObject.get_connection()
        ruleInformationList = []
        validateHeaders(rheaders, requestJson, ruleInformationList)
        if(len(ruleInformationList) != 0):
            return ruleInformationList
        transDict = requestJson.copy()
        transDict['headers'] = rheaders
        decryptedToken = decryptToken(transDict,sysdbConnection,ruleInformationList)
        if(len(ruleInformationList) == 0):
            validateToken(transDict,decryptedToken,privilegeName,ruleInformationList)
        return ruleInformationList
    except Exception as exception:
        print(traceback.format_exc())
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)
        return ruleInformationList
        
    
def decryptToken(transDict,sysdbConnection,ruleInformationList):
    try:
        syscursor = sysdbConnection.cursor(dictionary=True)
        encryptedToken = transDict['headers']['Token']
        # print(transDict)
        keyfetchingsql = "SELECT PARAMETER_VALUE FROM OWNER_CONFIG WHERE OWNER_ID="+transDict['ownerId']+" AND PARAMETER_NAME = 'TOKEN::AES::ENCRYPTION/DECRYPTION' AND ACTIVE = 'Y' LIMIT 1"
        syscursor.execute(keyfetchingsql)
        resultData = syscursor.fetchone()
        if(resultData != None):
            decryptionKey = resultData['PARAMETER_VALUE']
            tokenbytes = bytes(encryptedToken, 'utf-8')
            enctoken = b64decode(tokenbytes)
            #Convert the pre shared key from string to bytes.
            key = bytes(decryptionKey, 'utf-8')
            cipher_obj = AES.new(key, AES.MODE_ECB)
            decoded_token = cipher_obj.decrypt(enctoken).decode('utf8')
            return decoded_token
        else:
            errorDict = {}
            errorDict['Error'] = "Token Preshared Key Not Found"
            ruleInformationList.append(errorDict)         
    #If the Number of characters in token is less than the actual character length of token
    except UnicodeDecodeError:
        errorDict = {}
        errorDict['Error'] = "Invalid Token, UnicodeDecodeError"
        ruleInformationList.append(errorDict)
    #If the Token is Invalid
    except base64.binascii.Error:
        errorDict = {}
        errorDict['Error'] = "Invalid Token. base64.binascii.Error"
        ruleInformationList.append(errorDict)
    except Exception as exception:
        print(traceback.format_exc(),flush=True)
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)
    
def getUTCTimeFromInputDate(dateString):
    try:
        dateGetTimeZoneNonExtracted = dateString.split(":")[-1]
        DateexactTimeZone = dateGetTimeZoneNonExtracted[3:-4]
        startdatewithouttimezone = dateString.replace(DateexactTimeZone,"")
        datetime_obj = datetime.strptime(startdatewithouttimezone, "%a %b %d %H:%M:%S %Y")
        timezoneValues = {
            "IST":"Asia/Kolkata",
            "EDT":"America/New_York"
        }
        if(DateexactTimeZone[:-1] in timezoneValues):
            dynamicTZ = pytz.timezone(timezoneValues[DateexactTimeZone[:-1]])
            dynamicTime = dynamicTZ.localize(datetime_obj)
            utc_time = dynamicTime.astimezone(pytz.utc)
            return utc_time
        else:
            raise Exception("TimeZone not configured")
    except Exception as e:
        print(traceback.format_exc())
        raise Exception

    
def validateToken(transDict,token,privilegeName,ruleInformationList):
    try:
        if(token != None and token !=""):
            tokenSplitted = token.split("[")
            extractedData = []
            extractedDataPrivileges = []
            for split in tokenSplitted:
                if("]" in split):
                    extractedData.append(split.split("]")[0])
            privilegeTokenSplitted = token.split("{")
            for splitPrivileges in privilegeTokenSplitted:
                if("}" in splitPrivileges):
                    extractedDataPrivileges.append(splitPrivileges.split("}")[0])
            if(privilegeName not in extractedDataPrivileges):
                errorDict = {}
                errorDict['Error'] = "Privilege not found in the token"
                ruleInformationList.append(errorDict)
            else:
                if(transDict['ownerId'] != extractedData[0]):
                    errorDict = {}
                    errorDict['Error'] = "ownerId Does Not Match in the token"
                    ruleInformationList.append(errorDict)
                else:
                    if(transDict['sessionUser'] != extractedData[2]):
                        errorDict = {}
                        errorDict['Error'] = "sessionUser does not match in the token"
                        ruleInformationList.append(errorDict)
                    else:
                        startTime = extractedData[4]
                        startTimeOBJ = getUTCTimeFromInputDate(startTime)
                        endTime = extractedData[5]
                        endTimeOBJ = getUTCTimeFromInputDate(endTime)
                        currentTime_utc = datetime.now().astimezone(pytz.utc)
                        if(currentTime_utc < startTimeOBJ or currentTime_utc > endTimeOBJ):
                            errorDict = {}
                            errorDict['Error'] = "Token Expired"
                            ruleInformationList.append(errorDict)
        return ruleInformationList
    except Exception as exception:
        print(traceback.format_exc(),flush=True)
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)
        return ruleInformationList


def validateHeaders(rheaders, requestJson, ruleInformationList):
    try:
        # header validation
        headerData = rheaders
        if (headerData.get("Token","") == ""):
            errorDict = {}
            errorDict['Error'] = "Token is not found or Empty in Header Data"
            ruleInformationList.append(errorDict)
            return ruleInformationList
        
        # input data validation  
        required_inputs = ["ownerId",  "customerName", "customerType",  "sessionUser", "datetime",  "lob", "transdb",  "uiux",  "wf",  "rating",  "reportingdb"]
        for rinput in required_inputs:
            # print(rinput)
            if(requestJson.get(rinput,"") == ""):
                print("{} is not found in input".format(rinput))
                errorDict = {}
                errorDict['Error'] = "{} is not found in input".format(rinput)
                ruleInformationList.append(errorDict)
                return ruleInformationList
            
    except Exception as exception:
        print(traceback.format_exc(),flush=True)
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)
        return ruleInformationList
    

