"""CLI interface for Falcon FDR Dictionary using Click."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table

from falcon_fdr_dictionary.config import Config, get_config
from falcon_fdr_dictionary.api_client import FDRClient
from falcon_fdr_dictionary.tagging import tag_dictionary

VERSION = "1.0.0"
console = Console()

BANNER = r"""
 ___   ___   ____          ___   _   _  ___   _  _   _____         ___    ___   ___  _____   ___   ____   _  _     _    ____   _  _  
) __( \   \ /  _ \  ____  ) __( \ ( ) /) __( ) \/ ( )__ __( ____  \   \  )_ _( / _( )__ __( )_ _( / __ \ ) \/ (   )_\  /  _ \ ) () ( 
| _)  | ) ( )  ' / )____( | _)   )\_/( | _)  |  \ |   | |  )____( | ) (  _| |_ ))_    | |   _| |_ ))__(( |  \ |  /( )\ )  ' / '.  /  
)_(   /___/ |_()_\        )___(   \_/  )___( )_()_(   )_(         /___/ )_____(\__(   )_(  )_____(\____/ )_()_( )_/ \_(|_()_\  /_(

Falcon FDR Event Dictionary v{version}
"""


class BannerGroup(click.Group):
    """Custom Click Group that displays banner before help."""

    def get_help(self, ctx):
        """Get help with banner."""
        config = Config.from_env() if Path('.env').exists() else None
        print_banner(config, force=True)
        return super().get_help(ctx)


def print_banner(config: Optional[Config] = None, force: bool = False) -> None:
    """Print the banner if enabled in config.

    Args:
        config: Optional Config object (if None, will try to load from env)
        force: Force print even if config.show_banner is False
    """
    show = force
    if config and not force:
        show = config.show_banner

    if show:
        console.print(BANNER.format(version=VERSION), style="bold cyan", highlight=False)


def setup_logging(log_level: str, log_file: str, verbose: bool) -> None:
    """Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        verbose: Enable verbose console logging
    """
    level = logging.DEBUG if verbose else getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, show_time=True, show_path=False),
            logging.FileHandler(log_file)
        ]
    )


@click.group(invoke_without_command=True, cls=BannerGroup)
@click.version_option(version=VERSION)
@click.pass_context
def cli(ctx):
    """CrowdStrike Falcon FDR Event Dictionary Tool.

    Fetch, tag, and manage CrowdStrike FDR event schemas.
    """
    ctx.ensure_object(dict)

    # When no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@cli.command()
@click.option(
    '--client-id',
    envvar='FALCON_CLIENT_ID',
    help='CrowdStrike API client ID (env: FALCON_CLIENT_ID)'
)
@click.option(
    '--client-secret',
    envvar='FALCON_CLIENT_SECRET',
    help='CrowdStrike API client secret (env: FALCON_CLIENT_SECRET)'
)
@click.option(
    '--cloud',
    envvar='FALCON_CLIENT_CLOUD',
    default='auto',
    type=click.Choice(['auto', 'us1', 'us2', 'eu1', 'usgov1', 'usgov2']),
    help='CrowdStrike cloud region (env: FALCON_CLIENT_CLOUD)'
)
@click.option(
    '-o', '--output',
    help='Output file path (default: fdr-event-dictionary.json)',
    type=click.Path()
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
def generate(
    client_id: Optional[str],
    client_secret: Optional[str],
    cloud: Optional[str],
    output: Optional[str],
    verbose: bool
):
    """Generate FDR event dictionary from CrowdStrike API.

    Fetches all FDR event schemas from the CrowdStrike API and saves them
    to a JSON file. The data is paginated and may take several minutes.
    """
    # Load config with CLI overrides
    try:
        config = get_config(client_id, client_secret, cloud)
    except ValueError as e:
        console.print(f"[yellow]No .env file found or credentials not set[/yellow]")
        if not client_id or not client_secret:
            console.print("[red]Error: Missing credentials[/red]")
            console.print("[yellow]Provide credentials via --client-id and --client-secret options[/yellow]")
            sys.exit(1)
        # Create minimal config from CLI args
        config = Config(
            falcon_client_id=client_id,
            falcon_client_secret=client_secret,
            falcon_client_cloud=cloud or 'auto'
        )

    # Setup logging
    setup_logging(config.log_level, config.log_file, verbose)
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Starting FDR Event Dictionary Generation")
    logger.info(f"Cloud region: {config.falcon_client_cloud}")
    logger.info(f"Log level: {config.log_level}")

    # Display banner
    print_banner(config)
    console.print(Panel.fit("Generate Mode", style="bold green"))

    # Validate cloud region
    if not config.validate_cloud_region():
        logger.error(f"Invalid cloud region: {config.falcon_client_cloud}")
        console.print(f"[red]Invalid cloud region: {config.falcon_client_cloud}[/red]")
        sys.exit(1)

    # Determine output file
    if output:
        output_file = output
    else:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / config.default_output_file

    logger.info(f"Output file: {output_file}")
    console.print(f"[cyan]Output file: {output_file}[/cyan]")
    console.print(f"[cyan]Cloud region: {config.falcon_client_cloud}[/cyan]\n")

    # Initialize API client
    client = FDRClient(
        config.falcon_client_id,
        config.falcon_client_secret,
        config.falcon_client_cloud
    )

    # Authenticate
    logger.info("Authenticating with CrowdStrike API...")
    with console.status("[yellow]Authenticating...[/yellow]"):
        if not client.authenticate():
            logger.error("Authentication failed")
            console.print("[red]✗ Authentication failed[/red]")
            sys.exit(1)

    logger.info("Authentication successful")
    console.print("[green]✓ Authentication successful[/green]\n")

    # Fetch dictionary
    complete_dictionary = []
    total = 1
    current_offset = 0

    try:
        # First request to get total count
        logger.info("Fetching initial page to determine total event count...")
        initial_result = client.get_dictionary_page(limit=200, offset=0)
        if initial_result.get('status_code') not in [200, 201]:
            errors = initial_result.get('errors', [])
            logger.error(f"Error fetching dictionary: {errors}")
            console.print(f"[red]✗ Error fetching dictionary: {errors}[/red]")
            sys.exit(1)

        total = initial_result.get('meta', {}).get('pagination', {}).get('total', 0)
        logger.info(f"Total events to fetch: {total}")
        console.print(f"[bold]Fetching {total:,} events...[/bold]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Fetching event details...", total=total)

            # Process first batch
            for resource_id in initial_result.get('resources', []):
                item = client.get_dictionary_item(resource_id)
                if item.get('resources'):
                    complete_dictionary.append(item['resources'][0])
                progress.update(task, advance=1)

            current_offset = len(initial_result.get('resources', []))

            # Fetch remaining pages
            while current_offset < total:
                page_result = client.get_dictionary_page(limit=200, offset=current_offset)
                if page_result.get('status_code') not in [200, 201]:
                    logger.error(f"Error at offset {current_offset}")
                    console.print(f"[red]✗ Error at offset {current_offset}[/red]")
                    break

                for resource_id in page_result.get('resources', []):
                    item = client.get_dictionary_item(resource_id)
                    if item.get('resources'):
                        complete_dictionary.append(item['resources'][0])
                    progress.update(task, advance=1)

                current_offset += len(page_result.get('resources', []))

        # Sort by ID
        logger.info(f"Sorting {len(complete_dictionary)} events by ID...")
        complete_dictionary = sorted(complete_dictionary, key=lambda k: k.get('id', 0))

        # Write to file
        logger.info(f"Writing {len(complete_dictionary)} events to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(complete_dictionary, outfile, indent=4, sort_keys=True)

        logger.info(f"Successfully generated dictionary with {len(complete_dictionary)} events")
        logger.info(f"Output saved to: {output_file}")
        logger.info("=" * 80)
        console.print(f"\n[bold green]✓ Successfully generated dictionary[/bold green]")
        console.print(f"[green]Saved {len(complete_dictionary)} events to: {output_file}[/green]")

    except KeyboardInterrupt:
        logger.warning("Generation interrupted by user")
        console.print("\n[yellow]Generation interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("Error during generation")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option(
    '-t', '--tag-files',
    multiple=True,
    type=click.Path(exists=True),
    help='Custom tag files to use (can be specified multiple times)'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
def tag(input_file: str, output_file: str, tag_files: tuple, verbose: bool):
    """Tag FDR event dictionary with keywords and expanded names.

    Reads a JSON dictionary file, adds 'name_expanded' and 'tags' fields
    to each event based on keyword matching, and writes the result to
    output file.

    \b
    Examples:
      falcon-fdr-events-dictionary tag input.json output.json
      falcon-fdr-events-dictionary tag dict.json tagged.json -v
      falcon-fdr-events-dictionary tag input.json output.json -t custom_tags.yaml
      falcon-fdr-events-dictionary tag input.json output.json -t tags1.yaml -t tags2.yaml
    """
    # Try to load config for logging settings and tag files
    try:
        config = Config.from_env()
        show_banner_flag = config.show_banner
        log_level = config.log_level
        log_file = config.log_file
        # Use CLI tag files if provided, otherwise use config
        tag_files_list = list(tag_files) if tag_files else config.tag_files
    except ValueError:
        show_banner_flag = True
        log_level = "INFO"
        log_file = "falcon_fdr_dictionary.log"
        tag_files_list = list(tag_files) if tag_files else None

    # Setup logging
    setup_logging(log_level, log_file, verbose)
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Starting FDR Event Dictionary Tagging")
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")
    if tag_files_list:
        logger.info(f"Tag files: {', '.join(tag_files_list)}")
        console.print(f"[cyan]Tag files: {', '.join(tag_files_list)}[/cyan]")
    else:
        logger.info("Tag files: Using default tags")
        console.print("[cyan]Tag files: Using default tags[/cyan]")
    console.print()

    try:
        # Read input file
        logger.info(f"Reading dictionary from {input_file}...")
        with console.status("[yellow]Reading dictionary...[/yellow]"):
            with open(input_file, 'r', encoding='utf-8') as f:
                events = json.load(f)

        logger.info(f"Loaded {len(events)} events")
        console.print(f"[green]✓ Loaded {len(events)} events[/green]\n")

        # Tag events
        logger.info("Tagging events with keywords...")
        with console.status("[yellow]Tagging events...[/yellow]"):
            tagged_events, untagged_events = tag_dictionary(events, tag_files_list)

        # Write output
        logger.info(f"Writing {len(tagged_events)} tagged events to {output_file}...")
        with console.status("[yellow]Writing output...[/yellow]"):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tagged_events, f, indent=4, sort_keys=True)

        logger.info(f"Successfully tagged {len(tagged_events)} events")
        logger.info(f"Events with no tags: {len(untagged_events)}")
        console.print(f"[bold green]✓ Successfully tagged dictionary[/bold green]")
        console.print(f"[green]Saved {len(tagged_events)} events to: {output_file}[/green]")

        # Report untagged events
        if untagged_events:
            logger.warning(f"{len(untagged_events)} events with no tags found")
            console.print(f"\n[yellow]⚠ {len(untagged_events)} events with no tags found:[/yellow]")
            for event in untagged_events[:10]:  # Show first 10
                console.print(f"  • ({event['id']}) {event.get('name_expanded', event['name'])}")
            if len(untagged_events) > 10:
                console.print(f"  ... and {len(untagged_events) - 10} more")
        else:
            logger.info("All events successfully tagged")
            console.print("\n[green]✓ All events successfully tagged[/green]")

        logger.info("=" * 80)

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        console.print(f"[red]✗ Error: Input file not found: {input_file}[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in input file: {e}")
        console.print(f"[red]✗ Error: Invalid JSON in input file: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Tagging interrupted by user")
        console.print("\n[yellow]Tagging interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("Error during tagging")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    '--client-id',
    envvar='FALCON_CLIENT_ID',
    help='CrowdStrike API client ID (env: FALCON_CLIENT_ID)'
)
@click.option(
    '--client-secret',
    envvar='FALCON_CLIENT_SECRET',
    help='CrowdStrike API client secret (env: FALCON_CLIENT_SECRET)'
)
@click.option(
    '--cloud',
    envvar='FALCON_CLIENT_CLOUD',
    default='auto',
    type=click.Choice(['auto', 'us1', 'us2', 'eu1', 'usgov1', 'usgov2']),
    help='CrowdStrike cloud region (env: FALCON_CLIENT_CLOUD)'
)
def validate(
    client_id: Optional[str],
    client_secret: Optional[str],
    cloud: Optional[str]
):
    """Validate CrowdStrike API credentials and FDR access.

    Checks that credentials are valid and can access the FDR API.
    Verifies API version and endpoint availability.
    """
    # Load config with CLI overrides
    try:
        config = get_config(client_id, client_secret, cloud)
    except ValueError as e:
        console.print(f"[yellow]No .env file found or credentials not set[/yellow]")
        if not client_id or not client_secret:
            console.print("[red]Error: Missing credentials[/red]")
            console.print("[yellow]Provide credentials via --client-id and --client-secret options[/yellow]")
            sys.exit(1)
        # Create minimal config from CLI args
        config = Config(
            falcon_client_id=client_id,
            falcon_client_secret=client_secret,
            falcon_client_cloud=cloud or 'auto'
        )

    # Setup logging
    setup_logging(config.log_level, config.log_file, False)
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Starting credential validation")
    logger.info(f"Cloud region: {config.falcon_client_cloud}")

    # Display banner
    print_banner(config)
    console.print(Panel.fit("Validate Mode", style="bold blue"))

    # Validate cloud region
    if not config.validate_cloud_region():
        logger.error(f"Invalid cloud region: {config.falcon_client_cloud}")
        console.print(f"[red]✗ Invalid cloud region: {config.falcon_client_cloud}[/red]")
        sys.exit(1)

    console.print(f"[cyan]Cloud Region: {config.falcon_client_cloud}[/cyan]\n")

    # Create client
    client = FDRClient(
        config.falcon_client_id,
        config.falcon_client_secret,
        config.falcon_client_cloud
    )

    # Validate credentials
    logger.info("Validating API credentials...")
    with console.status("[yellow]Validating credentials...[/yellow]"):
        success, message = client.validate_credentials()

    if success:
        logger.info(f"Validation successful: {message}")
        logger.info(f"Base URL: {client.get_base_url()}")
        logger.info("=" * 80)
        console.print(f"\n[bold green]✓ {message}[/bold green]")
        console.print("[green]Your credentials and permissions are correctly configured.[/green]")
        console.print(f"[green]Base URL: {client.get_base_url()}[/green]")
    else:
        logger.error(f"Validation failed: {message}")
        logger.info("=" * 80)
        console.print(f"\n[bold red]✗ {message}[/bold red]")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})  # pylint: disable=no-value-for-parameter
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
