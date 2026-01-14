"""Simple test runner that bypasses problematic pytest plugins."""
import sys
import os

# Try to mock fcntl for Windows compatibility before any imports
try:
    import fcntl
except ImportError:
    # Create a mock fcntl module for Windows
    import types
    fcntl = types.ModuleType('fcntl')
    sys.modules['fcntl'] = fcntl

# Disable problematic plugin after mocking fcntl
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

if __name__ == '__main__':
    import pytest
    import pytest_asyncio
    # Run tests with minimal plugins, but keep pytest-asyncio
    args = sys.argv[1:] if len(sys.argv) > 1 else ['tests/']
    sys.exit(pytest.main([
        *args,
        '-v',
        '--tb=short',
        '-p', 'no:pytest_homeassistant_custom_component',
        '-p', 'no:faulthandler',
        '-p', 'pytest_asyncio',  # Explicitly enable pytest-asyncio
    ], plugins=[pytest_asyncio.plugin]))
