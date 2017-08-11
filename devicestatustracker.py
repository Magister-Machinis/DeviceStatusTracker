import policy_automation as policy
import argparse
import csv
import os
import requests
import itertools
import smtplib
#functional bit, checks if folder/files for this client exist, retrieves new list from console, compares to old list, then generates message showing new list of devices, what devices are new, and what devices are no longer present
def devicestatus(row, user, password, directory,DEBUG):
    internalsession = requests.Session()
    username = user + row[0]
    host = row[1]
    host, request_headers = policy.make_request_headers("DESTINATION",host,username,password, True, internalsession)
    clientcode = ((row[0]).split("@")[0])
    print("beginning work on "+clientcode)
    clientfolder = os.path.join(directory, clientcode)
    clientlist = clientcode + "current.csv"
    clientnewlist = clientcode + "new.csv"
    uri = "/settings/users/download/list?fromRow=1&maxRow=20&version=1&fieldName=TIME&sortOrder=DESC&deviceStatus=ACTIVE"
    os.makedirs(clientfolder, exist_ok=True)
    newlist = policy.functs.web_get_ALL(internalsession, host, uri, request_headers)
    print("download of "+clientcode+" list complete")
    if os.path.isfile(os.path.join(clientfolder,clientlist)):
        print("comparison file detected, calculating")
        with open(os.path.join(clientfolder,clientnewlist), "wb") as newclient:
            newclient.write(newlist.content)
        print("beginning list comparison")
        newlist,presentlist,absentlist = listcompare(clientfolder, clientlist, clientnewlist,DEBUG)
        if DEBUG == True:
            print("new list at " + newlist)
            print("current list at " + presentlist)
            print("absent list at " + absentlist)
    else:
        print("No previous file detected, using new list")
        with open(os.path.join(clientfolder,clientlist), "wb") as newclient:
            newclient.write(newlist.content)
        devicestatus(row, user, password, directory,DEBUG)
#loads in then compares both lists to find which devices are new, absent, or continuing
def listcompare(clientfolder, oldlist, newlist, DEBUG):
    olderlist = None
    newerlist = None
    devicepresence= {}
    #open old and new lists for comparison
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
            textfile = "devicestatus.csv"
            with open(os.path.join(clientfolder,textfile),"w") as statlist:
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
        return os.path.join(clientfolder,newdeviceslist),os.path.join(clientfolder,currentdeviceslist),os.path.join(clientfolder,absentdeviceslist)
        
#reads in config file and calls processing function for each client line, can alternatively run each line in parallel
def main():
    with open(args.config, 'r') as configfile:
        config = csv.reader(configfile)
        listofthreads = []
        next(config)
        for row in config:
            if THREADS == True:
                t = mp.Process(target= devicestatus, args = (row, user, password, os.path.abspath(args.directory),DEBUG))
                t.start()
                listofthreads.append(t)
            else:
                devicestatus(row, user, password, os.path.abspath(args.directory),DEBUG)
        for item in listofthreads:
            item.join()

def get_name_pw():
    uname = input("Input username without client code or @k2intelligence.com: ")
    pword = getpass.getpass("Input password to be used: ")
    if not pword:
        print("Error: Password cannot be blank. Rerun the tool.")
        sys.exit(1)
    return uname, pword

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config", help = "location of config file", required=True)
    parser.add_argument("-d", "--directory", help = "directory for storage of lists ", required=True)
    parser.add_argument("-cred", "--credentials", help = "input credentials in cmdline as form [USERNAME],[PASSWORD]")
    parser.add_argument("-v","--verbose", help = "set to True for verbose output flag for debug, defaults to False")
    parser.add_argument("-mp","--multiprocessed", help = "set to True to run uploads in parallel rather than sequentially, may be unstable")
    args = parser.parse_args()
    if args.verbose is not None:
        DEBUG = True
        print("config at "+ args.config)
        print("target directory is " + args.directory)
    else:
        DEBUG = False
    if args.multiprocessed is not None:
        if(DEBUG == True):
            print("Parallel uploading enabled, kiss your bandwidth goodbye")
        import multiprocessing as mp
        THREADS = True
    else:
        THREADS = False
    if args.credentials == None:
        import getpass
        user, password = get_name_pw()
    else:
        user = (args.credentials.split(","))[0]
        password = (args.credentials.split(","))[1]
    main()