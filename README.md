# Falcon FDR Event Dictionary

A comprehensive Python CLI tool for fetching, tagging, and managing CrowdStrike Falcon FDR (Flight Data Recorder) event schemas. Built with modern Python packaging, Rich terminal UI, and YAML-based configuration.

## Core Features

**Generate Event Dictionary** - Fetch all FDR event schemas from CrowdStrike API with progress tracking  

```txt
 ___   ___   ____          ___   _   _  ___   _  _   _____         ___    ___   ___  _____   ___   ____   _  _     _    ____   _  _  
) __( \   \ /  _ \  ____  ) __( \ ( ) /) __( ) \/ ( )__ __( ____  \   \  )_ _( / _( )__ __( )_ _( / __ \ ) \/ (   )_\  /  _ \ ) () ( 
| _)  | ) ( )  ' / )____( | _)   )\_/( | _)  |  \ |   | |  )____( | ) (  _| |_ ))_    | |   _| |_ ))__(( |  \ |  /( )\ )  ' / '.  /  
)_(   /___/ |_()_\        )___(   \_/  )___( )_()_(   )_(         /___/ )_____(\__(   )_(  )_____(\____/ )_()_( )_/ \_(|_()_\  /_(

Falcon FDR Event Dictionary v1.0.0

╭───────────────╮
│ Generate Mode │
╰───────────────╯
Output file: docs/fdr-event-dictionary.json
Cloud region: auto

✓ Authentication successful

Fetching 2,847 events...

⠋ Fetching event details... ████████████████████░░░░░░░░  75% (2135/2847) 0:01:23

✓ Successfully generated dictionary
Saved 2847 events to: docs/fdr-event-dictionary.json
```

### Additonal Features

**Smart Tagging** - Automatically tag events with keywords from customizable YAML files  
**Credential Validation** - Verify API credentials and permissions before operations  
**Rich Terminal Output** - Beautiful progress bars, tables, and status indicators  
**Comprehensive Logging** - Detailed audit trail of all operations  
**Flexible Configuration** - .env file support with CLI overrides  

## Requirements

* Python 3.8+
* CrowdStrike API credentials with FDR read scope
* pip or pipenv for installation

## Installation

### Install from source (recommended for development)

```bash
git clone https://github.com/cs-shadowbq/falcon-fdr-dictionary.git
cd falcon-fdr-dictionary
pip install -e .
```

This installs the package in editable mode with all dependencies.

## Configuration

### Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```dotenv
# Required
FALCON_CLIENT_ID=your_client_id_here
FALCON_CLIENT_SECRET=your_client_secret_here
FALCON_CLIENT_CLOUD=auto

# Optional
OUTPUT_DIR=./docs
DEFAULT_OUTPUT_FILE=fdr-event-dictionary.json
LOG_LEVEL=INFO
LOG_FILE=falcon_fdr_dictionary.log
TAG_FILES=/path/to/custom_tags.yaml
```

### Command-Line Overrides

All environment variables can be overridden via CLI options:

```bash
falcon-fdr-events-dictionary generate \
  --client-id YOUR_ID \
  --client-secret YOUR_SECRET \
  --cloud us1 \
  -o custom-output.json
```

## Usage

### Command Structure

```
falcon-fdr-events-dictionary [OPTIONS] COMMAND [ARGS]...
```

### Available Commands

#### 1. `generate` - Fetch FDR Event Dictionary

Fetches all FDR event schemas from CrowdStrike API with progress tracking:

```bash
# Using .env configuration
falcon-fdr-events-dictionary generate

# With CLI options
falcon-fdr-events-dictionary generate \
  --client-id YOUR_ID \
  --client-secret YOUR_SECRET \
  --cloud us1 \
  -o output.json \
  -v
```

**Options:**

* `--client-id TEXT` - CrowdStrike API client ID (env: FALCON_CLIENT_ID)
* `--client-secret TEXT` - CrowdStrike API client secret (env: FALCON_CLIENT_SECRET)
* `--cloud [auto|us1|us2|eu1|usgov1|usgov2]` - Cloud region (env: FALCON_CLIENT_CLOUD)
* `-o, --output PATH` - Output file path
* `-v, --verbose` - Enable verbose output

**Example Output:**

```
 ___   ___   ____          ___   _   _  ___   _  _   _____         ___    ___   ___  _____   ___   ____   _  _     _    ____   _  _  
) __( \   \ /  _ \  ____  ) __( \ ( ) /) __( ) \/ ( )__ __( ____  \   \  )_ _( / _( )__ __( )_ _( / __ \ ) \/ (   )_\  /  _ \ ) () ( 
| _)  | ) ( )  ' / )____( | _)   )\_/( | _)  |  \ |   | |  )____( | ) (  _| |_ ))_    | |   _| |_ ))__(( |  \ |  /( )\ )  ' / '.  /  
)_(   /___/ |_()_\        )___(   \_/  )___( )_()_(   )_(         /___/ )_____(\__(   )_(  )_____(\____/ )_()_( )_/ \_(|_()_\  /_(

Falcon FDR Event Dictionary v1.0.0

╭───────────────╮
│ Generate Mode │
╰───────────────╯
Output file: docs/fdr-event-dictionary.json
Cloud region: auto

✓ Authentication successful

Fetching 2,847 events...

⠋ Fetching event details... ████████████████████░░░░░░░░  75% (2135/2847) 0:01:23

✓ Successfully generated dictionary
Saved 2847 events to: docs/fdr-event-dictionary.json
```

#### 2. `tag` - Add Tags and Expanded Names

Adds human-readable event names and keyword-based tags to the dictionary:

```bash
# Using default tags
falcon-fdr-events-dictionary tag input.json output.json

# Using custom tag files
falcon-fdr-events-dictionary tag input.json output.json \
  -t custom_tags.yaml \
  -t additional_tags.yaml \
  -v
```

**Options:**

* `-t, --tag-files PATH` - Custom tag files (can be specified multiple times)
* `-v, --verbose` - Enable verbose output

**Example Output:**

```
Tag files: Using default tags

✓ Loaded 2847 events

✓ Successfully tagged dictionary
Saved 2847 events to: output.json

✓ All events successfully tagged
```

#### 3. `validate` - Validate API Credentials

Verifies API credentials and FDR access permissions:

```bash
# Using .env configuration
falcon-fdr-events-dictionary validate

# With specific credentials
falcon-fdr-events-dictionary validate \
  --client-id YOUR_ID \
  --client-secret YOUR_SECRET \
  --cloud us1
```

**Example Output:**

```
╭───────────────╮
│ Validate Mode │
╰───────────────╯
Cloud Region: us-1

✓ Validation successful - API access confirmed
Your credentials and permissions are correctly configured.
Base URL: https://api.us-1.crowdstrike.com
```

## Tag Files

### Default Tags

The tool includes 60+ built-in tags in `falcon_fdr_dictionary/tags/default_tags.yaml`:

```yaml
file: [file, files, disk, rename, volume, io, directory, image, symbolic link]
process: [process, processes, executable, execution, spawn]
network: [network, socket, connection, tcp, udp, port, dns, http]
memory: [memory, heap, allocation, page, virtual]
registry: [registry, reg key, hive, regkey]
authentication: [auth, login, logon, credential, password, token]
malware: [malware, virus, trojan, ransomware, backdoor]
# ... and 50+ more categories
```

### Custom Tag Files

Create custom YAML files for organization-specific tagging:

```yaml
# my_custom_tags.yaml
custom_category: [keyword1, keyword2, keyword3]
incident_response: [forensics, investigation, triage]
compliance: [pci, hipaa, gdpr, sox]
```

Load multiple tag files (they merge with default tags):

```bash
falcon-fdr-events-dictionary tag input.json output.json \
  -t my_custom_tags.yaml \
  -t team_tags.yaml
```

Or configure in `.env`:

```dotenv
TAG_FILES=/path/to/custom_tags.yaml,/path/to/team_tags.yaml
```

## Output Format

### Generated Dictionary Entry

```json
{
    "id": "268435640",
    "name": "ManifestDownloadComplete",
    "description": "Sent by LFODownloadActor when a new configuration manifest has been downloaded.",
    "platform": "mac",
    "base_id": "184",
    "version": 1,
    "fields": [
        {
            "id": "15",
            "name": "TargetFileName",
            "optional": false,
            "version-added": 0
        },
        {
            "id": "4",
            "name": "Status",
            "optional": false,
            "version-added": 0
        }
    ]
}
```

### Tagged Dictionary Entry

After running the `tag` command, entries include:

```json
{
    "id": "268435640",
    "name": "ManifestDownloadComplete",
    "name_expanded": "Manifest Download Complete",
    "description": "Sent by LFODownloadActor when a new configuration manifest has been downloaded.",
    "platform": "mac",
    "tags": [
        "configuration",
        "download",
        "file"
    ],
    "base_id": "184",
    "version": 1,
    "fields": [...]
}
```

## Advanced Usage

### Filtering with jq

Extract only essential fields:

```bash
cat fdr-event-dictionary.json | \
  jq 'map(del(.version,.base_id,.fields))' > filtered.json
```

### Converting to CSV

```bash
cat docs/fdr-event-dictionary-tagged.json | \
  jq -r '["id","name","name_expanded","platform","tags"],
         (.[] | [.id, .name, .name_expanded, .platform, (.tags | join(";"))])
         | @csv' > dictionary.csv
```

### Viewing in Terminal

Use Rich tables (built into the tool) or pipe to external tools:

```bash
cat fdr-event-dictionary-tagged.json | \
  jq 'map(del(.version,.base_id,.fields))' | \
  python -m json.tool
```

## Logging

All operations are logged to `falcon_fdr_dictionary.log` (configurable):

```
================================================================================
Starting FDR Event Dictionary Generation
Cloud region: us-1
Log level: INFO
Output file: docs/fdr-event-dictionary.json
Authenticating with CrowdStrike API...
Authentication successful
Fetching initial page to determine total event count...
Total events to fetch: 2847
Sorting 2847 events by ID...
Writing 2847 events to docs/fdr-event-dictionary.json...
Successfully generated dictionary with 2847 events
Output saved to: docs/fdr-event-dictionary.json
================================================================================
```

## Development

See [DEV.md](DEV.md) for development setup, architecture details, and contributing guidelines.

## Troubleshooting

### Authentication Failures

```bash
# Validate your credentials first
falcon-fdr-events-dictionary validate

# Check your .env file
cat .env

# Ensure API scope includes FDR read permissions
```

### Tag Files Not Loading

```bash
# Check tag file path and permissions
ls -la /path/to/custom_tags.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('custom_tags.yaml'))"

# Run with verbose mode to see tag loading messages
falcon-fdr-events-dictionary tag input.json output.json -t custom_tags.yaml -v
```

## Cloud Regions

Supported CrowdStrike cloud regions:

* `auto` - Automatic detection (default)
* `us1` - US Commercial 1
* `us2` - US Commercial 2
* `eu1` - European Union
* `usgov1` - US Government 1
* `usgov2` - US Government 2

## License

See [LICENSE](LICENSE) file for details.

## Credits

Developed and maintained by the CrowdStrike community.

## Related Projects

* [falcon-policy-scoring](https://github.com/cs-shadowbq/falcon-policy-scoring) - Policy audit and scoring tool
* [cao-report-fetcher](https://github.com/cs-shadowbq/cao-report-fetcher) - CrowdStrike report automation

## Support

For issues, questions, or contributions:

* Open an issue on GitHub
* See [DEV.md](DEV.md) for development guidelines
* Consult CrowdStrike API documentation for FDR schema details
