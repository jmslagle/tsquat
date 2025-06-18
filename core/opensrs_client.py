import requests
import json
import hashlib
import time
import logging
from datetime import datetime

class OpenSRSClient:
    def __init__(self, api_key, username, host, use_test=True):
        self.api_key = api_key
        self.username = username
        self.host = host.rstrip('/')
        self.use_test = use_test
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        self.session.headers.update({
            'Content-Type': 'text/xml',
            'X-Username': self.username,
            'X-Signature': ''
        })
        
        self.logger.info(f"Initialized OpenSRS client for user: {self.username}")
        self.logger.info(f"Host: {self.host}")
        self.logger.info(f"Test mode: {self.use_test}")
    
    def _generate_signature(self, xml_data):
        # Step 1: MD5 of (XML + API_KEY)
        step1 = hashlib.md5((xml_data + self.api_key).encode()).hexdigest()
        # Step 2: MD5 of (Step1_result + API_KEY)
        signature = hashlib.md5((step1 + self.api_key).encode()).hexdigest()
        self.logger.debug(f"Generated signature (2-step MD5): {signature[:8]}...")
        return signature
    
    def _build_xml_request(self, action, object_type, attributes):
        timestamp = str(int(time.time()))
        
        xml_template = '''<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
    <header>
        <version>0.9</version>
    </header>
    <body>
        <data_block>
            <dt_assoc>
                <item key="protocol">XCP</item>
                <item key="action">{action}</item>
                <item key="object">{object_type}</item>
                <item key="attributes">
                    <dt_assoc>
                        {attributes}
                    </dt_assoc>
                </item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>'''
        
        return xml_template.format(
            action=action,
            object_type=object_type,
            attributes=attributes
        )
    
    def _make_request(self, xml_data):
        signature = self._generate_signature(xml_data)
        headers = self.session.headers.copy()
        headers['X-Signature'] = signature
        
        self.logger.debug(f"Making request to: {self.host}/")
        self.logger.debug(f"Request headers: {dict(headers)}")
        self.logger.debug(f"Request XML (first 200 chars): {xml_data[:200]}...")
        
        try:
            response = self.session.post(
                f"{self.host}/",
                data=xml_data,
                headers=headers,
                timeout=30
            )
            
            self.logger.info(f"Response status: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            self.logger.debug(f"Response content (first 500 chars): {response.text[:500]}...")
            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"OpenSRS API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Error response content: {e.response.text}")
            raise Exception(f"OpenSRS API request failed: {e}")
    
    def check_domain_availability(self, domain):
        self.logger.info(f"Checking availability for domain: {domain}")
        
        attributes = f'''
            <item key="domain">{domain}</item>
        '''
        
        xml_request = self._build_xml_request('LOOKUP', 'DOMAIN', attributes)
        
        try:
            response = self._make_request(xml_request)
            
            self.logger.debug(f"Full response for {domain}: {response}")
            
            # Check for successful API response
            if '<item key="is_success">1</item>' in response:
                self.logger.info(f"Successful API response for {domain}")
                if 'status">available' in response:
                    self.logger.info(f"Domain {domain} is available")
                    return {'domain': domain, 'available': True, 'status': 'available'}
                else:
                    self.logger.info(f"Domain {domain} is not available")
                    return {'domain': domain, 'available': False, 'status': 'registered'}
            else:
                self.logger.error(f"API returned error for {domain}: {response}")
                return {'domain': domain, 'available': False, 'status': 'error', 'error': 'API error', 'response': response}
                
        except Exception as e:
            self.logger.error(f"Exception checking {domain}: {str(e)}")
            return {'domain': domain, 'available': False, 'status': 'error', 'error': str(e)}
    
    def bulk_check_availability(self, domains, batch_size=10):
        results = []
        
        for i in range(0, len(domains), batch_size):
            batch = domains[i:i + batch_size]
            
            for domain in batch:
                result = self.check_domain_availability(domain)
                results.append(result)
                time.sleep(0.1)
        
        return results
    
    def register_domain(self, domain, contact_info, years=1):
        if self.use_test:
            print(f"TEST MODE: Would register {domain} for {years} year(s)")
            return {'domain': domain, 'status': 'test_success', 'message': 'Test registration successful'}
        
        contact_xml = f'''
            <item key="first_name">{contact_info.get('first_name', '')}</item>
            <item key="last_name">{contact_info.get('last_name', '')}</item>
            <item key="org_name">{contact_info.get('org_name', '')}</item>
            <item key="address1">{contact_info.get('address1', '')}</item>
            <item key="city">{contact_info.get('city', '')}</item>
            <item key="state">{contact_info.get('state', '')}</item>
            <item key="country">{contact_info.get('country', '')}</item>
            <item key="postal_code">{contact_info.get('postal_code', '')}</item>
            <item key="phone">{contact_info.get('phone', '')}</item>
            <item key="email">{contact_info.get('email', '')}</item>
        '''
        
        attributes = f'''
            <item key="domain">{domain}</item>
            <item key="auto_renew">0</item>
            <item key="period">{years}</item>
            <item key="contact_set">
                <dt_assoc>
                    <item key="owner">
                        <dt_assoc>
                            {contact_xml}
                        </dt_assoc>
                    </item>
                    <item key="admin">
                        <dt_assoc>
                            {contact_xml}
                        </dt_assoc>
                    </item>
                    <item key="billing">
                        <dt_assoc>
                            {contact_xml}
                        </dt_assoc>
                    </item>
                    <item key="tech">
                        <dt_assoc>
                            {contact_xml}
                        </dt_assoc>
                    </item>
                </dt_assoc>
            </item>
        '''
        
        xml_request = self._build_xml_request('sw_register', 'domain', attributes)
        
        try:
            response = self._make_request(xml_request)
            
            if '<item key="is_success">1</item>' in response:
                return {'domain': domain, 'status': 'success', 'message': 'Domain registered successfully'}
            else:
                return {'domain': domain, 'status': 'failed', 'message': 'Registration failed'}
                
        except Exception as e:
            return {'domain': domain, 'status': 'error', 'message': str(e)}
    
    def validate_credentials(self):
        self.logger.info("Validating OpenSRS credentials...")
        try:
            test_domain = "test-validation-domain-12345.com"
            result = self.check_domain_availability(test_domain)
            
            self.logger.info(f"Validation result: {result}")
            
            is_valid = result.get('status') != 'error'
            if is_valid:
                self.logger.info("Credentials validation successful")
            else:
                self.logger.error(f"Credentials validation failed: {result.get('error', 'Unknown error')}")
                if 'response' in result:
                    self.logger.error(f"API response: {result['response']}")
            
            return is_valid
        except Exception as e:
            self.logger.error(f"Exception during credential validation: {str(e)}")
            return False