"""Fixtures for testing."""
import pytest


@pytest.fixture(scope="session")
def dummy_fixture(request):
    """Docstring.

    Parameters:
        request [object]:
            pytest request.
    """
    pass
