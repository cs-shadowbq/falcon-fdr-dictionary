"""Configuration management for Falcon FDR Dictionary."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration settings for Falcon FDR Dictionary."""

    # CrowdStrike API credentials
    falcon_client_id: str
    falcon_client_secret: str
    falcon_client_cloud: str = "auto"

    # Output settings
    output_dir: str = "./docs"
    default_output_file: str = "fdr-event-dictionary.json"

    # Tag file settings
    tag_files: Optional[list] = None  # List of tag file paths, None = use default

    # Logging
    log_level: str = "INFO"
    log_file: str = "falcon_fdr_dictionary.log"

    # Banner display
    show_banner: bool = True

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file (default: .env in current directory)

        Returns:
            Config instance with values from environment

        Raises:
            ValueError: If required credentials are missing
        """
        # Load .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Use FALCON_ prefix for API credentials
        env_prefix = "FALCON_"
        client_id = os.getenv(f"{env_prefix}CLIENT_ID")
        client_secret = os.getenv(f"{env_prefix}CLIENT_SECRET")

        # Validate required credentials
        if not client_id or not client_secret:
            raise ValueError(
                "Missing required CrowdStrike API credentials. "
                f"Please set {env_prefix}CLIENT_ID and {env_prefix}CLIENT_SECRET"
            )

        return cls(
            falcon_client_id=client_id,
            falcon_client_secret=client_secret,
            falcon_client_cloud=os.getenv(f"{env_prefix}CLIENT_CLOUD", "auto"),
            output_dir=os.getenv("OUTPUT_DIR", "./docs"),
            default_output_file=os.getenv("DEFAULT_OUTPUT_FILE", "fdr-event-dictionary.json"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "falcon_fdr_dictionary.log"),
            show_banner=os.getenv("SHOW_BANNER", "true").lower() in ["true", "1", "yes"],
            tag_files=cls._parse_tag_files(os.getenv("TAG_FILES")),
        )

    @staticmethod
    def _parse_tag_files(tag_files_str: Optional[str]) -> Optional[list]:
        """Parse TAG_FILES environment variable.

        Args:
            tag_files_str: Comma-separated list of tag file paths

        Returns:
            List of tag file paths or None
        """
        if not tag_files_str:
            return None

        # Split by comma and strip whitespace
        files = [f.strip() for f in tag_files_str.split(",") if f.strip()]
        return files if files else None

    def validate_cloud_region(self) -> bool:
        """Validate that the cloud region is supported.

        Returns:
            True if valid, False otherwise
        """
        valid_regions = ['auto', 'us1', 'us2', 'eu1', 'usgov1', 'usgov2']
        return self.falcon_client_cloud in valid_regions


def get_config(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    cloud: Optional[str] = None,
) -> Config:
    """Get configuration, with optional CLI overrides.

    Args:
        client_id: Override for client ID
        client_secret: Override for client secret
        cloud: Override for cloud region

    Returns:
        Config instance with CLI overrides applied
    """
    config = Config.from_env()

    # Apply CLI overrides
    if client_id:
        config.falcon_client_id = client_id
    if client_secret:
        config.falcon_client_secret = client_secret
    if cloud:
        config.falcon_client_cloud = cloud

    return config
