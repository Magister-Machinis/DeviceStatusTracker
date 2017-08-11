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

def make_request_headers(place,host=None,user=None,password=None,MINE=False,inniesession = session):
    if MINE == False:
        host = functs.get_cbd_instance(place)
        user, password = functs.get_username_password(place)
    print("Validating credentials...")
    referer = host + '/ui'
    request_headers = { 'Host': host, 'Origin': host, 'Referer': referer }
    request_headers['X-CSRF-Token'] = functs.login(inniesession, user, password, host, request_headers)
    
    return host, request_headers
   

def apply_changes(host, request_headers, policyDescription, groupId, policyName, jsonPolicy, priorityLevel, infile):
    formdata = {"id": groupId,
                "origname": policyName,
                "name": policyName,
                "origdescription": policyDescription,
                "description": policyDescription,
                "priorityLevel": priorityLevel,
                "origpriorityLevel": priorityLevel,
                "adminVersion": False,
                "policy": jsonPolicy}

    if infile:
        with open (infile, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                rule_id = jsonPolicy['maxRuleId'] + 1
                rule = {'required': 'false', 'id': rule_id}
            
                app_dict = {}
                app_dict['type'], app_dict['value'] = functs.app_match(row[0])
                if not app_dict['value']:
                    adv = row[0].split(': ')[1]
                    adv = re.sub('"', '', adv)
                    app_dict['value'] = adv
                
                rule['application'] = app_dict.copy()
                rule['operation'] = functs.op_match(row[1])
                if rule['operation'] == 'BYPASS_ALL':
                    #force the action to be IGNORE
                    rule['action'] = 'IGNORE'
                else:
                    #otherwise follow the CSV
                    rule['action'] = functs.action_match(row[2])
                
                formdata['policy']['rules'].append(rule.copy())
                formdata['policy']['maxRuleId'] = rule_id
    
    print("Inserting configuration and rules into policy id:  %i" % (groupId))

    uri = '/settings/groups/modify'
    functs.web_post(session, host, uri, request_headers, formdata)
    
    print("Policy Import completed. Logging out.")
    uri = '/logout'
    functs.web_get(session, host, uri, request_headers)


def import_policy(infile, intype, host, request_headers):
    policyName = functs.get_policy_name(infile)
    policyDescription = functs.get_policy_description()
    priorityLevel = functs.get_policy_priority()
    policyPriorityLevel = functs.get_policy_priority_level()
    
    formdata = {"name": policyName,
                "description": policyDescription,
                "priorityLevel": priorityLevel,
                "priority": int(policyPriorityLevel),
                "sourceGroupId": None}

    print("Creating Policy: %s" % (policyName))
    uri = '/settings/groups/add'
    response = functs.web_post(session, host, uri, request_headers, formdata)

    functs.does_policy_exist(response)

    groupId = response['addedDeviceGroupId']

    if intype == 'from_csv':
        jsonPolicy = pc.policy_template.copy()
    
    elif intype == 'from_json_memory':
        jsonPolicy = infile
        infile = ''
    
    elif intype == 'from_json_file':
        with open(infile, 'r') as f:
            jsonPolicy = json.load(f)
        infile = ''
    else:
        print("Error:  Import Policy called for an unsupported format.")
        sys.exit(1)
    
    apply_changes(host, request_headers, policyDescription, groupId, policyName, jsonPolicy, priorityLevel, infile)

def import_certs(infile, host, request_headers):
    uri = '/settings/hashentry/add'
    with open (infile, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            cert_dict = {}
            cert_dict['description'] = row[3]
            cert_dict['hashListType'] = "WHITE_LIST"
            cert_dict['reputationOverrideType'] = "CERT"
            cert_dict['value1'] = row[2]
            try:
                cert_dict['value2'] = row[4]
            except:
                cert_dict['value2'] = ''
            print("Adding Certificate: %s" % (cert_dict['description']))
            response = functs.web_post(session, host, uri, request_headers, cert_dict)
    
    print("Certificate Import completed. Logging out.")
    uri = '/logout'
    functs.web_get(session, host, uri, request_headers)                  

def import_blhash(infile, host, request_headers):
    uri = '/settings/hashentry/add'
    with open (infile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            hash_dict = {}
            hash_dict['description'] = row[4]
            hash_dict['hashListType'] = row[0]
            hash_dict['reputationOverrideType'] = "SHA256"
            hash_dict['value1'] = row[2]
            if row[3]:
                hash_dict['value2'] = row[3]
            else:
                hash_dict['value2'] = ''
            print("Adding SHA256: %s" % (hash_dict['value1']))
            response = functs.web_post(session, host, uri, request_headers, hash_dict)
    
    print("Black list Hash Import completed. Logging out.")
    uri = '/logout'
    functs.web_get(session, host, uri, request_headers)

def export_policy(exp_type, host, request_headers):
    uri = '/settings/groups/list'
    response = functs.web_get(session, host, uri, request_headers)
    
    if response['success']:
        # creating a list of the policies from the target org
        menu_number = 0
        policies = collections.OrderedDict()
        pol_names = []

        for entry in response['entries']:
            policies[entry['name']] = {'orgId': entry['orgId'], 'id': entry['id']}
            pol_names.append(entry['name'])
        
        print("Policies Available for Export:")
        for key in list(policies.keys()):
            print('%i) %s' % (menu_number, key))
            menu_number += 1
    
        pol_id = int(input("Choose the number for your SOURCE Policy: "))
        if pol_id < menu_number:
            pol_name = pol_names[int(pol_id)]
            print("SOURCE Policy Name: %s" % (pol_name))
            groupId = policies[pol_name]['id']
            print('SOURCE Policy ID: %i' % (groupId))
        else:
            print("Invalid SOURCE Policy choice received.  Rerun the script and retry.")
            sys.exit(1)
    
    uri = '/settings/policy/%i/details' % (groupId)
    response = functs.web_get(session, host, uri, request_headers)
    
    if response['success']:
        jsonResponse = json.dumps(response['policy'], indent=4, sort_keys=True)
        if exp_type == 'to_json_file':
            if not args.output:
                print("No Output File Specified.")
                outfile = input("Specify output filename or just press 'Enter' to output to '%s.json': " % (pol_name))
                if outfile == '':
                    outfile = pol_name + '.json'
            else:
                outfile = args.output
            with open(outfile, 'w') as outf:
                outf.write(jsonResponse)
        elif exp_type == 'to_json_memory':
            policyDescription = response['description']
            groupId = response['id']
            policyName = response['name']
            jsonPolicy = response['policy']
            priorityLevel = response['priorityLevel']
            return policyDescription, groupId, policyName, jsonPolicy, priorityLevel
        else:
            print("Export type not specified.  No data exported.")

def edit_policy(policyDescription, groupId, policyName, jsonPolicy, priorityLevel, infile, host, request_headers):

    #write original policy for safety's sake
    fo_name = "%s_orig.json" % (str(groupId))
    with open(fo_name, 'w') as fo:
        json.dump(jsonPolicy, fo, indent=4, sort_keys=True)
    
    apply_changes(host, request_headers, policyDescription, groupId, policyName, jsonPolicy, priorityLevel, infile)


def main():
    functs.check_request_version()
    
    if args.action == 'export_json':
        print("\n##### Begin Policy Export #####")
        host, request_headers = make_request_headers('SOURCE')
        export_policy('to_json_file', host, request_headers)
        
    elif args.action == 'import_csv':
        if not args.input:
            args.input = input("No Input file specified.\nWhat CSV file contains the rules to import?: ")
        print("Using %s as rule source" % (args.input))
        print("\n##### Begin Policy Import #####")
        host, request_headers = make_request_headers('DESTINATION')
        import_policy(args.input, 'from_csv', host, request_headers)
    
    elif args.action == 'import_json':
        if not args.input:
            args.input = input("No Input file specified.\nWhat JSON file contains the policy to import?: ")
        print("Using %s as rule source" % (args.input))
        print("\n##### Begin Policy Import #####")
        host, request_headers = make_request_headers('DESTINATION')
        import_policy(args.input, 'from_json_file', host, request_headers)

    elif args.action == 'import_certs':
        if not args.input:
            args.input = input("No Input file specified.\nWhat CSV file contains the certs to import?: ")
        print("Using %s as cert source" % (args.input))
        print("\n##### Begin Certificate Import #####")
        host, request_headers = make_request_headers('DESTINATION')
        import_certs(args.input, host, request_headers)
    
    elif args.action == 'import_blhash':
        if not args.input:
            args.input = input("No Input file specified.\nWhat CSV file contains the certs to import?: ")
        print("Using %s as cert source" % (args.input))
        print("\n##### Begin SHA256 Black List Hash Import #####")
        host, request_headers = make_request_headers('DESTINATION')
        import_blhash(args.input, host, request_headers)
    
    elif args.action == 'transfer':
        print("\n##### Begin Policy Export #####")
        host, request_headers = make_request_headers('SOURCE')
        policyDescription, groupId, policyName, jsonPolicy, priorityLevel = export_policy('to_json_memory', host, request_headers)
        #jsonPolicy is the only variable used for transfer, but define all because edit_policy needs them
        
        print("\n##### Begin Policy Import #####")
        host, request_headers = make_request_headers('DESTINATION')
        import_policy(jsonPolicy, 'from_json_memory', host, request_headers)
    
    elif args.action == 'edit_policy':
        if not args.input:
            args.input = input("No Input file specified.\nWhat CSV file contains the rules to import?: ")
        print("Using %s as rule source" % (args.input))
        infile = args.input

        host, request_headers = make_request_headers('DESTINATION')
        policyDescription, groupId, policyName, jsonPolicy, priorityLevel = export_policy('to_json_memory', host, request_headers)
        print("\n##### Begin Policy Edit #####")
        edit_policy(policyDescription, groupId, policyName, jsonPolicy, priorityLevel, infile, host, request_headers)

    else:
        print("Error: action was not one of 'export_json/import_csv/import_json/transfer/import_cert'.")
        print("Please rerun the script providing a correct action argument")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", help="Action to be taken.  Valid values: import_csv,import_json,export_json,transfer,import_certs, import_blhash, edit_policy", required=True)
    parser.add_argument("-i", "--input", help="File containing rules or policy to import.")
    parser.add_argument("-o", "--output", help="File to which to write policy JSON. Just in case you wish to verify the JSON.")
    args = parser.parse_args()
    
    main()


#Tests we should run:
#    export_json
#        with -o
#        without -o
#            accept pol name as outfile
#            not accept pol name as outfile
#    import_csv
#        with -i
#            accept filename as pol name
#            not accept filename as pol name
#        without -i
#            accept filename as pol name
#            not accept filename as pol name
#    import_json
#        with -i
#            accept filename as pol name
#            not accept filename as pol name
#        without -i
#            accept filename as pol name
#            not accept filename as pol name
#    import_certs
#        with -i
#        without -i
#    transfer
#        same server
#            same org
#                keep dst pol name same: should fail
#                change dst pol name
#            diff org
#                keep dst pol name same
#                change dst pol name
#        diff servers
#            keep dst pol name same
#            change dst pol name
#    edit_policy
#        with -i
#        without -i
