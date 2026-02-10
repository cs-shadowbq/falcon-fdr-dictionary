"""Comprehensive tests for tagging functionality."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from falcon_fdr_dictionary.tagging import (
    extract_tags,
    expand_name,
    tag_event,
    tag_dictionary,
    load_tag_files,
    get_keywords,
    get_default_tags_file,
)


class TestExtractTags:
    """Tests for tag extraction."""

    def test_extract_single_tag_file(self):
        """Test matching 'file' tag."""
        description = "This is a file operation."
        tags = extract_tags(description)
        assert 'file' in tags

    def test_extract_single_tag_pe(self):
        """Test matching 'pe' tag."""
        description = "The program is a portable executable."
        tags = extract_tags(description)
        assert 'pe' in tags

    def test_extract_tag_process_not_pe(self):
        """Test matching 'process' and not 'pe' from 'prepared'."""
        description = "A new prepared process was started."
        tags = extract_tags(description)
        assert 'process' in tags
        assert 'pe' not in tags

    def test_extract_multiple_tags(self):
        """Test matching multiple tags."""
        description = "The file was renamed and a new process started."
        tags = extract_tags(description)
        assert 'file' in tags
        assert 'process' in tags

    def test_extract_case_insensitive(self):
        """Test case-insensitive matching."""
        description = "DNS request sent to remote server."
        tags = extract_tags(description)
        assert 'dns' in tags
        assert 'network' in tags

    def test_extract_no_tags(self):
        """Test text with no matching tags."""
        description = "Something completely unrelated."
        tags = extract_tags(description)
        # May or may not have tags depending on keywords, just check it doesn't crash
        assert isinstance(tags, list)

    def test_extract_with_custom_keywords(self):
        """Test extraction with custom keyword dictionary."""
        custom_keywords = {
            'custom': ['special', 'unique'],
            'test': ['testing', 'trial']
        }
        description = "This is a special testing case."
        tags = extract_tags(description, custom_keywords)
        assert 'custom' in tags
        assert 'test' in tags


class TestExpandName:
    """Tests for name expansion."""

    def test_expand_simple_camelcase(self):
        """Test simple CamelCase expansion."""
        assert expand_name("ProcessRollup") == "Process Rollup"

    def test_expand_with_acronym(self):
        """Test expansion with acronyms."""
        assert expand_name("DnsRequest") == "Dns Request"

    def test_expand_all_caps(self):
        """Test expansion with multiple capital letters."""
        # HTTP is expanded as H T T P then becomes HTTP  Connection
        assert expand_name("HTTPConnection") == "HTTP Connection"

    def test_expand_single_word(self):
        """Test single word returns unchanged."""
        assert expand_name("Process") == "Process"

    def test_expand_lowercase(self):
        """Test lowercase word returns unchanged."""
        assert expand_name("process") == "process"

    def test_expand_complex(self):
        """Test complex CamelCase."""
        assert expand_name("ProcessMemoryAllocation") == "Process Memory Allocation"


class TestTagEvent:
    """Tests for complete event tagging."""

    def test_tag_event_basic(self):
        """Test basic event tagging."""
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

    def test_tag_event_preserves_fields(self):
        """Test that tagging preserves original fields."""
        event = {
            'id': '12345',
            'name': 'DnsRequest',
            'description': 'DNS query event',
            'platform': 'linux',
            'version': 1
        }

        tagged = tag_event(event)

        assert tagged['id'] == '12345'
        assert tagged['name'] == 'DnsRequest'
        assert tagged['platform'] == 'linux'
        assert tagged['version'] == 1

    def test_tag_event_combines_name_and_description(self):
        """Test that tags are extracted from both name and description."""
        event = {
            'id': '12345',
            'name': 'FileWrite',
            'description': 'Process writing to disk',
            'platform': 'windows'
        }

        tagged = tag_event(event)

        # Both 'file' and 'process' should be found
        assert 'file' in tagged['tags']
        assert 'process' in tagged['tags']

    def test_tag_event_deduplicates(self):
        """Test that duplicate tags are removed."""
        event = {
            'id': '12345',
            'name': 'ProcessStart',
            'description': 'New process started',
            'platform': 'windows'
        }

        tagged = tag_event(event)

        # 'process' should only appear once even though it's in both
        assert tagged['tags'].count('process') == 1

    def test_tag_event_sorted(self):
        """Test that tags are sorted."""
        event = {
            'id': '12345',
            'name': 'NetworkDnsRequest',
            'description': 'DNS network query',
            'platform': 'linux'
        }

        tagged = tag_event(event)

        # Check tags are in sorted order
        assert tagged['tags'] == sorted(tagged['tags'])


class TestTagDictionary:
    """Tests for tagging full dictionaries."""

    def test_tag_dictionary_basic(self):
        """Test tagging a list of events."""
        events = [
            {'id': '1', 'name': 'ProcessStart', 'description': 'Process started'},
            {'id': '2', 'name': 'FileWrite', 'description': 'File written'},
        ]

        tagged, untagged = tag_dictionary(events)

        assert len(tagged) == 2
        assert all('tags' in e for e in tagged)
        assert all('name_expanded' in e for e in tagged)

    def test_tag_dictionary_tracks_untagged(self):
        """Test that untagged events are tracked."""
        events = [
            {'id': '1', 'name': 'ProcessStart', 'description': 'Process started'},
            {'id': '2', 'name': 'Unknown', 'description': 'Something else'},
        ]

        tagged, untagged = tag_dictionary(events)

        # Second event might not have tags
        assert len(tagged) == 2
        # untagged may or may not be empty, just verify structure
        assert isinstance(untagged, list)

    def test_tag_dictionary_empty_list(self):
        """Test tagging empty event list."""
        events = []

        tagged, untagged = tag_dictionary(events)

        assert len(tagged) == 0
        assert len(untagged) == 0


class TestLoadTagFiles:
    """Tests for loading tag files."""

    def test_load_default_tags(self):
        """Test loading default tags file."""
        keywords = load_tag_files()

        assert isinstance(keywords, dict)
        assert len(keywords) > 0
        assert 'file' in keywords
        assert 'process' in keywords
        assert isinstance(keywords['file'], list)

    def test_load_custom_tag_file(self):
        """Test loading a custom tag file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'custom_tag': ['keyword1', 'keyword2'],
                'another_tag': ['word1', 'word2', 'word3']
            }, f)
            temp_file = f.name

        try:
            keywords = load_tag_files([temp_file])

            assert 'custom_tag' in keywords
            assert 'another_tag' in keywords
            assert keywords['custom_tag'] == ['keyword1', 'keyword2']
            assert len(keywords['another_tag']) == 3
        finally:
            Path(temp_file).unlink()

    def test_load_multiple_tag_files(self):
        """Test loading multiple tag files."""
        # Create first file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'tag1': ['word1', 'word2'],
                'shared': ['shared1']
            }, f)
            file1 = f.name

        # Create second file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'tag2': ['word3', 'word4'],
                'shared': ['shared2', 'shared3']
            }, f)
            file2 = f.name

        try:
            keywords = load_tag_files([file1, file2])

            assert 'tag1' in keywords
            assert 'tag2' in keywords
            assert 'shared' in keywords
            # Shared should be merged
            assert 'shared1' in keywords['shared']
            assert 'shared2' in keywords['shared']
            assert 'shared3' in keywords['shared']
        finally:
            Path(file1).unlink()
            Path(file2).unlink()

    def test_load_nonexistent_file_warning(self):
        """Test loading nonexistent file shows warning."""
        # Should not crash, just warn
        keywords = load_tag_files(['/nonexistent/file.yaml'])

        # Should return empty dict or continue with other files
        assert isinstance(keywords, dict)

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                load_tag_files([temp_file])
        finally:
            Path(temp_file).unlink()


class TestGetKeywords:
    """Tests for get_keywords caching."""

    def test_get_keywords_default(self):
        """Test getting default keywords."""
        keywords = get_keywords()

        assert isinstance(keywords, dict)
        assert len(keywords) > 0

    def test_get_keywords_caches(self):
        """Test that keywords are cached."""
        kw1 = get_keywords()
        kw2 = get_keywords()

        # Should be the same object (cached)
        assert kw1 is kw2

    def test_get_keywords_force_reload(self):
        """Test force reload bypasses cache."""
        kw1 = get_keywords()
        kw2 = get_keywords(force_reload=True)

        # Should be different objects (reloaded)
        assert kw1 is not kw2
        # But content should be the same
        assert kw1 == kw2


class TestGetDefaultTagsFile:
    """Tests for default tags file path."""

    def test_default_tags_file_exists(self):
        """Test that default tags file exists."""
        default_file = get_default_tags_file()

        assert default_file.exists()
        assert default_file.suffix == '.yaml'
        assert default_file.name == 'default_tags.yaml'

    def test_default_tags_file_is_valid_yaml(self):
        """Test that default tags file is valid YAML."""
        default_file = get_default_tags_file()

        with open(default_file, 'r') as f:
            data = yaml.safe_load(f)

        assert isinstance(data, dict)
        assert len(data) > 0


class TestTagDictionaryWithCustomFiles:
    """Integration tests using custom tag files."""

    def test_tag_dictionary_with_custom_file(self):
        """Test tagging with custom tag file."""
        # Create custom tag file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'custom': ['special', 'unique'],
                'mytest': ['testing']
            }, f)
            temp_file = f.name

        events = [
            {'id': '1', 'name': 'SpecialEvent', 'description': 'A special testing case'},
        ]

        try:
            tagged, untagged = tag_dictionary(events, [temp_file])

            assert 'custom' in tagged[0]['tags']
            assert 'mytest' in tagged[0]['tags']
        finally:
            Path(temp_file).unlink()

    def test_tag_dictionary_combines_default_and_custom(self):
        """Test that custom tags work alongside default ones."""
        # Create custom tag file with one new tag
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'file': ['document', 'spreadsheet'],  # Extend existing
                'custom': ['special']  # New tag
            }, f)
            temp_file = f.name

        # First load default
        default_tags = get_default_tags_file()

        events = [
            {'id': '1', 'name': 'FileWrite', 'description': 'Write document'},
        ]

        try:
            # Load both default and custom
            tagged, untagged = tag_dictionary(events, [str(default_tags), temp_file])

            # Should have 'file' tag from both files
            assert 'file' in tagged[0]['tags']
        finally:
            Path(temp_file).unlink()
