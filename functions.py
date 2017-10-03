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
    

def login(session, user, password, host, request_headers):
    #request_headers = build_request_headers(host)
    formdata = {'forward': '', 'email': user, 'password': password}
    
    url = host + '/checkAuthStrategy'
    counter = 1
    response = session.post(url, data=formdata, headers=request_headers, timeout=(counter*30))

    
    url = host + '/userInfo'
    while counter > 0:
        try:
            response = session.get(url, data=formdata, headers=request_headers, timeout=(counter*15))
            csrf = json.dumps(response.json()['csrf']).replace('"', '')
            counter = 0
            return csrf
        except Exception as e:
                print("Login GET request failed")
                print("Exception: %s" % (e))
                counter += 1
                time.sleep(counter)
                if counter > 4:
                    print('Error: Authentication failed. The username/password combination is not valid for %s' % (host))
                    sys.exit(1)


def web_get_ALL(session, host, uri, request_headers):
    counter = 1
    while counter > 0:
        try:
            url = host + uri
            response = session.get(url, headers=request_headers, timeout=(counter*15))
            counter = 0
        except Exception as e:
            counter += 1
            print("Web GET request failed for the following URI: %s" % (uri))
            print("Exception: %s" % (e))
            time.sleep(counter)
            if counter > 4:
                print("Multiple GET attempts failed, aborting process")
                sys.exit(1)
    try:
        return response
    except Exception as e:
        pass

