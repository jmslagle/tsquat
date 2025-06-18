import os
import configparser
from pathlib import Path

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = Path.home() / '.tsquat_config'
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        self.config['OpenSRS'] = {
            'api_key': '',
            'username': '',
            'test_host': 'https://horizon.opensrs.net:55443',
            'live_host': 'https://rr-n1-tor.opensrs.net:55443',
            'use_test': 'true'
        }
        
        self.config['Registration'] = {
            'first_name': '',
            'last_name': '',
            'org_name': '',
            'address1': '',
            'city': '',
            'state': '',
            'country': '',
            'postal_code': '',
            'phone': '',
            'email': '',
            'auto_dns': 'true',
            'default_ip': '',
            'reg_username': '',
            'reg_password': ''
        }
        
        self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_opensrs_config(self):
        return {
            'api_key': self.config.get('OpenSRS', 'api_key', fallback=''),
            'username': self.config.get('OpenSRS', 'username', fallback=''),
            'host': self.config.get('OpenSRS', 'test_host' if self.config.getboolean('OpenSRS', 'use_test', fallback=True) else 'live_host'),
            'use_test': self.config.getboolean('OpenSRS', 'use_test', fallback=True)
        }
    
    def set_opensrs_credentials(self, api_key, username, use_test=True):
        if 'OpenSRS' not in self.config:
            self.config['OpenSRS'] = {}
        
        self.config['OpenSRS']['api_key'] = api_key
        self.config['OpenSRS']['username'] = username
        self.config['OpenSRS']['use_test'] = str(use_test)
        self.save_config()
    
    def get_registration_config(self):
        return {
            'first_name': self.config.get('Registration', 'first_name', fallback=''),
            'last_name': self.config.get('Registration', 'last_name', fallback=''),
            'org_name': self.config.get('Registration', 'org_name', fallback=''),
            'address1': self.config.get('Registration', 'address1', fallback=''),
            'city': self.config.get('Registration', 'city', fallback=''),
            'state': self.config.get('Registration', 'state', fallback=''),
            'country': self.config.get('Registration', 'country', fallback=''),
            'postal_code': self.config.get('Registration', 'postal_code', fallback=''),
            'phone': self.config.get('Registration', 'phone', fallback=''),
            'email': self.config.get('Registration', 'email', fallback=''),
            'auto_dns': self.config.getboolean('Registration', 'auto_dns', fallback=True),
            'default_ip': self.config.get('Registration', 'default_ip', fallback=''),
            'reg_username': self.config.get('Registration', 'reg_username', fallback=''),
            'reg_password': self.config.get('Registration', 'reg_password', fallback='')
        }
    
    def set_registration_defaults(self, contact_info, auto_dns=True, default_ip=''):
        if 'Registration' not in self.config:
            self.config['Registration'] = {}
        
        for key, value in contact_info.items():
            self.config['Registration'][key] = str(value)
        
        self.config['Registration']['auto_dns'] = str(auto_dns)
        self.config['Registration']['default_ip'] = str(default_ip)
        self.save_config()
    
    def show_current_config(self):
        """Display current configuration in a readable format"""
        opensrs_config = self.get_opensrs_config()
        registration_config = self.get_registration_config()
        
        print("Current Configuration:")
        print("=" * 50)
        print(f"OpenSRS Username: {opensrs_config['username'] or 'Not set'}")
        
        if opensrs_config['api_key']:
            masked_key = '*' * (len(opensrs_config['api_key']) - 4) + opensrs_config['api_key'][-4:]
            print(f"OpenSRS API Key: {masked_key}")
        else:
            print("OpenSRS API Key: Not set")
        
        print(f"Environment: {'Test' if opensrs_config['use_test'] else 'Production'}")
        print(f"Host: {opensrs_config['host']}")
        
        print(f"\nRegistration Defaults:")
        print(f"Name: {registration_config['first_name']} {registration_config['last_name']}")
        print(f"Organization: {registration_config['org_name'] or 'Not set'}")
        print(f"Email: {registration_config['email'] or 'Not set'}")
        print(f"Address: {registration_config['address1'] or 'Not set'}")
        print(f"City: {registration_config['city'] or 'Not set'}")
        print(f"State: {registration_config['state'] or 'Not set'}")
        print(f"Country: {registration_config['country'] or 'Not set'}")
        print(f"Postal Code: {registration_config['postal_code'] or 'Not set'}")
        print(f"Phone: {registration_config['phone'] or 'Not set'}")
        print(f"Auto DNS: {'Yes' if registration_config['auto_dns'] else 'No'}")
        print(f"Default IP: {registration_config['default_ip'] or 'Not set'}")
        
        # Show registration credentials (masked)
        reg_username = registration_config['reg_username']
        reg_password = registration_config['reg_password']
        print(f"Registration Username: {reg_username or 'Not set'}")
        if reg_password:
            masked_password = '*' * (len(reg_password) - 2) + reg_password[-2:] if len(reg_password) > 2 else '***'
            print(f"Registration Password: {masked_password}")
        else:
            print("Registration Password: Not set")
        
        print(f"\nConfig File: {self.config_file}")
        print("=" * 50)
    
    def clear_config(self):
        """Clear all configuration"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.create_default_config()
    
    def validate_config(self):
        """Validate current configuration"""
        opensrs_config = self.get_opensrs_config()
        registration_config = self.get_registration_config()
        issues = []
        
        # Validate OpenSRS API credentials
        if not opensrs_config['username']:
            issues.append("OpenSRS API username is not set")
        
        if not opensrs_config['api_key']:
            issues.append("OpenSRS API key is not set")
        
        if opensrs_config['api_key'] and len(opensrs_config['api_key']) < 10:
            issues.append("OpenSRS API key appears to be too short")
        
        # Validate registration credentials
        if not registration_config['reg_username']:
            issues.append("Domain registration username is not set")
        elif len(registration_config['reg_username']) < 3 or len(registration_config['reg_username']) > 20:
            issues.append("Domain registration username should be 3-20 characters")
        elif not registration_config['reg_username'].isalnum():
            issues.append("Domain registration username should be alphanumeric only")
        
        if not registration_config['reg_password']:
            issues.append("Domain registration password is not set")
        elif len(registration_config['reg_password']) < 10 or len(registration_config['reg_password']) > 20:
            issues.append("Domain registration password should be 10-20 characters")
        
        # Validate contact information
        required_contact_fields = ['first_name', 'last_name', 'address1', 'city', 'state', 'country', 'postal_code', 'phone', 'email']
        missing_contact = [field for field in required_contact_fields if not registration_config.get(field)]
        if missing_contact:
            issues.append(f"Missing contact information: {', '.join(missing_contact)}")
        
        return issues