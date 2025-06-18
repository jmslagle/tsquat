import pytest
import responses
from unittest.mock import Mock, patch
import hashlib
import sys
import os

# Add the parent directory to sys.path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.opensrs_client import OpenSRSClient

class TestOpenSRSClient:
    
    def setup_method(self):
        """Setup method run before each test"""
        self.api_key = "test_api_key_12345"
        self.username = "test_user"
        self.test_host = "https://horizon.opensrs.net:55443"
        self.live_host = "https://rr-n1-tor.opensrs.net:55443"
        
        self.client = OpenSRSClient(
            api_key=self.api_key,
            username=self.username,
            host=self.test_host,
            use_test=True
        )
    
    def test_client_initialization(self):
        """Test that the client initializes correctly"""
        assert self.client.api_key == self.api_key
        assert self.client.username == self.username
        assert self.client.host == self.test_host
        assert self.client.use_test == True
        assert self.client.session.headers['X-Username'] == self.username
        assert self.client.session.headers['Content-Type'] == 'text/xml'
    
    def test_generate_signature(self):
        """Test 2-step MD5 signature generation"""
        xml_data = "<?xml version='1.0'?><test>data</test>"
        # Step 1: MD5 of (XML + API_KEY)
        step1 = hashlib.md5((xml_data + self.api_key).encode()).hexdigest()
        # Step 2: MD5 of (Step1_result + API_KEY)
        expected_signature = hashlib.md5((step1 + self.api_key).encode()).hexdigest()
        
        signature = self.client._generate_signature(xml_data)
        assert signature == expected_signature
    
    def test_build_xml_request(self):
        """Test XML request building"""
        action = "get"
        object_type = "domain"
        attributes = '<item key="domain">test.com</item>'
        
        xml_request = self.client._build_xml_request(action, object_type, attributes)
        
        # Check that the XML contains the expected elements
        assert '<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'no\' ?>' in xml_request
        assert '<item key="action">get</item>' in xml_request
        assert '<item key="object">domain</item>' in xml_request
        assert '<item key="domain">test.com</item>' in xml_request
    
    @responses.activate
    def test_successful_domain_check_available(self):
        """Test successful domain availability check - domain available"""
        domain = "test-available-domain.com"
        
        # Mock successful response indicating domain is available
        mock_response = """<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <header>
        <version>0.9</version>
    </header>
    <body>
        <data_block>
            <dt_assoc>
                <item key="is_success">1</item>
                <item key="response_text">Command successful</item>
                <item key="attributes">
                    <dt_assoc>
                        <item key="status">available</item>
                    </dt_assoc>
                </item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>"""
        
        responses.add(
            responses.POST,
            f"{self.test_host}/",
            body=mock_response,
            status=200,
            content_type='text/xml'
        )
        
        result = self.client.check_domain_availability(domain)
        
        assert result['domain'] == domain
        assert result['available'] == True
        assert result['status'] == 'available'
    
    @responses.activate
    def test_successful_domain_check_registered(self):
        """Test successful domain availability check - domain registered"""
        domain = "test-registered-domain.com"
        
        # Mock successful response indicating domain is registered
        mock_response = """<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <header>
        <version>0.9</version>
    </header>
    <body>
        <data_block>
            <dt_assoc>
                <item key="is_success">1</item>
                <item key="response_text">Command successful</item>
                <item key="attributes">
                    <dt_assoc>
                        <item key="status">registered</item>
                    </dt_assoc>
                </item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>"""
        
        responses.add(
            responses.POST,
            f"{self.test_host}/",
            body=mock_response,
            status=200,
            content_type='text/xml'
        )
        
        result = self.client.check_domain_availability(domain)
        
        assert result['domain'] == domain
        assert result['available'] == False
        assert result['status'] == 'registered'
    
    @responses.activate
    def test_api_error_response(self):
        """Test handling of API error responses"""
        domain = "test-error-domain.com"
        
        # Mock API error response
        mock_response = """<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <header>
        <version>0.9</version>
    </header>
    <body>
        <data_block>
            <dt_assoc>
                <item key="is_success">0</item>
                <item key="response_code">465</item>
                <item key="response_text">Authentication failed</item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>"""
        
        responses.add(
            responses.POST,
            f"{self.test_host}/",
            body=mock_response,
            status=200,
            content_type='text/xml'
        )
        
        result = self.client.check_domain_availability(domain)
        
        assert result['domain'] == domain
        assert result['available'] == False
        assert result['status'] == 'error'
        assert 'error' in result
    
    @responses.activate
    def test_http_error_response(self):
        """Test handling of HTTP errors"""
        domain = "test-http-error-domain.com"
        
        # Mock HTTP 500 error
        responses.add(
            responses.POST,
            f"{self.test_host}/",
            body="Internal Server Error",
            status=500,
            content_type='text/html'
        )
        
        result = self.client.check_domain_availability(domain)
        
        assert result['domain'] == domain
        assert result['available'] == False
        assert result['status'] == 'error'
        assert 'error' in result
    
    @responses.activate
    def test_network_timeout(self):
        """Test handling of network timeouts"""
        domain = "test-timeout-domain.com"
        
        # Mock timeout by not adding any response
        # This will cause a ConnectionError
        
        result = self.client.check_domain_availability(domain)
        
        assert result['domain'] == domain
        assert result['available'] == False
        assert result['status'] == 'error'
        assert 'error' in result
    
    @responses.activate
    def test_authentication_headers(self):
        """Test that authentication headers are set correctly"""
        domain = "test-auth-domain.com"
        
        mock_response = """<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <body>
        <data_block>
            <dt_assoc>
                <item key="is_success">1</item>
                <item key="attributes">
                    <dt_assoc>
                        <item key="status">available</item>
                    </dt_assoc>
                </item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>"""
        
        responses.add(
            responses.POST,
            f"{self.test_host}/",
            body=mock_response,
            status=200,
            content_type='text/xml'
        )
        
        self.client.check_domain_availability(domain)
        
        # Check that the request was made with correct headers
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        
        assert request.headers['X-Username'] == self.username
        assert 'X-Signature' in request.headers
        assert request.headers['Content-Type'] == 'text/xml'
        
        # Verify signature is a valid MD5 hash (32 hex characters)
        signature = request.headers['X-Signature']
        assert len(signature) == 32
        assert all(c in '0123456789abcdef' for c in signature.lower())
    
    def test_bulk_check_availability(self):
        """Test bulk domain availability checking"""
        domains = ["test1.com", "test2.com", "test3.com"]
        
        # Mock the individual check method
        with patch.object(self.client, 'check_domain_availability') as mock_check:
            mock_check.side_effect = [
                {'domain': 'test1.com', 'available': True, 'status': 'available'},
                {'domain': 'test2.com', 'available': False, 'status': 'registered'},
                {'domain': 'test3.com', 'available': False, 'status': 'error', 'error': 'API error'}
            ]
            
            results = self.client.bulk_check_availability(domains, batch_size=2)
            
            assert len(results) == 3
            assert mock_check.call_count == 3
            
            # Check individual results
            assert results[0]['available'] == True
            assert results[1]['available'] == False
            assert results[2]['status'] == 'error'
    
    @responses.activate
    def test_validate_credentials_success(self):
        """Test successful credential validation"""
        mock_response = """<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <body>
        <data_block>
            <dt_assoc>
                <item key="is_success">1</item>
                <item key="attributes">
                    <dt_assoc>
                        <item key="status">available</item>
                    </dt_assoc>
                </item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>"""
        
        responses.add(
            responses.POST,
            f"{self.test_host}/",
            body=mock_response,
            status=200,
            content_type='text/xml'
        )
        
        assert self.client.validate_credentials() == True
    
    @responses.activate
    def test_validate_credentials_failure(self):
        """Test failed credential validation"""
        mock_response = """<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <body>
        <data_block>
            <dt_assoc>
                <item key="is_success">0</item>
                <item key="response_code">465</item>
                <item key="response_text">Authentication failed</item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>"""
        
        responses.add(
            responses.POST,
            f"{self.test_host}/",
            body=mock_response,
            status=200,
            content_type='text/xml'
        )
        
        assert self.client.validate_credentials() == False
    
    def test_register_domain_test_mode(self):
        """Test domain registration in test mode"""
        domain = "test-register.com"
        contact_info = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '555-1234',
            'address1': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'country': 'US',
            'postal_code': '12345'
        }
        
        result = self.client.register_domain(domain, contact_info)
        
        assert result['domain'] == domain
        assert result['status'] == 'test_success'
        assert 'Test registration successful' in result['message']
    
    @responses.activate
    def test_register_domain_production_success(self):
        """Test successful domain registration in production mode"""
        # Create production client
        prod_client = OpenSRSClient(
            api_key=self.api_key,
            username=self.username,
            host=self.live_host,
            use_test=False
        )
        
        domain = "test-register-prod.com"
        contact_info = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '555-1234',
            'address1': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'country': 'US',
            'postal_code': '12345'
        }
        
        mock_response = """<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <body>
        <data_block>
            <dt_assoc>
                <item key="is_success">1</item>
                <item key="response_text">Command successful</item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>"""
        
        responses.add(
            responses.POST,
            f"{self.live_host}/",
            body=mock_response,
            status=200,
            content_type='text/xml'
        )
        
        result = prod_client.register_domain(domain, contact_info)
        
        assert result['domain'] == domain
        assert result['status'] == 'success'
        assert 'successfully' in result['message']


class TestOpenSRSClientEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        self.client = OpenSRSClient(
            api_key="edge_test_key",
            username="edge_user",
            host="https://test.example.com",
            use_test=True
        )
    
    def test_empty_domain(self):
        """Test handling of empty domain"""
        result = self.client.check_domain_availability("")
        assert result['available'] == False
        assert result['status'] == 'error'
    
    def test_invalid_domain_format(self):
        """Test handling of invalid domain format"""
        invalid_domains = [
            "not-a-domain",
            "domain..com",
            "domain-.com",
            "-domain.com"
        ]
        
        for domain in invalid_domains:
            result = self.client.check_domain_availability(domain)
            # The API should handle invalid domains, but they shouldn't crash
            assert 'domain' in result
            assert 'available' in result
    
    def test_host_url_normalization(self):
        """Test that host URLs are normalized correctly"""
        # Test with trailing slash
        client1 = OpenSRSClient("key", "user", "https://example.com/", True)
        assert client1.host == "https://example.com"
        
        # Test without trailing slash
        client2 = OpenSRSClient("key", "user", "https://example.com", True)
        assert client2.host == "https://example.com"
    
    @responses.activate
    def test_malformed_xml_response(self):
        """Test handling of malformed XML responses"""
        domain = "test-malformed.com"
        
        # Mock malformed XML response
        responses.add(
            responses.POST,
            f"{self.client.host}/",
            body="This is not XML",
            status=200,
            content_type='text/xml'
        )
        
        result = self.client.check_domain_availability(domain)
        
        assert result['domain'] == domain
        assert result['available'] == False
        assert result['status'] == 'error'
    
    @responses.activate
    def test_empty_response(self):
        """Test handling of empty responses"""
        domain = "test-empty.com"
        
        responses.add(
            responses.POST,
            f"{self.client.host}/",
            body="",
            status=200,
            content_type='text/xml'
        )
        
        result = self.client.check_domain_availability(domain)
        
        assert result['domain'] == domain
        assert result['available'] == False
        assert result['status'] == 'error'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])