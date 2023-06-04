#!/usr/bin/env python
# -*- coding: utf-8 -*-

r"""FDR Event Dictionary.
 ___   ___   ____          ___   _   _  ___   _  _   _____         ___    ___   ___  _____   ___   ____   _  _     _    ____   _  _  
) __( \   \ /  _ \  ____  ) __( \ ( ) /) __( ) \/ ( )__ __( ____  \   \  )_ _( / _( )__ __( )_ _( / __ \ ) \/ (   )_\  /  _ \ ) () ( 
| _)  | ) ( )  ' / )____( | _)   )\_/( | _)  |  \ |   | |  )____( | ) (  _| |_ ))_    | |   _| |_ ))__(( |  \ |  /( )\ )  ' / '.  /  
)_(   /___/ |_()_\        )___(   \_/  )___( )_()_(   )_(         /___/ )_____(\__(   )_(  )_____(\____/ )_()_( )_/ \_(|_()_\  /_(

"""

import sys
import json
import requests

try:
    from falconpy import APIHarness
except ImportError as no_falconpy:
    raise SystemExit(
        "The CrowdStrike SDK must be installed in order to use this utility.\n"
        "Install this application with the command `python3 -m pip install crowdstrike-falconpy`."
    ) from no_falconpy

from argparse import ArgumentParser, RawTextHelpFormatter


ex = """
Example(s):
./falcon-fdr-event-dictionary.py  -k $FALCON_CLIENT_ID -s $FALCON_CLIENT_SECRET
./falcon-fdr-event-dictionary.py  -k $FALCON_CLIENT_ID -s $FALCON_CLIENT_SECRET -b $FALCON_BASE_URL
"""

# Helper Function for Error Printing


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Main Class GetFDRDictionary


class GetFDRDictionary:
    version = '0.1.0'
    name = "Get FDR Event Dictionary"
    description = "Get FDR Event Dictionary from CrowdStrike API in JSON format"

    def __init__(self, argv):
        """
            Initialize all stuff
        """
        self.headers = {'Content-Type': 'application/json',
                        'accept': 'application/json', }
        # Set file header
        self.body = None
        # self.verifySSL = None
        self.code = None
        self.json = None
        self.falcon = None
        self.argv = argv
        self.parse_args()

    def parse_args(self):
        """Parse the arguments provided on the command line.

        Returns: a pair (continue, exit_code). If continue is False,
          the exit_code should be returned.
        """
        parser = ArgumentParser(
            usage='%(prog)s [options]',
            description=__doc__,
            formatter_class=RawTextHelpFormatter,
            add_help=True,
            epilog=ex)
        options = parser.add_argument_group('Options')
        options.add_argument(
            '-v', '--version', action='version', version=f'%(prog)s {self.version}'
        )
        req = parser.add_argument_group("required arguments")
        req.add_argument(
            "-k", "--falcon_client_id",
            help="CrowdStrike Falcon API Client ID",
            required=True
        )

        req.add_argument(
            "-s", "--falcon_client_secret",
            help="CrowdStrike Falcon API Client Secret",
            required=True
        )

        parser.add_argument(
            '-b', '--base_url',
            help="CrowdStrike base URL for Gov Clouds",
            required=False,
            default="auto"
        )

        output = parser.add_argument_group("Output options")
        output.add_argument(
            '-o', '--output',
            help='Output file name',
            required=False,
            default='fdr-event-dictionary.json'
        )

        parser.add_argument(
            '-V', '--verbose', help='verbose mode', action='store_true'
        )
        parser.parse_args(self.argv, namespace=GetFDRDictionary)

        self.verboseMode = bool(self.verbose)

    # "pagination": {
    #    "offset": 0,
    #    "limit": 100,
    #    "total": 1709
    # },
    def getDictionary(self, limit='200', offset='0'):
        self.headers = {
            "accept": "application/json",
            "authorization": f"bearer {self.falcon.token}",
        }
        content = {}
        if self.base_url == 'auto':
            base = 'https://api.crowdstrike.com'
        else:
            base = self.base_url
        request = self._request(
            f'{base}/fdr/queries/schema-events/v1?limit={limit}&offset={offset}',
            'GET',
            headers=self.headers,
        )

        if request.status_code in [200, 201]:
            content = json.loads(request.content.decode("utf-8"))
            content['status_code'] = request.status_code
        else:
            content = self.zeroResource(request)
        return content

    def getDictionaryItem(self, id):
        self.headers = {
            "accept": "application/json",
            "authorization": f"bearer {self.falcon.token}",
        }
        content = {}
        if self.base_url == 'auto':
            base = 'https://api.crowdstrike.com'
        else:
            base = self.base_url
        request = self._request(
            f'{base}/fdr/entities/schema-events/v1?ids={id}',
            'GET',
            headers=self.headers,
        )

        if request.status_code in [200, 201]:
            content = json.loads(request.content.decode("utf-8"))
            content['status_code'] = request.status_code
        else:
            content = self.zeroResource(request)
        return content

    # non-200 status codes
    def zeroResource(self, request):
        content = json.loads(request.content.decode("utf-8"))
        content['status_code'] = request.status_code
        content['resources'] = []
        return content

    def _request(self, url, method, headers='', data='', params=''):
        """
        Establish HTTP connection using called method.

        Returns: HTTP response in dictionary format.
        """
        response = ''
        self.headers.update(headers)
        while True:
            try:
                prepared = requests.Request(
                    method.upper(), url, headers=headers, data=data, params=params).prepare()

                if self.verboseMode:
                    message = '{}\n{}\n{}\n\n{}'.format(
                        '-----------BEGIN REQUEST-----------',
                        f'{prepared.method} {prepared.url}',
                        '\n'.join(
                            '{}: {}'.format(k, v)
                            for k, v in prepared.headers.items()
                        ),
                        prepared.body,
                    )
                    print(message)

                self.session = requests.Session()
                response = self.session.send(prepared)

                if self.verboseMode:
                    message = '{}\n\nStatus-Code:{}\n{}\n\nContent: {}'.format(
                        '-----------BEGIN RESPONSE-----------',
                        response.status_code,
                        '\n'.join('{}: {}'.format(k, v)
                                  for k, v in response.headers.items()), response.content
                    )
                    print(message)
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(
                    "Unexpected error:\n{}\n\nWe will try to continue, let's see.".format(str(e)))

                def response(): return None
                setattr(response, 'status_code', False)
                break
            break

        return response

    def main(self):
        """Main body of the script."""

        CompleteDictionary = []
        # Login to the Falcon API and retrieve our list of sensors
        self.falcon = APIHarness(client_id=self.falcon_client_id,
                                 client_secret=self.falcon_client_secret, base_url=self.base_url)
        if self.falcon.authenticate():
            if self.verboseMode:
                eprint("Authentication successful")
                eprint(self.falcon.token)
        else:
            if self.verboseMode:
                eprint("Authentication failure")
            sys.exit(1)

        total = 1
        current_offset = 0

        while current_offset < total:
            dictionaryList = self.getDictionary(
                limit='200', offset=str(current_offset))
            if dictionaryList['status_code'] in [200, 201]:
                total = dictionaryList['meta']['pagination']['total']
                current_set_length = len(dictionaryList['resources'])
            else:
                eprint(
                    f"Error: {dictionaryList['status_code']} {dictionaryList['errors']}")
                sys.exit(1)

            print(f"Length of current set: {current_set_length}")
            print(f"{current_offset} of {total}")
            for resource in dictionaryList['resources']:
                dictionaryItem = self.getDictionaryItem(id=resource)
                print(".", end="", flush=True)
                try:
                    if len(dictionaryItem['resources']) > 0:
                        CompleteDictionary.append(
                            dictionaryItem['resources'][0])
                except Exception:
                    eprint(f"Error: {dictionaryItem}")
            print("-", flush=True)
            current_offset += current_set_length
        CompleteDictionary = sorted(CompleteDictionary, key=lambda k: k['id'])

       # Print the dictionary to a file
        with open('fdr-event-dictionary.json', 'w') as outfile:
            json.dump(CompleteDictionary, outfile, indent=4, sort_keys=True)

# Main Function


def main(argv=None):
    if len(sys.argv[1:]) == 0:
        sys.argv[1:].append("--help")
    ma = GetFDRDictionary(argv or sys.argv[1:])
    return ma.main()


if __name__ == "__main__":
    sys.exit(main())
