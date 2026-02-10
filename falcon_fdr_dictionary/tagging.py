"""Event dictionary tagging and name expansion functionality."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
from rich.console import Console

console = Console()

# Global keyword cache
_KEYWORDS_CACHE: Optional[Dict[str, List[str]]] = None


def get_default_tags_file() -> Path:
    """Get the path to the default tags file.

    Returns:
        Path to default_tags.yaml
    """
    return Path(__file__).parent / "tags" / "default_tags.yaml"


def load_tag_files(tag_files: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """Load tag keyword mappings from YAML files.

    Args:
        tag_files: List of paths to tag YAML files. If None, uses default.

    Returns:
        Dictionary mapping tag names to keyword lists

    Raises:
        FileNotFoundError: If a tag file doesn't exist
        yaml.YAMLError: If a tag file has invalid YAML
    """
    keywords: Dict[str, List[str]] = {}

    # If no files specified, use default
    if not tag_files:
        tag_files = [str(get_default_tags_file())]

    for tag_file_path in tag_files:
        tag_path = Path(tag_file_path)

        if not tag_path.exists():
            console.print(f"[yellow]Warning: Tag file not found: {tag_file_path}[/yellow]")
            continue

        try:
            with open(tag_path, 'r', encoding='utf-8') as f:
                file_keywords = yaml.safe_load(f)

            if not file_keywords:
                console.print(f"[yellow]Warning: Empty tag file: {tag_file_path}[/yellow]")
                continue

            # Merge keywords, later files can override earlier ones or add new tags
            for tag, words in file_keywords.items():
                # Skip invalid entries
                if tag is None or words is None:
                    console.print(f"[yellow]Warning: Skipping invalid tag entry in {tag_file_path}[/yellow]")
                    continue

                # Ensure words is a list
                if not isinstance(words, list):
                    console.print(f"[yellow]Warning: Tag '{tag}' in {tag_file_path} has invalid format, skipping[/yellow]")
                    continue

                if tag in keywords:
                    # Merge and deduplicate keywords for existing tag
                    keywords[tag] = list(set(keywords[tag] + words))
                else:
                    keywords[tag] = words

        except yaml.YAMLError as e:
            console.print(f"[red]Error parsing tag file {tag_file_path}: {e}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Error loading tag file {tag_file_path}: {e}[/red]")
            raise

    return keywords


def get_keywords(tag_files: Optional[List[str]] = None, force_reload: bool = False) -> Dict[str, List[str]]:
    """Get keyword mappings, using cache if available.

    Args:
        tag_files: List of paths to tag YAML files. If None, uses default.
        force_reload: Force reload even if cached

    Returns:
        Dictionary mapping tag names to keyword lists
    """
    global _KEYWORDS_CACHE

    # Use cache if available and not forcing reload
    if _KEYWORDS_CACHE is not None and not force_reload and not tag_files:
        return _KEYWORDS_CACHE

    # Load from files
    keywords = load_tag_files(tag_files)

    # Cache default keywords
    if not tag_files:
        _KEYWORDS_CACHE = keywords

    return keywords


def extract_tags(description: str, keywords: Optional[Dict[str, List[str]]] = None) -> List[str]:
    """Extract tags from a description based on keyword matching.

    Args:
        description: The text to extract tags from
        keywords: Optional keyword dictionary. If None, uses default.

    Returns:
        List of matching tag names
    """
    if keywords is None:
        keywords = get_keywords()

    matching_tags = []

    for tag, words in keywords.items():
        # Skip invalid entries
        if tag is None or words is None or not isinstance(words, list):
            continue

        pattern = r"\b(?:{})\b".format("|".join(re.escape(word) for word in words))
        if re.search(pattern, description, flags=re.IGNORECASE):
            matching_tags.append(tag)

    return matching_tags


def split_words(match: re.Match) -> str:
    """Split CamelCase words by inserting spaces before capitals.

    Args:
        match: Regex match object

    Returns:
        Modified string with spaces
    """
    word = match.group(0)
    if len(word) > 1 and word.isupper():
        return word
    return ' ' + word


def expand_name(name: str) -> str:
    """Expand a CamelCase name by inserting spaces.

    Args:
        name: The CamelCase name to expand

    Returns:
        Name with spaces inserted before capital letters
    """
    modified_name = re.sub(
        r'([A-Z](?=[a-z])|[A-Z]{2,}(?=[A-Z]))',
        split_words,
        name
    ).strip()
    return modified_name


def tag_event(event: Dict[str, Any], keywords: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
    """Add tags and expanded name to an event dictionary entry.

    Args:
        event: Event dictionary with at least 'name' and 'description' fields
        keywords: Optional keyword dictionary. If None, uses default.

    Returns:
        Event dictionary with 'name_expanded' and 'tags' fields added
    """
    if keywords is None:
        keywords = get_keywords()

    # Expand the name
    expanded_name = expand_name(event['name'])
    event['name_expanded'] = expanded_name

    # Extract tags from both description and expanded name
    tag_from_description = extract_tags(event.get('description', ''), keywords)
    tag_from_name = extract_tags(expanded_name, keywords)

    # Combine, deduplicate, and filter None values before sorting
    all_tags = tag_from_description + tag_from_name
    event['tags'] = sorted([tag for tag in set(all_tags) if tag is not None])

    return event


def tag_dictionary(
    events: List[Dict[str, Any]],
    tag_files: Optional[List[str]] = None
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Tag all events in a dictionary.

    Args:
        events: List of event dictionaries
        tag_files: Optional list of tag file paths to use

    Returns:
        Tuple of (tagged_events, untagged_events)
    """
    # Load keywords once for all events
    keywords = get_keywords(tag_files)

    tagged_events = []
    untagged_events = []

    for event in events:
        tagged_event = tag_event(event, keywords)
        tagged_events.append(tagged_event)

        # Track events with no tags
        if not tagged_event['tags']:
            untagged_events.append(tagged_event)

    return tagged_events, untagged_events
