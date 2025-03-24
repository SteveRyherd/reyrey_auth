import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

# Import package functions
from reyrey_auth import (
    configure,
    get_token,
    save_token,
    check_token_validity,
    get_auth_headers
)
from reyrey_auth.providers import EnvFileProvider, JsonFileProvider

class TestProviders:
    """Test token provider functionality"""
    
    def test_env_file_provider(self):
        """Test environment file provider"""
        # Create a temporary directory and file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure to use the temp directory
            env_file = os.path.join(temp_dir, '.env')
            
            # Create test provider
            provider = EnvFileProvider()
            
            # Test saving token
            with patch('reyrey_auth.providers.env_file.os.path.exists', return_value=False):
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # Call save_token
                    result = provider.save_token('test_token', 'TEST', 'example.com')
                    
                    # Check result
                    assert result is True
                    mock_file.write.assert_called_with('REYREY_TOKEN_TEST=test_token\n')
    
    def test_json_file_provider(self):
        """Test JSON file provider"""
        # Create a temporary directory and file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure to use the temp directory
            json_file = os.path.join(temp_dir, 'token.json')
            
            # Create test provider
            provider = JsonFileProvider(filename=json_file)
            
            # Test saving token
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                # Call save_token
                result = provider.save_token('test_token', 'TEST', 'example.com')
                
                # Check result
                assert result is True
                mock_file.write.assert_called()

class TestTokenValidation:
    """Test token validation functionality"""
    
    def test_check_token_validity(self):
        """Test token validation"""
        # Mock requests.post
        with patch('requests.post') as mock_post:
            # Configure the mock
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {'tokenexpiry': '2023-12-31T23:59:59Z'}
            mock_post.return_value = mock_response
            
            # Call check_token_validity
            result = check_token_validity('test_token')
            
            # Check result
            assert result is True
            
            # Test invalid response
            mock_response.status_code = 401
            result = check_token_validity('test_token')
            assert result is False

class TestTokenManagement:
    """Test token management functions"""
    
    def test_get_token_from_providers(self):
        """Test getting token from providers"""
        # Mock get_provider
        with patch('reyrey_auth.auth.get_provider') as mock_get_provider:
            # Create mock provider
            mock_provider = MagicMock()
            mock_provider.get_token.return_value = 'test_token'
            mock_get_provider.return_value = mock_provider
            
            # Mock check_token_validity
            with patch('reyrey_auth.auth.check_token_validity', return_value=True):
                # Call get_token
                token = get_token(providers=['env_file'])
                
                # Check result
                assert token == 'test_token'
    
    def test_save_token_to_providers(self):
        """Test saving token to providers"""
        # Mock get_provider
        with patch('reyrey_auth.auth.get_provider') as mock_get_provider:
            # Create mock provider
            mock_provider = MagicMock()
            mock_provider.save_token.return_value = True
            mock_get_provider.return_value = mock_provider
            
            # Call save_token
            result = save_token('test_token', providers=['env_file'])
            
            # Check result
            assert result is True
            mock_provider.save_token.assert_called_with('test_token', 'DRT', 'focus.dealer.reyrey.net')

class TestAuthHelpers:
    """Test authentication helper functions"""
    
    def test_get_auth_headers(self):
        """Test getting authentication headers"""
        # Mock get_token
        with patch('reyrey_auth.auth.get_token', return_value='test_token'):
            # Call get_auth_headers
            headers = get_auth_headers()
            
            # Check result
            assert headers is not None
            assert headers['Token'] == 'test_token'
            assert headers['Content-Type'] == 'application/json;charset=utf-8'
            
            # Test failure case
            with patch('reyrey_auth.auth.get_token', return_value=None):
                headers = get_auth_headers()
                assert headers is None

if __name__ == '__main__':
    pytest.main(['-v', 'test_auth.py'])
