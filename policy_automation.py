#!/usr/bin/env python

from __future__ import print_function
from builtins import str
from builtins import input
import sys
import csv
import re
import argparse
import json
import pprint
import collections
try:
    import requests
except ImportError as e:
    print("It appears that you do not have the required Python module 'requests' installed.")
    print("Try running the following command to install 'requests'")
    print("    sudo pip install requests --upgrade")
    sys.exit(0)

import components as pc
import functions as functs

pp = pprint.PrettyPrinter(indent=4)
session = requests.Session()

def make_request_headers(place,host=None,user=None,password=None,inniesession = session):
    
    print("Validating credentials...")
    referer = host + '/ui'
    request_headers = { 'Host': host, 'Origin': host, 'Referer': referer }
    request_headers['X-CSRF-Token'] = functs.login(inniesession, user, password, host, request_headers)
    
    return host, request_headers
   