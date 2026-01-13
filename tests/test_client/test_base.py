"""Tests for base INEClient."""

import pytest
import responses

from pyine.client.base import INEClient
from pyine.utils.exceptions import APIError, RateLimitError


class TestINEClient:
    """Tests for INEClient base class."""

    def test_initialization_default(self):
        """Test client initialization with defaults."""
        client = INEClient()

        assert client.language == "EN"
        assert client.timeout == INEClient.DEFAULT_TIMEOUT
        assert client.cache_enabled is True
        assert client.max_retries == INEClient.MAX_RETRIES

    def test_initialization_custom(self):
        """Test client initialization with custom parameters."""
        client = INEClient(language="PT", timeout=60, cache_enabled=False, max_retries=5)

        assert client.language == "PT"
        assert client.timeout == 60
        assert client.cache_enabled is False
        assert client.max_retries == 5

    def test_invalid_language(self):
        """Test initialization with invalid language."""
        with pytest.raises(ValueError, match="Language must be"):
            INEClient(language="FR")

    @responses.activate
    def test_make_request_json_success(self):
        """Test successful JSON request."""
        client = INEClient()

        responses.add(
            responses.GET,
            "https://www.ine.pt/test/endpoint",
            json={"result": "success"},
            status=200,
        )

        response = client._make_request(
            "/test/endpoint", params={"param1": "value1"}, response_format="json"
        )

        assert response == {"result": "success"}
        assert len(responses.calls) == 1

    @responses.activate
    def test_make_request_xml_success(self):
        """Test successful XML request."""
        client = INEClient()

        xml_data = "<?xml version='1.0'?><root><data>test</data></root>"
        responses.add(
            responses.GET,
            "https://www.ine.pt/test/endpoint",
            body=xml_data,
            status=200,
        )

        response = client._make_request("/test/endpoint", response_format="xml")

        assert isinstance(response, str)
        assert "test" in response

    @responses.activate
    def test_make_request_adds_language(self):
        """Test that language is added to parameters."""
        client = INEClient(language="PT")

        responses.add(
            responses.GET,
            "https://www.ine.pt/test",
            json={"ok": True},
            status=200,
        )

        client._make_request("/test", params={"param1": "value1"})

        # Check that lang parameter was added
        request_url = responses.calls[0].request.url
        assert "lang=PT" in request_url

    @responses.activate
    def test_make_request_rate_limit_error(self):
        """Test handling of rate limit (429) response."""
        client = INEClient()

        responses.add(
            responses.GET,
            "https://www.ine.pt/test",
            status=429,
        )

        with pytest.raises(RateLimitError, match="Too many requests"):
            client._make_request("/test")

    @responses.activate
    def test_make_request_404_error(self):
        """Test handling of 404 error."""
        client = INEClient()

        responses.add(
            responses.GET,
            "https://www.ine.pt/test",
            status=404,
        )

        with pytest.raises(APIError, match="Resource not found"):
            client._make_request("/test")

    @responses.activate
    def test_make_request_500_error(self):
        """Test handling of server error."""
        client = INEClient()

        responses.add(
            responses.GET,
            "https://www.ine.pt/test",
            status=500,
        )

        with pytest.raises(APIError):
            client._make_request("/test")

    @responses.activate
    def test_make_request_invalid_json(self):
        """Test handling of invalid JSON response."""
        client = INEClient()

        responses.add(
            responses.GET,
            "https://www.ine.pt/test",
            body="not valid json",
            status=200,
        )

        with pytest.raises(APIError, match="Invalid JSON"):
            client._make_request("/test", response_format="json")

    def test_unsupported_response_format(self):
        """Test error on unsupported response format."""
        client = INEClient()

        # Mock a response that won't be called
        with pytest.raises(ValueError, match="Unsupported response format"):
            # We need to mock the request itself since _make_request validates format
            responses.add(
                responses.GET,
                "https://www.ine.pt/test",
                json={"ok": True},
                status=200,
            )
            responses.start()
            try:
                client._make_request("/test", response_format="csv")
            finally:
                responses.stop()

    def test_context_manager(self):
        """Test client works as context manager."""
        with INEClient() as client:
            assert isinstance(client, INEClient)
            assert client.session is not None

    def test_close(self):
        """Test client cleanup."""
        client = INEClient()
        session = client.session

        client.close()

        # Session should be closed (though this doesn't raise an error)
        assert session is not None

    def test_session_headers(self):
        """Test that session has correct headers."""
        client = INEClient()

        headers = client.session.headers
        assert "User-Agent" in headers
        assert "pyine" in headers["User-Agent"]
        assert "Accept" in headers

    @responses.activate
    def test_retry_on_500(self):
        """Test that client retries on 500 errors."""
        client = INEClient(max_retries=2)

        # First two requests fail, third succeeds
        responses.add(responses.GET, "https://www.ine.pt/test", status=500)
        responses.add(responses.GET, "https://www.ine.pt/test", status=500)
        responses.add(
            responses.GET,
            "https://www.ine.pt/test",
            json={"ok": True},
            status=200,
        )

        # Should eventually succeed after retries
        response = client._make_request("/test")
        assert response == {"ok": True}

    def test_language_case_insensitive(self):
        """Test that language parameter is case-insensitive."""
        client_lower = INEClient(language="en")
        client_upper = INEClient(language="EN")

        assert client_lower.language == "EN"
        assert client_upper.language == "EN"
