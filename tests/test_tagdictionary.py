import code
import re


def extract_tag(description):
    keywords = {
        'file': ['file', 'disk', 'rename', 'volume', 'io', 'directory', 'image'],
        'pe': ['pe', 'pe32', 'pe64', 'portable executable', 'executable'],
        'process': ['proc', 'pr2', 'process', 'start', 'thread', 'command', 'execute', 'fork', 'execution', 'executed', 'executing'],
        'memory': ['memory', 'allocate', 'free', 'amcache', 'cache', 'page', 'pool', 'heap', 'stack', 'virtual', 'physical', 'ram', 'swap', 'address', 'address space', 'addressspace', 'address-space', 'address_space', 'vad', 'vads', 'vadtree', 'vad_tree', 'vad tree', 'vadtree', 'mprotect', 'seh', 'sehchain'],
        'network': ['network', 'connection', 'request', 'bind', 'ip4', 'ip6', 'arp', 'promiscuous', 'remote', 'socket', 'channel', 'bindip4', 'bindip6', 'bindip', 'addressip4', 'addressip6', 'addressip', 'routeip4', 'routeip6', 'routeip', 'listip4', 'packet'],
        'dll': ['dll', 'loaded', 'dylib', 'so', 'module'],
        'hook': ['hook', 'hooked', 'api', 'call', 'function', 'handle'],
        'kernel': ['kernel', 'driver', 'os', 'system', 'nt', 'ntoskrnl', 'ntdll', 'ntos', 'ntoskrnl', 'ntdll'],
        'syscall': ['syscall', 'system call'],
        'time': ['time', 'timestamp', 'date', 'datetime', 'timezone', 'utc', 'gmt', 'localtime', 'local', 'zone', 'entropy'],
        'registry': ['registry', 'key', 'asep', 'reg'],
        'machine': ['hostname', 'host', 'machine', 'computer'],
        'manipulation': ['manipulation', 'zero', 'sign', 'bypass'],
        'authentication': ['authentication', 'login', 'logout', 'logon', 'logoff'],
        'user': ['user', 'account', 'credential', 'credentials', 'kerberos', 'ntlm', 'password'],
        'group': ['group', 'membership'],
        'audit': ['audit', 'logging', 'tamper', 'ledger', 'etw', 'amsi', 'log', 'error', 'warning', 'critical', 'info', 'debug', 'trace'],
        'privilege': ['privilege', 'escalation', 'elevation', 'impersonate', 'impersonation', 'token', 'access', 'rights', 'permission', 'permissions', 'privileges'],
        'malware': ['malware', 'trojan', 'virus'],
        'classification': ['classification', 'classified', 'category', 'categories', 'type', 'types', 'maliciousness'],
        'exploit': ['exploit', 'vulnerability', 'brute'],
        'intrusion': ['intrusion', 'intruder', 'detection', 'detect'],
        'anomaly': ['anomaly', 'abnormal', 'anomalous', 'excessive', 'behavior', 'behaviour', 'abnormality', 'abnormalities', 'abnormally'],
        'monitoring': ['monitoring', 'surveillance'],
        'incident': ['incident', 'breach'],
        'data': ['data', 'exfiltration', 'leak'],
        'font': ['font'],
        'clipboard': ['clipboard', 'clip'],
        'dns': ['dns', 'domain'],
        'smb': ['smb', 'share', 'samba'],
        'simpleservice': ['ftp', 'ping', 'http', 'https', 'telnet', 'ssh', 'sftp', 'dhcp', 'tftp', 'ntp', 'snmp', 'ldap', 'kerberos', 'rpc', 'rpcbind', 'service', 'daemon', 'services'],
        'mail': ['mail', 'email', 'imap', 'pop', 'smtp'],
        'windows': ['wmi', 'active', 'powershell', 'cmd', 'ad', 'gpo'],
        'mac': ['mac', 'osx', 'os x', 'macos', 'mac os', 'macosx', 'mac os x', 'macos x', 'macosx'],
        'unix': ['unix', 'sudo', 'suid', 'linux', 'posix', 'uname', 'sysctl', 'sys'],
        'manifest': ['manifest', 'resource'],
        'certificate': ['certificate', 'cert', 'certificates', 'certs', 'tls', 'ssl'],
        'crypto': ['crypto', 'encrypt', 'decrypt', 'hash'],
        'schedule': ['schedule', 'task', 'job', 'cron', 'at', 'scheduler', 'batch'],
        'firmware': ['firmware', 'bios', 'uefi', 'boot', 'mft', 'mbr', 'gpt', 'efi', 'bootkit'],
        'firewall': ['firewall', 'rule'],
        'usb': ['usb', 'device'],
        'browser': ['browser', 'chrome', 'firefox', 'edge', 'ie', 'safari'],
        'script': ['script', 'macro', 'shell', 'powershell', 'bash', 'pty'],
        'endpoint': ['endpoint', 'device'],
        'container': ['container', 'docker', 'kubernetes', 'pod', 'k8s', 'cluster', 'workload', 'workloads', 'containerd', 'namespace', 'instance'],
        'cloud': ['cloud', 'aws', 'azure', 'gcp', 'awsiam', 'awss3', 'awscloudtrail', 'awscloudwatch', 'awscloudfront', 'awscloudformation', 'awscloudwatchlogs', 'awscloudwatchevents'],
        'null': ['null', 'undefined'],
        'snapshot': ['snapshot', 'backup'],
        'policy': ['policy', 'compliance', 'complete', 'completed', 'suppression'],
        'agent': ['agent', 'falcon', 'sensor', 'falcon-sensor', 'zta', 'lightning', 'rtr', 'lfo', 'collector', 'ods', 'forensics', 'spotlight', 'idp', 'sps', 'telemetry', 'shim', 'fcr', 'provisioning'],
        'test': ['test', 'tests', 'debug', 'debuggable', 'suppressing', 'suppress'],
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


def test_extract_tag1():
    # Test 1: Matching "file"
    description = "This is a file operation."
    expected_tags = ['file']
    assert extract_tag(description) == expected_tags


def test_extract_tag2():
    # Test 2: Matching "pe"
    description = "The program is a portable executable."
    expected_tags = ['pe']
    assert extract_tag(description) == expected_tags


def test_extract_tag3():
    # Test 3: Matching "process" and not "pe" from "prepared"
    description = "A new prepared process was started."
    expected_tags = ['process']
    assert extract_tag(description) == expected_tags


def test_extract_tag4():
    # Test 4: Matching multiple tags
    description = "The file was renamed and a new process started."
    expected_tags = ['file', 'process']
    assert extract_tag(description) == expected_tags


def test_extract_tag5():
    # Test 4: Matching multiple tags
    description = "Safety Net Compatibility is enabled."
    expected_tags = ['mobile']
    assert extract_tag(description) == expected_tags
# code.interact(local=dict(globals(), **locals()))
