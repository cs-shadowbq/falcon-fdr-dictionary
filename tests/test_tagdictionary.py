"""Tests for tagging functionality."""

from falcon_fdr_dictionary.tagging import extract_tags, expand_name, tag_event


def test_extract_tags_file():
    """Test 1: Matching 'file' tag."""
    description = "This is a file operation."
    tags = extract_tags(description)
    assert 'file' in tags


def test_extract_tags_pe():
    """Test 2: Matching 'pe' tag."""
    description = "The program is a portable executable."
    tags = extract_tags(description)
    assert 'pe' in tags


def test_extract_tags_process_not_pe():
    """Test 3: Matching 'process' and not 'pe' from 'prepared'."""
    description = "A new prepared process was started."
    tags = extract_tags(description)
    assert 'process' in tags
    assert 'pe' not in tags


def test_extract_tags_multiple():
    """Test 4: Matching multiple tags."""
    description = "The file was renamed and a new process started."
    tags = extract_tags(description)
    assert 'file' in tags
    assert 'process' in tags


def test_expand_name():
    """Test name expansion from CamelCase."""
    assert expand_name("ProcessRollup") == "Process Rollup"
    assert expand_name("DnsRequest") == "Dns Request"
    assert expand_name("HTTPConnection") == "HTTP Connection"


def test_tag_event():
    """Test complete event tagging."""
    event = {
        'id': '12345',
        'name': 'ProcessRollup',
        'description': 'Process execution event',
        'platform': 'windows'
    }

    tagged = tag_event(event)

    assert 'name_expanded' in tagged
    assert tagged['name_expanded'] == 'Process Rollup'
    assert 'tags' in tagged
    assert 'process' in tagged['tags']


def test_extract_tag5():
    # Test 5: Matching mobile tag (and info from 'enabled')
    description = "Safety Net Compatibility is enabled."
    tags = extract_tags(description)
    assert 'mobile' in tags
    # Note: 'enabled' may also match 'info' tag depending on keywords

# code.interact(local=dict(globals(), **locals()))
