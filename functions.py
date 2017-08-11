#!/usr/bin/python
from __future__ import print_function
from builtins import input
from builtins import str
from past.builtins import basestring
import sys
import time
import re
import json
import requests
import getpass
import requests.packages.urllib3
import components as pc
import time

requests.packages.urllib3.disable_warnings()
session = requests.Session()


def prettyPrint(entry):
    print(json.dumps(entry, indent=4, sort_keys=True))

def check_request_version():
    req_ver = requests.__version__
    if req_ver < '2.14.2':
        print("WARNING: Your version of the Python module 'requests' is not the most up-to-date.\n\
If you have errors related to 'requests' upgrade to the latest version using:\n\t\
sudo pip install requests --upgrade")
        input("Press 'Enter' to continue")

def data_validation_error(input_string, field_numb):
    print("CSV contains invalid data in field %i (printed below).  Fix data and try again." % (field_numb))
    print(input_string)
    sys.exit(1)

def app_match(input_string):
    for k in list(pc.applications.keys()):
        if input_string.upper().startswith(k.upper()):
            return (pc.applications[k]['type'], pc.applications[k]['value'])
    #if we get to here, the 1st field on a line does not match our rule types.
    data_validation_error(input_string, 1)

def op_match(input_string):
    for k in list(pc.operations.keys()):
        if input_string.upper().startswith(k.upper()):
            return (pc.operations[k])
    #if we got to here, the 2nd field on a line does not match our rule operations.
    data_validation_error(input_string, 2)

def action_match(input_string):
    for k in list(pc.actions.keys()):
        if input_string.upper().startswith(k.upper()):
            return (pc.actions[k])
    #if we got to here, the 3rd field on a line does not match our rule actions.
    data_validation_error(input_string, 3)

def list_servers():
    cntr = 0
    for k in pc.defense_servers:
        print("%s) %s: %s" % (str(cntr).rjust(2), k.ljust(6), pc.defense_servers[k]))
        cntr +=1

def get_cbd_instance(src_or_dst):
    list_servers()
    host_raw = input("****%s**** server.\nPlease choose a number from list of available Cb Defense Servers: " % (src_or_dst))
    try:
        host_int = int(host_raw) 
    except:
        print("Expected an integer input.  Re-run the tool and input an integer.")
        sys.exit()
    
    if host_int >= (len(pc.defense_servers)-1):
        host = input("Please enter the ****%s**** CbD console URL\n(example: https://host.conferdeploy.net/): " % (src_or_dst))
    else:
        host = list(pc.defense_servers.values())[host_int]
        print("%s Server: %s" % (src_or_dst, host))
    
    if len(host) == 0:
        print("No Cb Defense server specified.  Please rerun the tool and specify a CbD instance.")
        sys.exit(1)

    if host.startswith('http://'):
        host = re.sub('http://', 'https://', host)

    if not host.startswith('https://'):
        host = 'https://' + host
    return host

def get_username_password(src_or_dst):
    uname = input("%s Username: " % (src_or_dst))
    if not uname:
        print("Error: Username cannot be blank. Rerun the tool.")
        sys.exit(1)
    pword = getpass.getpass("%s Password: " % (src_or_dst))
    if not pword:
        print("Error: Password cannot be blank. Rerun the tool.")
        sys.exit(1)
    return uname, pword

def get_policy_name(infile):
    if isinstance(infile, basestring):
        ppn = infile.split('.',1)[0]
        print("DESTINATION Policy Name: %s" % (ppn))
        pol_name = input("Type your New Policy Name or just press 'Enter' to use '%s': " % (ppn))
        if not pol_name:
            pol_name = ppn
    else:
        pol_name = input("DESTINATION Policy Name: ")
        if not pol_name:
            print("ERROR:  DESTINATION policy name cannot be blank.  Rerun the tool and provide a name.")
            sys.exit(1)
    
    return pol_name

def get_policy_description():
    pol_desc = input("DESTINATION Policy Description: ")
    return pol_desc

def get_policy_priority():
    valid_pol_pris = ['LOW', 'MEDIUM', 'HIGH', 'MISSION_CRITICAL']
    pol_pri = input("DESTINATION Policy Target Value: LOW MEDIUM HIGH MISSION_CRITICAL: [MEDIUM] ")
    if len(pol_pri) == 0:
        pol_pri = "MEDIUM"
    if pol_pri in valid_pol_pris:
        return pol_pri
    else:
        print("Error:  %s is an invalid Policy Priority.  Valid Policy Priorities are:")
        for i in valid_pol_pris:
            print(i)
        sys.exit(1)

def get_policy_priority_level():
    #Nobody seems to know what this variable maps to
    #  Until we figure it out, I'm just hard setting it to 3
    #  If anybody ever says anything, just uncomment the next 3 lines
    #  And delete the on just below them.
    #ppl = raw_input("Policy Priority Level: [3] ")
    #if len(ppl) == 0:
    #    ppl = 3
    ppl = 3
    return ppl
    

def login(session, user, password, host, request_headers):
    #request_headers = build_request_headers(host)
    formdata = {'forward': '', 'email': user, 'password': password}
    
    url = host + '/checkAuthStrategy'
    response = session.post(url, data=formdata, headers=request_headers, timeout=30)
    
    url = host + '/userInfo'
    response = session.get(url, data=formdata, headers=request_headers, timeout=30)
    
    if 'csrf' in response.json() and response.json()['csrf'] is not None:
        csrf = json.dumps(response.json()['csrf']).replace('"', '')
        return csrf
    else:
        print('Error: Authentication failed. The username/password combination is not valid for %s' % (host))
        sys.exit(1)


def web_get(session, host, uri, request_headers):
    try:
        url = host + uri
        response = session.get(url, headers=request_headers, timeout=30)
    except Exception as e:
        print("GET request failed for the following URI: %s" % (uri))
        print("Exception: %s" % (e))
        sys.exit(1)
    try:
        return response.json()
    except Exception as e:
        pass
        
def web_get_ALL(session, host, uri, request_headers):
    counter = 1
    while counter > 0:
        try:
            url = host + uri
            response = session.get(url, headers=request_headers, timeout=(counter*15))
            counter = 0
        except Exception as e:
            counter += 1
            print("GET request failed for the following URI: %s" % (uri))
            print("Exception: %s" % (e))
            if counter > 4:
                print("Multiple GET attempts failed, aborting process")
                sys.exit(1)
    try:
        return response
    except Exception as e:
        pass

        
def web_post(session, host, uri, request_headers, formdata):
    statustest = True
    count = 1
    while statustest == True:
        try:
            url = host + uri
            response = session.post(url, json=formdata, headers=request_headers, timeout=30)
        except Exception as e:
            print("POST request failed for the following URI: %s" % (uri))
            print("Exception: %s" % (e))
            sys.exit(1)
        print("URL = " + url + "\nStatus = " + str(response.status_code))
        if str(response.status_code) != "200":
            statustest = True
            print("POST attempt failed with message: " + str(response.status_code) + " attempting again in " + str(5*count) +" seconds")
            time.sleep(5 * count)
            count += 1
        else:
            statustest = False
        
    try:
        return response.json()
    except Exception as e:
        print("Exception: %s" % (e))
        

def does_policy_exist(jsonResponse):
    if jsonResponse['groupAlreadyExists'] is True:
        print("ERROR: A policy with this name already exists.")
        print("Re-run the import and create a policy with a new name.")
        sys.exit(1)

