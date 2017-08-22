import policy_automation as policy
import argparse
import csv
import os
import requests
import itertools
import smtplib
#functional bit, checks if folder/files for this client exist, retrieves new list from console, compares to old list, then generates message showing new list of devices, what devices are new, and what devices are no longer present
def devicestatus(row, user, password, directory,DEBUG,emailbody):
    internalsession = requests.Session()
    username = user + row[0]
    host = row[1]
    host, request_headers = policy.make_request_headers("DESTINATION",host,username,password,internalsession)
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
        newlist,presentlist,absentlist,liststatus = policy.listcompare(clientfolder, clientlist, clientnewlist,DEBUG)
        policy.mailinate(row,newlist,presentlist,absentlist,liststatus,emailbody)
        if DEBUG == True:
            print("new list at " + newlist)
            print("current list at " + presentlist)
            print("absent list at " + absentlist)
    else:
        print("No previous file detected, using new list")
        with open(os.path.join(clientfolder,clientlist), "wb") as newclient:
            newclient.write(newlist.content)
        devicestatus(row, user, password, directory,DEBUG,emailbody)

      
#reads in config file and calls processing function for each client line, can alternatively run each line in parallel
def main():
    #little tidbit to locate emailbody.txt file
    generalpath = os.path.dirname(args.config)
    emailbodylocation = os.path.join(generalpath,"./emailbody.txt")
    with open(args.config, 'r') as configfile:
        config = csv.reader(configfile)
        listofthreads = []
        next(config)
        for row in config:
            if THREADS == True:
                t = mp.Process(target= devicestatus, args = (row, user, password, os.path.abspath(args.directory),DEBUG,os.path.abspath(emailbodylocation)))
                t.start()
                listofthreads.append(t)
            else:
                devicestatus(row, user, password, os.path.abspath(args.directory),DEBUG,os.path.abspath(emailbodylocation))
        for item in listofthreads:
            item.join()

def get_name_pw():
    uname = input("Input username without client code or @blueteamglobal.com: ")
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
            print("Parallel job handling enabled, kiss your bandwidth goodbye")
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
