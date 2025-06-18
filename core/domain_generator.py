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
    
    def hyphenation_variations(self, domain):
        """Generate hyphenated variations for multi-word domains - prioritize real word boundaries"""
        name, tld = self.extract_domain_parts(domain)
        variants = set()
        
        # PRIMARY: Known compound words and real word boundaries
        # These are the most believable and effective typosquatting domains
        primary_word_splits = [
            # Technology companies and common terms
            ('face', 'book'), ('you', 'tube'), ('linked', 'in'), ('pay', 'pal'),
            ('micro', 'soft'), ('apple', 'store'), ('google', 'drive'), ('drop', 'box'),
            ('face', 'time'), ('word', 'press'), ('sales', 'force'), ('light', 'room'),
            
            # Common website/app terms
            ('web', 'site'), ('web', 'page'), ('home', 'page'), ('log', 'in'),
            ('sign', 'up'), ('sign', 'in'), ('check', 'out'), ('pass', 'word'),
            ('user', 'name'), ('email', 'address'), ('contact', 'us'), ('about', 'us'),
            
            # Business/service terms  
            ('customer', 'service'), ('tech', 'support'), ('help', 'desk'), ('live', 'chat'),
            ('online', 'store'), ('shopping', 'cart'), ('credit', 'card'), ('gift', 'card'),
            ('news', 'letter'), ('press', 'release'), ('terms', 'service'), ('privacy', 'policy'),
            
            # Technology terms
            ('data', 'base'), ('soft', 'ware'), ('hard', 'ware'), ('fire', 'wall'),
            ('net', 'work'), ('inter', 'net'), ('web', 'cam'), ('lap', 'top'),
            ('desk', 'top'), ('smart', 'phone'), ('tab', 'let'), ('note', 'book'),
            
            # Action words
            ('down', 'load'), ('up', 'load'), ('back', 'up'), ('set', 'up'),
            ('log', 'out'), ('shut', 'down'), ('start', 'up'), ('break', 'down'),
            
            # Common prefixes with words
            ('my', 'account'), ('my', 'profile'), ('my', 'settings'), ('my', 'dashboard'),
            ('get', 'started'), ('get', 'help'), ('go', 'back'), ('go', 'home'),
            ('new', 'user'), ('new', 'account'), ('best', 'deals'), ('top', 'rated'),
            
            # Common suffixes
            ('app', 'store'), ('web', 'app'), ('mobile', 'app'), ('desktop', 'app'),
            ('game', 'center'), ('music', 'player'), ('video', 'player'), ('photo', 'gallery')
        ]
        
        name_lower = name.lower()
        
        # Check for primary word boundaries first (highest priority)
        for word1, word2 in primary_word_splits:
            pattern = word1 + word2
            if pattern in name_lower:
                idx = name_lower.find(pattern)
                if idx >= 0:
                    # Preserve original case
                    hyphenated = name[:idx + len(word1)] + '-' + name[idx + len(word1):]
                    variant = f"{hyphenated}{tld}"
                    variants.add(variant)
        
        # SECONDARY: Common prefixes and suffixes (good word boundaries)
        common_prefixes = ['web', 'my', 'get', 'go', 'the', 'best', 'top', 'new', 'old', 'big', 'small', 'super', 'mega', 'ultra', 'auto', 'smart']
        common_suffixes = ['app', 'site', 'web', 'net', 'hub', 'zone', 'pro', 'plus', 'max', 'tech', 'soft', 'ware', 'tool', 'box', 'center', 'world']
        
        # Check for common prefixes
        for prefix in common_prefixes:
            if name.lower().startswith(prefix) and len(name) > len(prefix):
                # Only split if what follows could be a word (at least 2 chars)
                if len(name) - len(prefix) >= 2:
                    boundary = len(prefix)
                    hyphenated = name[:boundary] + '-' + name[boundary:]
                    variant = f"{hyphenated}{tld}"
                    variants.add(variant)
        
        # Check for common suffixes
        for suffix in common_suffixes:
            if name.lower().endswith(suffix) and len(name) > len(suffix):
                # Only split if what precedes could be a word (at least 2 chars)
                if len(name) - len(suffix) >= 2:
                    boundary = len(name) - len(suffix)
                    hyphenated = name[:boundary] + '-' + name[boundary:]
                    variant = f"{hyphenated}{tld}"
                    variants.add(variant)
        
        # TERTIARY: CamelCase and other patterns (lower priority)
        secondary_boundaries = []
        
        # CamelCase transitions
        for i in range(1, len(name)):
            if name[i-1].islower() and name[i].isupper():
                # Only if both parts are reasonable length
                if i >= 2 and len(name) - i >= 2:
                    secondary_boundaries.append(i)
        
        # Number transitions (less common but valid)
        for i in range(1, len(name)):
            if name[i-1].isalpha() and name[i].isdigit():
                secondary_boundaries.append(i)
            elif name[i-1].isdigit() and name[i].isalpha():
                secondary_boundaries.append(i)
        
        # Add secondary boundaries only if we don't have many primary ones
        if len(variants) < 3:
            for boundary in secondary_boundaries:
                if 1 <= boundary < len(name):
                    hyphenated = name[:boundary] + '-' + name[boundary:]
                    variant = f"{hyphenated}{tld}"
                    variants.add(variant)
        
        # Remove original domain if it was added
        variants.discard(domain)
        
        return list(variants)
    
    def generate_all_variants(self, domain, max_variants=500):
        all_variants = set()
        
        methods = [
            self.hyphenation_variations,  # Prioritize hyphenation - most believable typosquats
            self.character_substitution,
            self.character_deletion,
            self.character_transposition,
            self.homophone_replacement,
            self.tld_variations,
            self.subdomain_insertion
        ]
        
        for i, method in enumerate(methods):
            variants = method(domain)
            # Filter to only valid domains
            valid_variants = [v for v in variants if self.is_valid_domain(v)]
            
            # Special handling for hyphenation - give it higher allocation
            if method == self.hyphenation_variations:
                # Hyphenation gets all of its variants (they're high quality)
                method_limit = len(valid_variants)
            else:
                # Other methods get fair share of remaining slots
                remaining_methods = len(methods) - 1
                method_limit = max(1, (max_variants - len(all_variants)) // remaining_methods) if remaining_methods > 0 else max_variants
            
            all_variants.update(valid_variants[:method_limit])
        
        all_variants.discard(domain)
        
        return list(all_variants)[:max_variants]