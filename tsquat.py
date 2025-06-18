#!/usr/bin/env python3

import argparse
import sys
import os
from pathlib import Path
from colorama import init, Fore, Style
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent))

from core.domain_generator import DomainGenerator
from core.opensrs_client import OpenSRSClient
from core.scraper import WebScraper
from config.config import Config
from utils.helpers import setup_logging, validate_domain, create_banner

init(autoreset=True)

class TSquat:
    def __init__(self, debug=False):
        self.config = Config()
        self.generator = DomainGenerator()
        self.opensrs_client = None
        self.scraper = WebScraper()
        self.logger = setup_logging(debug=debug)
    
    def configure_credentials(self, force_reconfigure=False):
        """Interactive configuration of OpenSRS credentials and registration defaults"""
        opensrs_config = self.config.get_opensrs_config()
        registration_config = self.config.get_registration_config()
        
        # Show current configuration if it exists
        if not force_reconfigure and opensrs_config['api_key'] and opensrs_config['username']:
            print(f"{Fore.CYAN}Current Configuration:")
            print(f"  OpenSRS Username: {opensrs_config['username']}")
            print(f"  API Key: {'*' * (len(opensrs_config['api_key']) - 4) + opensrs_config['api_key'][-4:] if opensrs_config['api_key'] else 'Not set'}")
            print(f"  Environment: {'Test' if opensrs_config['use_test'] else 'Production'}")
            print(f"  Registration defaults: {'Configured' if registration_config['email'] else 'Not set'}")
            print()
            
            if not force_reconfigure:
                update = input(f"{Fore.YELLOW}Update configuration? (y/n): ").strip().lower()
                if update != 'y':
                    print(f"{Fore.GREEN}Configuration unchanged.")
                    return True
        
        print(f"{Fore.CYAN}=== OpenSRS API Configuration ===")
        
        # Get new credentials
        current_username = opensrs_config.get('username', '')
        username = input(f"OpenSRS Username [{current_username}]: ").strip()
        if not username and current_username:
            username = current_username
        
        api_key = input("API Key: ").strip()
        if not api_key:
            current_key = opensrs_config.get('api_key', '')
            if current_key:
                keep_current = input(f"Keep current API key? (y/n): ").strip().lower()
                if keep_current == 'y':
                    api_key = current_key
        
        current_test_mode = opensrs_config.get('use_test', True)
        test_env_default = 'y' if current_test_mode else 'n'
        use_test = input(f"Use test environment? (y/n) [{test_env_default}]: ").strip().lower()
        if not use_test:
            use_test = test_env_default
        use_test = use_test == 'y'
        
        if not username or not api_key:
            print(f"{Fore.RED}Username and API key are required.")
            return False
        
        # Save OpenSRS configuration
        self.config.set_opensrs_credentials(api_key, username, use_test)
        
        # Configure registration defaults
        print(f"\n{Fore.CYAN}=== Registration Defaults Configuration ===")
        print(f"{Fore.YELLOW}Configure default contact information for domain registration:")
        
        contact_info = self.get_contact_info_interactive(registration_config)
        
        # Configure registration credentials
        print(f"\n{Fore.CYAN}=== Domain Registration Credentials ===")
        print(f"{Fore.YELLOW}OpenSRS requires separate username/password for domain registration:")
        print(f"{Fore.YELLOW}Username: 3-20 characters (alphanumeric)")
        print(f"{Fore.YELLOW}Password: 10-20 characters (alphanumeric + symbols)")
        
        current_reg_username = registration_config.get('reg_username', '')
        reg_username = input(f"Registration username [{current_reg_username}]: ").strip()
        if not reg_username and current_reg_username:
            reg_username = current_reg_username
        
        # Validate username
        if reg_username and (len(reg_username) < 3 or len(reg_username) > 20 or not reg_username.isalnum()):
            print(f"{Fore.YELLOW}Warning: Username should be 3-20 alphanumeric characters")
        
        import getpass
        reg_password = getpass.getpass("Registration password: ").strip()
        if not reg_password:
            current_reg_password = registration_config.get('reg_password', '')
            if current_reg_password:
                keep_current = input(f"Keep current registration password? (y/n): ").strip().lower()
                if keep_current == 'y':
                    reg_password = current_reg_password
        
        # Validate password
        if reg_password and (len(reg_password) < 10 or len(reg_password) > 20):
            print(f"{Fore.YELLOW}Warning: Password should be 10-20 characters")
        
        # Add registration credentials to contact info
        contact_info['reg_username'] = reg_username
        contact_info['reg_password'] = reg_password
        
        # Configure DNS settings
        print(f"\n{Fore.CYAN}=== DNS Configuration ===")
        auto_dns_current = 'y' if registration_config.get('auto_dns', True) else 'n'
        auto_dns = input(f"Automatically set up DNS at OpenSRS? (y/n) [{auto_dns_current}]: ").strip().lower()
        if not auto_dns:
            auto_dns = auto_dns_current
        auto_dns_bool = auto_dns == 'y'
        
        default_ip = ''
        if auto_dns_bool:
            current_ip = registration_config.get('default_ip', '')
            default_ip = input(f"Default IP address for A records [{current_ip}]: ").strip()
            if not default_ip and current_ip:
                default_ip = current_ip
        
        # Save registration configuration
        self.config.set_registration_defaults(contact_info, auto_dns_bool, default_ip)
        
        print(f"{Fore.GREEN}Configuration saved successfully.")
        return True
    
    def setup_opensrs_client(self):
        opensrs_config = self.config.get_opensrs_config()
        
        if not opensrs_config['api_key'] or not opensrs_config['username']:
            print(f"{Fore.YELLOW}OpenSRS credentials not configured.")
            if not self.configure_credentials(force_reconfigure=True):
                return False
            opensrs_config = self.config.get_opensrs_config()
        
        self.opensrs_client = OpenSRSClient(
            opensrs_config['api_key'],
            opensrs_config['username'],
            opensrs_config['host'],
            opensrs_config['use_test']
        )
        
        if not self.opensrs_client.validate_credentials():
            print(f"{Fore.RED}Invalid OpenSRS credentials. Please check your API key and username.")
            print(f"{Fore.YELLOW}Tip: Use --debug flag for detailed error information")
            return False
        
        return True
    
    def generate_domains(self, target_domain, max_variants=100):
        print(f"{Fore.CYAN}Generating typosquatted domains for: {target_domain}")
        variants = self.generator.generate_all_variants(target_domain, max_variants)
        print(f"{Fore.GREEN}Generated {len(variants)} domain variants")
        return variants
    
    def check_availability(self, domains):
        if not self.opensrs_client:
            if not self.setup_opensrs_client():
                return []
        
        print(f"{Fore.CYAN}Checking domain availability...")
        results = []
        
        with tqdm(total=len(domains), desc="Checking domains") as pbar:
            for domain in domains:
                result = self.opensrs_client.check_domain_availability(domain)
                results.append(result)
                pbar.update(1)
        
        return results
    
    def display_results(self, results):
        available_domains = [r for r in results if r.get('available')]
        unavailable_domains = [r for r in results if not r.get('available')]
        error_domains = [r for r in unavailable_domains if r.get('status') == 'error']
        
        print(f"\n{Fore.GREEN}=== AVAILABLE DOMAINS ({len(available_domains)}) ===")
        for result in available_domains:
            print(f"{Fore.GREEN}✓ {result['domain']}")
        
        print(f"\n{Fore.RED}=== UNAVAILABLE DOMAINS ({len(unavailable_domains) - len(error_domains)}) ===")
        for result in unavailable_domains:
            if result.get('status') != 'error':
                status = result.get('status', 'unknown')
                print(f"{Fore.RED}✗ {result['domain']} ({status})")
        
        if error_domains:
            print(f"\n{Fore.YELLOW}=== DOMAINS WITH ERRORS ({len(error_domains)}) ===")
            for result in error_domains:
                error_msg = result.get('error', 'Unknown error')
                print(f"{Fore.YELLOW}? {result['domain']} - {error_msg}")
        
        return available_domains
    
    def register_domains(self, available_domains):
        if not available_domains:
            print(f"{Fore.YELLOW}No available domains to register.")
            return
        
        print(f"\n{Fore.CYAN}Available domains for registration:")
        for i, domain_info in enumerate(available_domains, 1):
            print(f"{i}. {domain_info['domain']}")
        
        selection = input(f"\nEnter domain numbers to register (comma-separated) or 'all': ").strip()
        
        if selection.lower() == 'all':
            domains_to_register = available_domains
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                domains_to_register = [available_domains[i] for i in indices if 0 <= i < len(available_domains)]
            except (ValueError, IndexError):
                print(f"{Fore.RED}Invalid selection.")
                return
        
        if not domains_to_register:
            print(f"{Fore.YELLOW}No domains selected.")
            return
        
        contact_info = self.get_contact_info()
        
        print(f"\n{Fore.CYAN}Registering selected domains...")
        print(f"{Fore.YELLOW}Note: Check tsquat.log for detailed registration debugging information")
        
        registration_config = self.config.get_registration_config()
        
        for domain_info in domains_to_register:
            domain = domain_info['domain']
            print(f"\n{Fore.CYAN}Attempting to register: {domain}")
            
            result = self.opensrs_client.register_domain(domain, contact_info)
            
            if result['status'] in ['success', 'test_success']:
                print(f"{Fore.GREEN}✓ {domain} - {result['message']}")
                
                # Set up DNS if configured
                if registration_config.get('auto_dns') and registration_config.get('default_ip'):
                    print(f"{Fore.CYAN}  Setting up DNS for {domain}...")
                    dns_result = self.opensrs_client.setup_dns_zone(domain, registration_config['default_ip'])
                    
                    if dns_result['status'] in ['success', 'test_success']:
                        print(f"{Fore.GREEN}  ✓ DNS configured - {dns_result['message']}")
                    else:
                        print(f"{Fore.YELLOW}  ⚠ DNS setup failed - {dns_result['message']}")
                        print(f"{Fore.YELLOW}    You can manually configure DNS later")
                elif registration_config.get('auto_dns'):
                    print(f"{Fore.YELLOW}  ⚠ DNS setup skipped - no default IP configured")
                    print(f"{Fore.YELLOW}    Run --config to set a default IP address")
                
            else:
                print(f"{Fore.RED}✗ {domain} - {result['message']}")
                if 'response' in result:
                    print(f"{Fore.YELLOW}  Full API response logged to tsquat.log")
                
                # Show common error explanations
                if 'response_code' in result.get('message', ''):
                    print(f"{Fore.YELLOW}  Check the log file for the complete error response and response code")
                elif 'Missing required' in result.get('message', ''):
                    print(f"{Fore.YELLOW}  Contact information validation failed - check required fields")
                elif 'Registration failed' in result.get('message', ''):
                    print(f"{Fore.YELLOW}  Domain registration was rejected by the registry")
                else:
                    print(f"{Fore.YELLOW}  Unknown registration error - check logs for details")
    
    def get_contact_info_interactive(self, current_config=None):
        """Get contact info with defaults from current configuration"""
        if current_config is None:
            current_config = {}
        
        return {
            'first_name': input(f"First name [{current_config.get('first_name', '')}]: ").strip() or current_config.get('first_name', ''),
            'last_name': input(f"Last name [{current_config.get('last_name', '')}]: ").strip() or current_config.get('last_name', ''),
            'org_name': input(f"Organization [{current_config.get('org_name', '')}]: ").strip() or current_config.get('org_name', ''),
            'address1': input(f"Address [{current_config.get('address1', '')}]: ").strip() or current_config.get('address1', ''),
            'city': input(f"City [{current_config.get('city', '')}]: ").strip() or current_config.get('city', ''),
            'state': input(f"State/Province [{current_config.get('state', '')}]: ").strip() or current_config.get('state', ''),
            'country': input(f"Country [{current_config.get('country', '')}]: ").strip() or current_config.get('country', ''),
            'postal_code': input(f"Postal code [{current_config.get('postal_code', '')}]: ").strip() or current_config.get('postal_code', ''),
            'phone': input(f"Phone [{current_config.get('phone', '')}]: ").strip() or current_config.get('phone', ''),
            'email': input(f"Email [{current_config.get('email', '')}]: ").strip() or current_config.get('email', '')
        }
    
    def get_contact_info(self):
        """Get contact info using configured defaults or prompt for new info"""
        registration_config = self.config.get_registration_config()
        
        # Check if we have complete registration defaults including credentials
        required_fields = ['first_name', 'last_name', 'address1', 'city', 'state', 'country', 'postal_code', 'phone', 'email', 'reg_username', 'reg_password']
        if all(registration_config.get(field) for field in required_fields):
            print(f"\n{Fore.CYAN}Using configured registration defaults:")
            print(f"  Name: {registration_config['first_name']} {registration_config['last_name']}")
            print(f"  Email: {registration_config['email']}")
            print(f"  Address: {registration_config['address1']}, {registration_config['city']}, {registration_config['state']}")
            print(f"  Registration Username: {registration_config['reg_username']}")
            
            use_defaults = input(f"\n{Fore.YELLOW}Use these defaults? (y/n): ").strip().lower()
            if use_defaults == 'y':
                return registration_config
        
        print(f"\n{Fore.CYAN}Enter contact information for domain registration:")
        contact_info = self.get_contact_info_interactive(registration_config)
        
        # Get registration credentials if not already configured
        if not registration_config.get('reg_username') or not registration_config.get('reg_password'):
            print(f"\n{Fore.CYAN}Registration credentials required:")
            
            if not registration_config.get('reg_username'):
                reg_username = input("Registration username (3-20 alphanumeric): ").strip()
                contact_info['reg_username'] = reg_username
            else:
                contact_info['reg_username'] = registration_config['reg_username']
            
            if not registration_config.get('reg_password'):
                import getpass
                reg_password = getpass.getpass("Registration password (10-20 chars): ").strip()
                contact_info['reg_password'] = reg_password
            else:
                contact_info['reg_password'] = registration_config['reg_password']
        else:
            contact_info['reg_username'] = registration_config['reg_username']
            contact_info['reg_password'] = registration_config['reg_password']
        
        return contact_info
    
    def clone_website(self, target_domain, output_dir, lookalike_domain=None):
        print(f"{Fore.CYAN}Cloning website: {target_domain}")
        if lookalike_domain:
            print(f"{Fore.CYAN}Will replace {target_domain} URLs with: {lookalike_domain}")
        
        success = self.scraper.clone_website(target_domain, output_dir, lookalike_domain)
        
        if success:
            print(f"{Fore.GREEN}Website cloned successfully to: {output_dir}")
            if lookalike_domain:
                print(f"{Fore.GREEN}Domain replacement completed: {target_domain} -> {lookalike_domain}")
        else:
            print(f"{Fore.RED}Failed to clone website")

def main():
    parser = argparse.ArgumentParser(
        description="TSquat - Domain Typosquatting Tool for Penetration Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tsquat.py example.com
  python tsquat.py example.com --register
  python tsquat.py example.com --clone --output ./cloned_site
  python tsquat.py example.com --clone --lookalike-domain examp1e.com
  python tsquat.py example.com --register --clone --max-variants 50

Configuration:
  python tsquat.py --config          # Configure OpenSRS credentials, registration defaults, and DNS
  python tsquat.py --show-config     # Show current configuration
  python tsquat.py --clear-config    # Clear all configuration
        """
    )
    
    parser.add_argument('domain', nargs='?', help='Target domain to generate variants for')
    parser.add_argument('--register', action='store_true', help='Register available domains')
    parser.add_argument('--clone', action='store_true', help='Clone the target website')
    parser.add_argument('--output', default='./cloned_site', help='Output directory for cloned website')
    parser.add_argument('--lookalike-domain', help='Lookalike domain to replace target domain URLs with (for cloning)')
    parser.add_argument('--max-variants', type=int, default=100, help='Maximum number of domain variants to generate')
    parser.add_argument('--config', action='store_true', help='Configure OpenSRS credentials')
    parser.add_argument('--show-config', action='store_true', help='Show current configuration')
    parser.add_argument('--clear-config', action='store_true', help='Clear all configuration')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    tsquat = TSquat(debug=args.debug)
    
    if args.config:
        if tsquat.configure_credentials():
            print(f"{Fore.GREEN}Configuration updated successfully.")
        else:
            print(f"{Fore.RED}Configuration update failed.")
        return
    
    if args.show_config:
        tsquat.config.show_current_config()
        return
    
    if args.clear_config:
        confirm = input(f"{Fore.YELLOW}Are you sure you want to clear all configuration? (y/n): ").strip().lower()
        if confirm == 'y':
            tsquat.config.clear_config()
            print(f"{Fore.GREEN}Configuration cleared successfully.")
        else:
            print(f"{Fore.YELLOW}Configuration unchanged.")
        return
    
    # Check if domain is required for the operation
    if not args.domain:
        print(f"{Fore.RED}Error: domain is required for this operation")
        parser.print_help()
        return
    
    print(f"{Fore.CYAN}{create_banner()}")
    print(f"{Fore.MAGENTA}For legitimate penetration testing only")
    print(f"{Fore.YELLOW}Target: {args.domain}\n")
    
    if not validate_domain(args.domain):
        print(f"{Fore.RED}Invalid domain format: {args.domain}")
        return
    
    variants = tsquat.generate_domains(args.domain, args.max_variants)
    
    if not variants:
        print(f"{Fore.RED}No domain variants generated.")
        return
    
    results = tsquat.check_availability(variants)
    available_domains = tsquat.display_results(results)
    
    if args.register and available_domains:
        tsquat.register_domains(available_domains)
    
    if args.clone:
        tsquat.clone_website(args.domain, args.output, args.lookalike_domain)

if __name__ == "__main__":
    main()