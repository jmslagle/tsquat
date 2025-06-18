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
    
    def show_current_config(self):
        """Display current configuration in a readable format"""
        opensrs_config = self.get_opensrs_config()
        
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
        print(f"Config File: {self.config_file}")
        print("=" * 50)
    
    def clear_config(self):
        """Clear all configuration"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.create_default_config()
    
    def validate_config(self):
        """Validate current configuration"""
        opensrs_config = self.get_opensrs_config()
        issues = []
        
        if not opensrs_config['username']:
            issues.append("OpenSRS username is not set")
        
        if not opensrs_config['api_key']:
            issues.append("OpenSRS API key is not set")
        
        if len(opensrs_config['api_key']) < 10:
            issues.append("OpenSRS API key appears to be too short")
        
        return issues