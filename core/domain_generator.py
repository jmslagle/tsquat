import re
import itertools
from urllib.parse import urlparse

class DomainGenerator:
    def __init__(self):
        self.keyboard_adjacency = {
            'q': 'wa', 'w': 'qse', 'e': 'wrd', 'r': 'etf', 't': 'ryg', 'y': 'tuh', 'u': 'yij', 'i': 'uok', 'o': 'ipl', 'p': 'ol',
            'a': 'qsz', 's': 'awde', 'd': 'serf', 'f': 'drtg', 'g': 'ftyh', 'h': 'gyuj', 'j': 'huik', 'k': 'jiol', 'l': 'kop',
            'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        
        self.visual_similarity = {
            'a': 'o', 'b': '6d', 'c': 'o0', 'd': 'b', 'e': '3', 'f': 't', 'g': '69q', 'h': 'n',
            'i': '1l', 'j': 'i', 'k': 'x', 'l': '1i', 'm': 'nn', 'n': 'm', 'o': '0a',
            'p': 'q', 'q': '9gp', 'r': 'n', 's': '5', 't': 'f', 'u': 'v', 'v': 'u', 'w': 'vv',
            'x': 'k', 'y': 'v', 'z': '2', '0': 'o', '1': 'li', '2': 'z', '3': 'e', '5': 's',
            '6': 'bg', '9': 'gq'
        }
        
        self.homophones = {
            'to': ['too', 'two', '2'], 'for': ['four', '4'], 'ate': ['eight', '8'], 'one': ['won', '1'],
            'two': ['to', 'too', '2'], 'four': ['for', '4'], 'eight': ['ate', '8'], 'won': ['one', '1'],
            'there': ['their'], 'their': ['there'], 'you': ['u'], 'u': ['you'],
            'are': ['r'], 'r': ['are'], 'see': ['sea', 'c'], 'sea': ['see', 'c'],
            'c': ['see', 'sea'], 'be': ['bee'], 'bee': ['be']
        }
        
        self.common_tlds = [
            '.com', '.net', '.org', '.info', '.biz', '.co', '.io', '.me', '.tv',
            '.cc', '.us', '.uk', '.de', '.fr', '.it', '.es', '.ca', '.au'
        ]
        
        # Valid TLD pattern for validation
        self.valid_tlds = set(self.common_tlds)
    
    def extract_domain_parts(self, domain):
        if '://' in domain:
            domain = urlparse(domain).netloc
        
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[:-1]), '.' + parts[-1]
        return domain, ''
    
    def character_substitution(self, domain):
        variants = set()
        name, tld = self.extract_domain_parts(domain)
        
        for i, char in enumerate(name):
            char_lower = char.lower()
            
            if char_lower in self.keyboard_adjacency:
                for replacement in self.keyboard_adjacency[char_lower]:
                    variant = name[:i] + replacement + name[i+1:]
                    variants.add(variant + tld)
            
            if char_lower in self.visual_similarity:
                for replacement in self.visual_similarity[char_lower]:
                    variant = name[:i] + replacement + name[i+1:]
                    variants.add(variant + tld)
        
        return list(variants)
    
    def character_insertion(self, domain):
        variants = set()
        name, tld = self.extract_domain_parts(domain)
        
        # Limit insertions to avoid very long domains
        if len(name) > 20:  # Skip insertion for very long domains
            return list(variants)
        
        # Insert common typo characters at key positions
        common_chars = 'abcdefghijklmnopqrstuvwxyz'
        for i in range(min(len(name) + 1, 5)):  # Limit positions to first 5
            for char in common_chars:
                variant = name[:i] + char + name[i:]
                if len(variant) <= 63:  # Domain name limit
                    variants.add(variant + tld)
        
        return list(variants)
    
    def character_deletion(self, domain):
        variants = set()
        name, tld = self.extract_domain_parts(domain)
        
        for i in range(len(name)):
            variant = name[:i] + name[i+1:]
            if variant:
                variants.add(variant + tld)
        
        return list(variants)
    
    def character_transposition(self, domain):
        variants = set()
        name, tld = self.extract_domain_parts(domain)
        
        for i in range(len(name) - 1):
            variant = name[:i] + name[i+1] + name[i] + name[i+2:]
            variants.add(variant + tld)
        
        return list(variants)
    
    def homophone_replacement(self, domain):
        variants = set()
        name, tld = self.extract_domain_parts(domain)
        
        for word, replacements in self.homophones.items():
            if word in name.lower():
                for replacement in replacements:
                    variant = name.lower().replace(word, replacement)
                    variants.add(variant + tld)
        
        return list(variants)
    
    def tld_variations(self, domain):
        variants = set()
        name, original_tld = self.extract_domain_parts(domain)
        
        for tld in self.common_tlds:
            if tld != original_tld:
                variants.add(name + tld)
        
        return list(variants)
    
    def subdomain_insertion(self, domain):
        variants = set()
        name, tld = self.extract_domain_parts(domain)
        
        # Only add subdomains as part of the domain name (registrable)
        # NOT as actual subdomains (which aren't registrable)
        subdomains = ['www', 'mail', 'ftp', 'admin', 'secure', 'login', 'support']
        for sub in subdomains:
            # Create domains like "wwwexample.com" or "examplemail.com"
            variants.add(f"{sub}{name}{tld}")
            variants.add(f"{name}{sub}{tld}")
        
        return list(variants)
    
    def is_valid_domain(self, domain):
        """Validate that a domain is registrable and follows proper format"""
        if not domain or len(domain) > 253:
            return False
        
        # Extract parts
        name, tld = self.extract_domain_parts(domain)
        
        # Check if TLD is valid
        if tld not in self.valid_tlds:
            return False
        
        # Check domain name part
        if not name or len(name) < 1 or len(name) > 63:
            return False
        
        # Domain name should not start/end with hyphen
        if name.startswith('-') or name.endswith('-'):
            return False
        
        # Domain name should only contain alphanumeric characters and hyphens
        if not re.match(r'^[a-z0-9-]+$', name.lower()):
            return False
        
        # Should not contain consecutive hyphens
        if '--' in name:
            return False
        
        # Should not be purely numeric (some registrars don't allow this)
        if name.isdigit():
            return False
        
        # Domain should not contain dots in the name part (no subdomains)
        if '.' in name:
            return False
        
        return True
    
    def generate_all_variants(self, domain, max_variants=500):
        all_variants = set()
        
        methods = [
            self.character_substitution,
            self.character_deletion,
            self.character_transposition,
            self.homophone_replacement,
            self.tld_variations,
            self.subdomain_insertion
        ]
        
        for method in methods:
            variants = method(domain)
            # Filter to only valid domains
            valid_variants = [v for v in variants if self.is_valid_domain(v)]
            # Ensure each method contributes at least 1 variant if available
            method_limit = max(1, max_variants // len(methods))
            all_variants.update(valid_variants[:method_limit])
        
        all_variants.discard(domain)
        
        return list(all_variants)[:max_variants]