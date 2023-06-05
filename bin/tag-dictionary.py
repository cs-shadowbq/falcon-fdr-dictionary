#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import re

# This script takes a JSON file as input and outputs a JSON file with the tag and name_expanded fields added to each collection
# The script also prints to STDOUT the collections for which no tag was found


# Function to extract the tag from the description and name_expanded
# The function returns a list of tags
# The function uses a dictionary of keywords and their corresponding tags to find likely tags
# The function uses regex to match the keywords in the description and name_expanded


def extract_tag(description):  # sourcery skip: use-fstring-for-formatting
    keywords = {
        'file': ['file', 'files', 'disk', 'rename', 'volume', 'io', 'directory', 'image', 'symbolic link'],
        'pe': ['pe', 'pe32', 'pe64', 'portable executable', 'executable'],
        'process': ['proc', 'pr2', 'process', 'start', 'thread', 'command', 'execute', 'fork', 'execution', 'executed', 'executing', 'named pipe', 'suppressingpr2s'],
        'memory': ['memory', 'allocate', 'free', 'byte', 'amcache', 'cache', 'page', 'pool', 'heap', 'stack', 'virtual', 'physical', 'ram', 'swap', 'address', 'address space', 'addressspace', 'address-space', 'address_space', 'vad', 'vads', 'vadtree', 'vad_tree', 'vad tree', 'vadtree', 'mprotect', 'seh', 'sehchain'],
        'network': ['network', 'connection', 'request', 'bind', 'ip4', 'ip6', 'arp', 'promiscuous', 'remote', 'socket', 'channel', 'bindip4', 'bindip6', 'bindip', 'addressip4', 'addressip6', 'addressip', 'routeip4', 'routeip6', 'routeip', 'listip4', 'packet'],
        'dll': ['dll', 'loaded', 'dylib', 'so', 'module'],
        'hook': ['hook', 'hooked', 'api', 'call', 'function', 'handle'],
        'kernel': ['kernel', 'driver', 'os', 'system', 'nt', 'ntoskrnl', 'ntdll', 'ntos', 'ntoskrnl', 'ntdll'],
        'syscall': ['syscall', 'system call'],
        'time': ['time', 'timestamp', 'date', 'datetime', 'timezone', 'utc', 'gmt', 'localtime', 'local', 'zone', 'entropy'],
        'registry': ['registry', 'key', 'asep', 'reg'],
        'machine': ['hostname', 'host', 'machine', 'computer'],
        'manipulation': ['manipulation', 'zero', 'sign', 'bypass'],
        'authentication': ['authentication', 'login', 'logout', 'logon', 'logoff', 'active directory', 'skeleton'],
        'user': ['user', 'account', 'credential', 'credentials', 'kerberos', 'ntlm', 'password'],
        'group': ['group', 'membership'],
        'audit': ['audit', 'logging', 'tamper', 'ledger', 'etw', 'amsi', 'log', 'error', 'warning', 'critical', 'info', 'debug', 'trace', 'crash'],
        'privilege': ['privilege', 'escalation', 'elevation', 'impersonate', 'impersonation', 'token', 'access', 'rights', 'permission', 'permissions', 'privileges'],
        'malware': ['malware', 'trojan', 'virus', 'malicious', 'mal', 'threat'],
        'classification': ['classification', 'classified', 'category', 'categories', 'type', 'types', 'maliciousness', 'Bad Reputation'],
        'exploit': ['exploit', 'vulnerability', 'brute'],
        'intrusion': ['intrusion', 'intruder', 'detection', 'detect'],
        'anomaly': ['anomaly', 'abnormal', 'anomalous', 'excessive', 'behavior', 'behaviour', 'abnormality', 'abnormalities', 'abnormally'],
        'monitoring': ['monitoring', 'surveillance'],
        'incident': ['incident', 'breach'],
        'data': ['data', 'exfiltration', 'leak'],
        'font': ['font'],
        'clipboard': ['clipboard', 'clip'],
        'application': ['application', 'installed application', 'installed applications', 'installed app', 'installed apps', 'app', 'apps', 'application', 'applications', 'installed', 'install', 'uninstall', 'uninstalled', 'uninstalling', 'installing', 'installer', 'uninstaller', 'installer', 'uninstaller', 'installers', 'uninstall'],
        'dns': ['dns', 'domain'],
        'smb': ['smb', 'share', 'samba'],
        'simpleservice': ['ftp', 'ping', 'http', 'https', 'telnet', 'ssh', 'sftp', 'dhcp', 'tftp', 'ntp', 'snmp', 'ldap', 'kerberos', 'rpc', 'rpcbind', 'service', 'daemon', 'services'],
        'mail': ['mail', 'email', 'imap', 'pop', 'smtp'],
        'windows': ['wmi', 'active', 'powershell', 'cmd', 'ad', 'gpo'],
        'mac': ['mac', 'osx', 'os x', 'macos', 'mac os', 'macosx', 'mac os x', 'macos x', 'macosx', 'macmru'],
        'unix': ['unix', 'sudo', 'suid', 'linux', 'posix', 'uname', 'sysctl', 'sys'],
        'manifest': ['manifest', 'resource'],
        'certificate': ['certificate', 'cert', 'certificates', 'certs', 'tls', 'ssl', 'code signing', 'signing'],
        'crypto': ['crypto', 'encrypt', 'decrypt', 'hash'],
        'schedule': ['schedule', 'task', 'job', 'cron', 'at', 'scheduler', 'batch'],
        'firmware': ['firmware', 'bios', 'uefi', 'boot', 'mft', 'mbr', 'gpt', 'efi', 'bootkit'],
        'firewall': ['firewall', 'rule'],
        'usb': ['usb', 'device'],
        'browser': ['browser', 'chrome', 'firefox', 'edge', 'ie', 'safari'],
        'office': ['excel', 'outlook', 'word', 'powerpoint', 'office365', 'office'],
        'script': ['script', 'macro', 'shell', 'powershell', 'bash', 'pty', 'runtime environment', 'environment variables'],
        'endpoint': ['endpoint', 'device'],
        'container': ['container', 'docker', 'kubernetes', 'pod', 'k8s', 'cluster', 'workload', 'workloads', 'containerd', 'namespace', 'instance', 'uncontainerize'],
        'cloud': ['cloud', 'aws', 'azure', 'gcp', 'awsiam', 'awss3', 'awscloudtrail', 'awscloudwatch', 'awscloudfront', 'awscloudformation', 'awscloudwatchlogs', 'awscloudwatchevents'],
        'null': ['null', 'undefined'],
        'info': ['info', 'telemetry', 'entry', 'status', 'compatibility'],
        'snapshot': ['snapshot', 'backup'],
        'policy': ['policy', 'compliance', 'complete', 'completed', 'suppression', 'config state update'],
        'agent': ['agent', 'falcon', 'sensor', 'falcon-sensor', 'zta', 'lightning', 'rtr', 'lfo', 'collector', 'ods', 'forensics', 'spotlight', 'idp', 'sps', 'shim', 'fcr', 'provisioning', 'injectionml'],
        'test': ['test', 'tests', 'debug', 'debuggable', 'suppressing', 'suppress', 'invalidated'],
        'cid': ['cid', 'customer id'],
        'mobile': ['apk', 'eapks', 'ios', 'android', 'mobile', 'phone', 'tablet', 'play', 'safety net'],
        # Add more tags and their corresponding keywords as needed
    }

    matching_tags = []  # List to store matching tags

    for tag, words in keywords.items():
        pattern = r"\b(?:{})\b".format("|".join(words))
        if re.search(pattern, description, flags=re.IGNORECASE):
            matching_tags.append(tag)

    return matching_tags


# Function to split words based on capital letters
def split_words(match):
    word = match.group(0)
    if len(word) > 1 and word.isupper():
        return word
    return ' ' + word


# Check if the JSON file path is provided as an argument
if len(sys.argv) < 3:
    print("Please provide the JSON file path as an argument.")
    sys.exit(1)

# Get the JSON file path and output file path from the command-line arguments
json_file_path = sys.argv[1]
output_file_path = sys.argv[2]

# Read in the JSON file
data = ""
with open(json_file_path) as json_file:
    data = json.load(json_file)

# Iterate over each collection
for item in data:
    # Split the name at each capital letter using regex with custom split_words function
    modified_name = re.sub(
        r'([A-Z](?=[a-z])|[A-Z]{2,}(?=[A-Z]))', split_words, item['name']).strip()

    # Update the name in the collection
    item['name_expanded'] = modified_name

    # Extract the tag from the description and name_expanded
    tag_d = extract_tag(item['description'])
    tag_n = extract_tag(item['name_expanded'])
    item['tags'] = list(set(tag_d + tag_n))

    if item['tags'] == []:
        print(f"No tags found for: ({item['id']}) {item['name_expanded']}")


# Print the dictionary to a json file
with open(output_file_path, 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)
