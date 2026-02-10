"""Core API client for CrowdStrike Falcon FDR."""

import json
import sys
from typing import Dict, Any, Optional, List
import requests
from falconpy import APIHarness
from rich.console import Console

console = Console()


class FDRClient:
    """Client for interacting with CrowdStrike FDR API."""

    def __init__(self, client_id: str, client_secret: str, base_url: str = "auto"):
        """Initialize FDR API client.

        Args:
            client_id: CrowdStrike API client ID
            client_secret: CrowdStrike API client secret
            base_url: CrowdStrike base URL (default: auto)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.falcon = None
        self.token = None
        self.session = None

    def authenticate(self) -> bool:
        """Authenticate with CrowdStrike API.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.falcon = APIHarness(
                client_id=self.client_id,
                client_secret=self.client_secret,
                base_url=self.base_url
            )
            if self.falcon.authenticate():
                self.token = self.falcon.token
                return True
            return False
        except Exception as e:
            console.print(f"[red]Authentication error: {e}[/red]")
            return False

    def get_base_url(self) -> str:
        """Get the effective base URL.

        Returns:
            The base URL to use for API calls
        """
        if self.base_url == 'auto':
            return 'https://api.crowdstrike.com'
        return self.base_url

    def get_dictionary_page(self, limit: int = 200, offset: int = 0) -> Dict[str, Any]:
        """Retrieve a page of FDR event dictionary resources.

        Args:
            limit: Number of resources to retrieve (default: 200)
            offset: Starting offset for pagination (default: 0)

        Returns:
            Dictionary containing resources and pagination metadata
        """
        headers = {
            "accept": "application/json",
            "authorization": f"bearer {self.token}",
        }

        base = self.get_base_url()
        url = f'{base}/fdr/queries/schema-events/v1?limit={limit}&offset={offset}'

        try:
            response = self._request(url, 'GET', headers=headers)
            if response.status_code in [200, 201]:
                content = json.loads(response.content.decode("utf-8"))
                content['status_code'] = response.status_code
                return content
            else:
                return self._zero_resource(response)
        except Exception as e:
            console.print(f"[red]Error fetching dictionary page: {e}[/red]")
            return {'status_code': 500, 'resources': [], 'errors': [str(e)]}

    def get_dictionary_item(self, event_id: str) -> Dict[str, Any]:
        """Retrieve a specific FDR event dictionary item.

        Args:
            event_id: The event ID to retrieve

        Returns:
            Dictionary containing the event schema details
        """
        headers = {
            "accept": "application/json",
            "authorization": f"bearer {self.token}",
        }

        base = self.get_base_url()
        url = f'{base}/fdr/entities/schema-events/v1?ids={event_id}'

        try:
            response = self._request(url, 'GET', headers=headers)
            if response.status_code in [200, 201]:
                content = json.loads(response.content.decode("utf-8"))
                content['status_code'] = response.status_code
                return content
            else:
                return self._zero_resource(response)
        except Exception as e:
            console.print(f"[red]Error fetching dictionary item {event_id}: {e}[/red]")
            return {'status_code': 500, 'resources': [], 'errors': [str(e)]}

    def validate_credentials(self) -> tuple[bool, str]:
        """Validate that credentials work and can access FDR API.

        Returns:
            Tuple of (success, message)
        """
        # First check basic authentication
        if not self.authenticate():
            return False, "Authentication failed - invalid credentials or connection error"

        # Try to access FDR API with a minimal query
        try:
            result = self.get_dictionary_page(limit=1, offset=0)
            if result.get('status_code') in [200, 201]:
                total = result.get('meta', {}).get('pagination', {}).get('total', 0)
                return True, f"Credentials validated - FDR API accessible ({total} total events)"
            else:
                errors = result.get('errors', [])
                error_msg = errors[0] if errors else "Unknown error"
                return False, f"FDR API access failed: {error_msg}"
        except Exception as e:
            return False, f"FDR API validation error: {str(e)}"

    def _zero_resource(self, response: requests.Response) -> Dict[str, Any]:
        """Handle non-200 status codes.

        Args:
            response: The HTTP response object

        Returns:
            Dictionary with error information
        """
        try:
            content = json.loads(response.content.decode("utf-8"))
        except Exception:
            content = {}

        content['status_code'] = response.status_code
        content['resources'] = []
        if 'errors' not in content:
            content['errors'] = [f"HTTP {response.status_code}"]

        return content

    def _request(
        self,
        url: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Perform HTTP request.

        Args:
            url: The URL to request
            method: HTTP method (GET, POST, etc.)
            headers: Optional headers dictionary
            data: Optional request body
            params: Optional query parameters

        Returns:
            requests.Response object
        """
        if headers is None:
            headers = {}

        try:
            prepared = requests.Request(
                method.upper(),
                url,
                headers=headers,
                data=data,
                params=params
            ).prepare()

            if self.session is None:
                self.session = requests.Session()

            response = self.session.send(prepared)
            return response

        except KeyboardInterrupt:
            sys.exit(130)
        except Exception as e:
            console.print(f"[red]Request error: {e}[/red]")
            # Create a mock response for error handling
            mock_response = requests.Response()
            mock_response.status_code = 500
            mock_response._content = json.dumps({
                'errors': [str(e)]
            }).encode('utf-8')
            return mock_response
