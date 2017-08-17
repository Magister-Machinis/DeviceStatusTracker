#!/usr/bin/env python

from __future__ import print_function
from builtins import str
from builtins import input
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
import sys
import itertools
import csv
import re
import argparse
import json
import pprint
import smtplib
import os

try:
    import requests
except ImportError as e:
    print("It appears that you do not have the required Python module 'requests' installed.")
    print("Try running the following command to install 'requests'")
    print("    sudo pip install requests --upgrade")
    sys.exit(0)


import functions as functs

pp = pprint.PrettyPrinter(indent=4)
session = requests.Session()

def make_request_headers(place,host=None,user=None,password=None,inniesession = session):
    
    print("Validating credentials...")
    referer = host + '/ui'
    request_headers = { 'Host': host, 'Origin': host, 'Referer': referer }
    request_headers['X-CSRF-Token'] = functs.login(inniesession, user, password, host, request_headers)
    
    return host, request_headers

#loads in then compares both lists to find which devices are new, absent, or continuing
def listcompare(clientfolder, oldlist, newlist, DEBUG):
    olderlist = None
    newerlist = None
    devicepresence= {}
    #open old and new lists for comparison
    statuslist = "devicestatus.csv"
    with open(os.path.join(clientfolder,oldlist),"r") as oldcsv:
        olderlist = csv.reader(oldcsv)
        with open(os.path.join(clientfolder,newlist), "r") as newcsv:
            newerlist = csv.reader(newcsv)
            next(newerlist)
            next(olderlist)
            #extract device names from the two lists, deduplicate, and create a dictionary listing their status
            for rowo, rowo in itertools.zip_longest(newerlist, olderlist):
                try:
                    print("new list item is" + rowo[0])
                    if rowo[0] in devicepresence:
                        devicepresence[rowo[0]] = "present"
                    else:
                        devicepresence[rowo[0]] = "new"
                    print("device " +rowo[0]+" is "+devicepresence[rowo[0]])
                except:
                    print("new list empty")
                try:
                    if rowo[0].lower() != "name":
                        print("old list item is" + rowo[0])
                        if rowo[0] in devicepresence:
                            devicepresence[rowo[0]] = "present"
                        else:
                            devicepresence[rowo[0]] = "absent"
                        print("device " +rowo[0]+" is "+devicepresence[rowo[0]])
                except:
                    print("old list is empty")
            
            with open(os.path.join(clientfolder,statuslist),"w") as statlist:
                statlist.write("Devicename,Status\n")
                for k in devicepresence:
                    temp = k + "," + devicepresence[k] + "\n"
                    statlist.write(temp)
    #generating lists of new, absent, and present devices
    olderlist = None
    newerlist = None
    newdeviceslist = "NewDevices.csv"
    absentdeviceslist = "AbsentDevices.csv"
    currentdeviceslist = "Devicelist.csv"
    with open(os.path.join(clientfolder,oldlist),"r") as oldcsv:
        olderlist = csv.reader(oldcsv)
        with open(os.path.join(clientfolder,newlist), "r") as newcsv:
            newerlist = csv.reader(newcsv)
            
            with open(os.path.join(clientfolder,newdeviceslist),"w") as newdevices:
                newdevices.write("Devicename,Username,Registered Date,Last Contact,Last Internal Ip Address,Last External Ip Address,Device Type,Policy,OS,Sensor Version\n")
                print("initialized new device list")
                with open(os.path.join(clientfolder,absentdeviceslist),"w") as absentdevices:
                    absentdevices.write("Devicename,Username,Registered Date,Last Contact,Last Internal Ip Address,Last External Ip Address,Device Type,Policy,OS,Sensor Version\n")
                    print("initialized absent device list")
                    with open(os.path.join(clientfolder,currentdeviceslist),"w") as currentdevices:
                        currentdevices.write("Devicename,Username,Registered Date,Last Contact,Last Internal Ip Address,Last External Ip Address,Device Type,Policy,OS,Sensor Version\n")
                        print("initialized current device list")
                        next(newerlist)
                        next(olderlist)
                        for rowo, rowo in itertools.zip_longest(newerlist, olderlist):
                            try:
                                if DEBUG == True:
                                    print(rowo)
                                if devicepresence[rowo[0]] == "present":
                                    temp = str(rowo[0]+","+rowo[1]+","+rowo[7]+","+rowo[9]+","+rowo[10]+","+rowo[12]+","+rowo[13]+","+rowo[14]+","+rowo[16]+","+rowo[17]+"\n")
                                    print("sorting device: "+rowo[0]+" into present list")
                                    if DEBUG == True: 
                                        print(temp)
                                    currentdevices.write(temp)
                                    temp = None
                                elif devicepresence[rowo[0]] == "new":
                                    temp = str(rowo[0]+","+rowo[1]+","+rowo[7]+","+rowo[9]+","+rowo[10]+","+rowo[12]+","+rowo[13]+","+rowo[14]+","+rowo[16]+","+rowo[17]+"\n")
                                    print("sorting device: "+rowo[0]+" into new list")
                                    if DEBUG == True: 
                                        print(temp)
                                    newdevices.write(temp)
                                    temp = None
                            except:
                                if DEBUG == True:
                                    print("new list is empty")
                                else:
                                    pass
                            try:
                                if devicepresence[rowo[0]] == "absent":
                                    temp = str(rowo[0]+","+rowo[1]+","+rowo[7]+","+rowo[9]+","+rowo[10]+","+rowo[12]+","+rowo[13]+","+rowo[14]+","+rowo[16]+","+rowo[17]+"\n")
                                    print("sorting device: "+rowo[0]+" into new list")
                                    if DEBUG == True: 
                                        print(temp)
                                    absentdevices.write(temp)
                                    temp = None
                            except:
                                if DEBUG == True:
                                    print("old list is empty")
                                else:
                                    pass
        return os.path.join(clientfolder,newdeviceslist),os.path.join(clientfolder,currentdeviceslist),os.path.join(clientfolder,absentdeviceslist),os.path.join(clientfolder,statuslist)
  
#crafts and sends email
def mailinate(row,newdevicelist,currentdevicelist,absentdevicelist,statuslist):
    listoflists = newdevicelist,currentdevicelist,absentdevicelist,statuslist
    sendto = row[2] + ";Cybersupport@blueteamglobal.com; jfromholtz@hotmail.com"
   
    with open(os.path.abspath("./emailbody.txt"),'r') as bodytext:
        msgbody = MIMEText(bodytext.read())
        msgbody['From'] = "CyberSupport@blueteamglobal.com"
        msgbody['To'] = ",".join(sendto)
        msgbody['Subject'] = "Weekly Enrollment Status Report"
    msg['Date'] = formatdate(localtime=True)
    msg = MIMEMultipart()
    
    msg.preamble = "If this text is visible in an email there has been an error in the presentation of the message. Please contact your engagement lead."
    
    for item in listoflists:
        print("Attaching list %s" % item)
        component = MIMEBase('application', 'octet-stream')
        with open(item, 'rb') as filein:
            component.set_payload(filein.read())
            component.add_header('Content-Disposition', "attachment; filename= %s" % item)
            msg.attach(component)
    msg.attach(msgbody)
    s = smtplib.SMTP('localhost')
    s.sendmail("CyberSupport@blueteamglobal.com",sendto,(msgbody.as_string()))
    s.quit()