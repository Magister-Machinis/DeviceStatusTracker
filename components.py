import collections

defense_servers = collections.OrderedDict()
defense_servers['prod'] = 'https://dashboard.confer.net/'
defense_servers['prod02'] = 'https://defense.conferdeploy.net/'
defense_servers['prod05'] = 'https://defense-prod05.conferdeploy.net/'
defense_servers['prod06'] = 'https://defense-eu.conferdeploy.net/'
defense_servers['eap'] = 'https://defense-eap01.conferdeploy.net/'
defense_servers['other'] = 'Any Server Not Listed. Will require manual URL entry.'

applications = {
    'When known malware that has a verified signature': {'type': 'REPUTATION', 'value': 'KNOWN_MALWARE'},
    'When applications that appear on the company blacklist': {'type': 'REPUTATION', 'value': 'COMPANY_BLACK_LIST'},
    'When suspected malware': {'type': 'REPUTATION', 'value': 'SUSPECT_MALWARE'},
    'When adware or a potentially unwanted program': {'type': 'REPUTATION', 'value': 'PUP'},
    'When an unknown application': {'type': 'REPUTATION', 'value': 'RESOLVING'},
    'When a not listed application': {'type': 'REPUTATION', 'value': 'ADAPTIVE_WHITE_LIST'},
    'When an application at path': {'type': 'NAME_PATH', 'value': ''}
}

operations = {
    'Tries to communicate over the network': 'NETWORK',
    'Tries to execute code from memory': 'RUN_INMEMORY_CODE',
    'Tries to inject code or modify memory of another process': 'CODE_INJECTION',
    'Tries to invoke an untrusted application': 'POL_INVOKE_NOT_TRUSTED',
    'Tries to run or is running': 'RUN',
    'Tries to scrape memory of another process': 'MEMORY_SCRAPE',
	'Tries to perform any operations': 'BYPASS_ALL'
}

actions = {
    'Terminate process': 'TERMINATE',
    'Deny': 'DENY',
    'Allow': 'ALLOW',
    'Ignore': 'IGNORE'
}

policy_template = {
    "avSettings": {
        "features": [
            {
                "enabled": "true", 
                "name": "SIGNATURE_UPDATE"
            }, 
            {
                "enabled": "true", 
                "name": "ONACCESS_SCAN"
            }, 
            {
                "enabled": "true", 
                "name": "ONDEMOND_SCAN"
            }
        ], 
        "onAccessScan": {
            "profile": "NORMAL"
        }, 
        "onDemandScan": {
            "profile": "NORMAL", 
            "scanCdDvd": "AUTOSCAN", 
            "scanUsb": "AUTOSCAN", 
            "schedule": {
                "days": None, 
                "rangeHours": 0, 
                "recoveryScanIfMissed": "true", 
                "startHour": 0
            }
        }, 
        "settings": None, 
        "signatureUpdate": {
            "schedule": {
                "fullIntervalHours": 0, 
                "initialRandomDelayHours": 1, 
                "intervalHours": 2
            }
        }, 
        "updateServers": {
            "servers": [
                {
                    "flags": 0, 
                    "regId": None, 
                    "server": [
                        "http://updates.cdc.carbonblack.io/update"
                    ]
                }
            ], 
            "serversForOffSiteDevices": [
                "http://updates.cdc.carbonblack.io/update"
            ], 
            "serversOverride": [], 
            "useServersOverride": "false"
        }
    }, 
    "directoryActionRules": [], 
    "id": -1, 
    "maxRuleId": 0, 
    "mobileSensorSettings": None, 
    "phishingSettings": None, 
    "rules": [], 
    "sensorAutoUpdateEnabled": "true", 
    "sensorSettings": [
        {
            "name": "ALLOW_UNINSTALL", 
            "value": "true"
        }, 
        {
            "name": "ALLOW_UPLOADS", 
            "value": "true"
        }, 
        {
            "name": "SHOW_UI", 
            "value": "true"
        }, 
        {
            "name": "ENABLE_THREAT_SHARING", 
            "value": "true"
        }, 
        {
            "name": "QUARANTINE_DEVICE", 
            "value": "false"
        }, 
        {
            "name": "LOGGING_LEVEL", 
            "value": "NORMAL"
        }, 
        {
            "name": "QUARANTINE_DEVICE_MESSAGE", 
            "value": "Device has been quarantined by your computer administrator."
        }, 
        {
            "name": "SET_SENSOR_MODE", 
            "value": "0"
        }, 
        {
            "name": "SENSOR_RESET", 
            "value": "0"
        }, 
        {
            "name": "BACKGROUND_SCAN", 
            "value": "true"
        }, 
        {
            "name": "POLICY_ACTION_OVERRIDE", 
            "value": "true"
        }, 
        {
            "name": "HELP_MESSAGE", 
            "value": ""
        }, 
        {
            "name": "PRESERVE_SYSTEM_MEMORY_SCAN", 
            "value": "false"
        }, 
        {
            "name": "HASH_MD5", 
            "value": "true"
        }, 
        {
            "name": "SCAN_LARGE_FILE_READ", 
            "value": "false"
        }, 
        {
            "name": "SCAN_EXECUTE_ON_NETWORK_DRIVE", 
            "value": "true"
        }, 
        {
            "name": "DELAY_EXECUTE", 
            "value": "true"
        }, 
        {
            "name": "SCAN_NETWORK_DRIVE", 
            "value": "true"
        }, 
        {
            "name": "BYPASS_AFTER_LOGIN_MINS", 
            "value": "0"
        }, 
        {
            "name": "BYPASS_AFTER_RESTART_MINS", 
            "value": "0"
        }, 
        {
            "name": "SHOW_FULL_UI", 
            "value": "false"
        }
    ], 
    "updateVersion": 0
}

