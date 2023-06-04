# Falcon FDR Event Dictionary

This tool will pull the Falcon FDR event dictionary and save it to a file in the current directory. The file will be named `falcon-fdr-event-dictionary.json`.

## Requirements

* Python 3.6+
* Falcon API client
* Falcon API secret
* Falcon API with proper scope
* Falcon API base URL (optional, defaults to `https://api.crowdstrike.com`)

## Usage

### Installation

Python package can be installed from PyPI: (When available TBD)

```bash
pip install falcon-fdr-event-dictionary
```

You can also install directly from source:

```bash
python setup.py install
```

You can also just run the script directly:

```bash
python ./falcon-fdr-event-dictionary.py -k $FALCON_CLIENT_ID -s $FALCON_CLIENT_SECRET
```

## Falcon FDR Event Dictionary

This tool will pull the Falcon FDR event dictionary and save it to a file in the current directory.
When running directly from the script, the file will be named `falcon-fdr-event-dictionary.json` by default.

```shell
usage: falcon-fdr-event-dictionary.py [options]

FDR Event Dictionary.
 ___   ___   ____          ___   _   _  ___   _  _   _____         ___    ___   ___  _____   ___   ____   _  _     _    ____   _  _
) __( \   \ /  _ \  ____  ) __( \ ( ) /) __( ) \/ ( )__ __( ____  \   \  )_ _( / _( )__ __( )_ _( / __ \ ) \/ (   )_\  /  _ \ ) () (
| _)  | ) ( )  ' / )____( | _)   )\_/( | _)  |  \ |   | |  )____( | ) (  _| |_ ))_    | |   _| |_ ))__(( |  \ |  /( )\ )  ' / '.  /
)_(   /___/ |_()_\        )___(   \_/  )___( )_()_(   )_(         /___/ )_____(\__(   )_(  )_____(\____/ )_()_( )_/ \_(|_()_\  /_(

optional arguments:
  -h, --help            show this help message and exit
  -b BASE_URL, --base_url BASE_URL
                        CrowdStrike base URL for Gov Clouds
  -V, --verbose         verbose mode

Options:
  -v, --version         show program's version number and exit

required arguments:
  -k FALCON_CLIENT_ID, --falcon_client_id FALCON_CLIENT_ID
                        CrowdStrike Falcon API Client ID
  -s FALCON_CLIENT_SECRET, --falcon_client_secret FALCON_CLIENT_SECRET
                        CrowdStrike Falcon API Client Secret

Output options:
  -o OUTPUT, --output OUTPUT
                        Output file name

Example(s):
./falcon-fdr-event-dictionary.py  -k $FALCON_CLIENT_ID -s $FALCON_CLIENT_SECRET
./falcon-fdr-event-dictionary.py  -k $FALCON_CLIENT_ID -s $FALCON_CLIENT_SECRET -b $FALCON_BASE_URL
```

### Example

Note the FDR Event Dictionary download request is paginated, and the script will automatically download all pages. This may take a few minutes.

```python
 python ./falcon-fdr-event-dictionary.py -k $FALCON_CLIENT_ID -s $FALCON_CLIENT_SECRET
Length of current set: 200
0 of 1709
........................................................................................................................................................................................................-
Length of current set: 200
200 of 1709
........................................................................................................................................................................................................-
Length of current set: 200
400 of 1709
........................................................................................................................................................................................................-
Length of current set: 200
600 of 1709
........................................................................................................................................................................................................-
Length of current set: 200
800 of 1709
........................................................................................................................................................................................................-
Length of current set: 200
1000 of 1709
........................................................................................................................................................................................................-
Length of current set: 200
1200 of 1709
........................................................................................................................................................................................................-
Length of current set: 200
1400 of 1709
........................................................................................................................................................................................................-
Length of current set: 109
1600 of 1709
.............................................................................................................-
```

## Tagging the DataSets created by Falcon FDR Schemas Dictionary

You can tag the DataSets created by Falcon FDR Schemas Dictionary with the following command:


```shell
python ./bin/tag-dictionary.py docs/fdr-event-dictionary-filtered.json docs/fdr-event-dictionary-tagged.json
```

This script takes a JSON file as input and outputs a JSON file with the tag and name_expanded fields added to each collection. The function uses a dictionary of keywords and their corresponding tags to find likely tags. The script also prints to STDOUT the collections for which no tag was found

An example of the tag cloud keword dictionary:

```python
keywords = {
        'file': ['file', 'files', 'disk', 'rename', 'volume', 'io', 'directory', 'image', 'symbolic link'],
        'pe': ['pe', 'pe32', 'pe64', 'portable executable', 'executable'],
}
```

### Example

```shell
python tag-dictionary.py docs/fdr-event-dictionary-filtered.json docs/fdr-event-dictionary-tagged.json
No tag found for: (999999) New Unknown Keyword Found
```

## Filtering or Converting the JSON Dictionary

You may want to simplify the dictionary to only include the `name`, `id`, `description`, and `platform` fields. This can be done with the following command:

Using `jq`:

```shell
cat fdr-event-dictionary.json | jq 'map(del(.version,.base_id,.fields))' > fdr-event-dictionary-filtered.json
```

You can also use `jtbl` to convert the JSON to CSV:

Using `jtbl`:

```shell
cat docs/fdr-event-dictionary-tagged.json |jtbl -c > dictionary.csv
```

You can also use `jq` and `jtbl` to better view the data in the terminal:

```shell
cat fdr-event-dictionary.json | jq 'map(del(.version,.base_id,.fields))' | jtbl

╒══════════════════════════════╤════════════╤══════════════════════════════╤══════════════════════════════╤══════════════╤══════════════════════════════╕
│ description                  │         id │ name                         │ name_expanded                │ platform     │ tag                          │
╞══════════════════════════════╪════════════╪══════════════════════════════╪══════════════════════════════╪══════════════╪══════════════════════════════╡
│                              │  805308726 │ SysConfigInfo                │ Sys Config Info              │ linux        │ ['unix', 'info', 'audit']    │
├──────────────────────────────┼────────────┼──────────────────────────────┼──────────────────────────────┼──────────────┼──────────────────────────────┤
│                              │  805308759 │ EmailFileWritten             │ Email File Written           │ linux        │ ['file', 'mail']             │
├──────────────────────────────┼────────────┼──────────────────────────────┼──────────────────────────────┼──────────────┼──────────────────────────────┤
│                              │  805308800 │ TestStringFormatHexlify      │ Test String Format Hexlify   │ linux        │ ['test']                     │
├──────────────────────────────┼────────────┼──────────────────────────────┼──────────────────────────────┼──────────────┼──────────────────────────────┤
...
```

## License

MIT License
