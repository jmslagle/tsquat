import re
import socket
import subprocess
import logging
from urllib.parse import urlparse

def setup_logging(log_file='tsquat.log', debug=False):
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers to appropriate levels
    if debug:
        logging.getLogger('core.opensrs_client').setLevel(logging.DEBUG)
        logging.getLogger('requests').setLevel(logging.WARNING)  # Reduce requests noise
        logging.getLogger('urllib3').setLevel(logging.WARNING)  # Reduce urllib3 noise
    
    return logging.getLogger(__name__)

def validate_domain(domain):
    """Validate domain name format"""
    if not domain:
        return False
    
    # Remove protocol if present
    if '://' in domain:
        domain = urlparse(domain).netloc
    
    # Check basic format
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    return bool(domain_pattern.match(domain))

def check_dns_resolution(domain):
    """Check if domain resolves to an IP address"""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def format_domain_list(domains, max_display=10):
    """Format domain list for display"""
    if len(domains) <= max_display:
        return '\n'.join(f"  • {domain}" for domain in domains)
    else:
        displayed = domains[:max_display]
        remaining = len(domains) - max_display
        result = '\n'.join(f"  • {domain}" for domain in displayed)
        result += f"\n  ... and {remaining} more domains"
        return result

def calculate_similarity_score(original, variant):
    """Calculate similarity score between original and variant domain"""
    # Simple Levenshtein distance calculation
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    # Extract domain names without TLD for comparison
    orig_parts = original.split('.')
    var_parts = variant.split('.')
    
    orig_name = orig_parts[0] if orig_parts else original
    var_name = var_parts[0] if var_parts else variant
    
    distance = levenshtein_distance(orig_name.lower(), var_name.lower())
    max_len = max(len(orig_name), len(var_name))
    
    if max_len == 0:
        return 1.0
    
    return 1.0 - (distance / max_len)

def check_tool_dependencies():
    """Check if required tools are available"""
    dependencies = {
        'curl': 'curl --version',
        'whois': 'whois --version',
        'dig': 'dig -v'
    }
    
    available = {}
    for tool, check_cmd in dependencies.items():
        try:
            result = subprocess.run(
                check_cmd.split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            available[tool] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            available[tool] = False
    
    return available

def sanitize_filename(filename):
    """Sanitize filename for safe file system operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def extract_emails_from_text(text):
    """Extract email addresses from text"""
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return email_pattern.findall(text)

def extract_phone_numbers_from_text(text):
    """Extract phone numbers from text"""
    phone_patterns = [
        re.compile(r'\b\d{3}-\d{3}-\d{4}\b'),  # 123-456-7890
        re.compile(r'\b\(\d{3}\)\s*\d{3}-\d{4}\b'),  # (123) 456-7890
        re.compile(r'\b\d{3}\.\d{3}\.\d{4}\b'),  # 123.456.7890
        re.compile(r'\b\d{10}\b'),  # 1234567890
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(pattern.findall(text))
    
    return phone_numbers

def create_banner():
    """Create ASCII banner for the tool"""
    banner = """
████████╗███████╗ ██████╗ ██╗   ██╗ █████╗ ████████╗
╚══██╔══╝██╔════╝██╔═══██╗██║   ██║██╔══██╗╚══██╔══╝
   ██║   ███████╗██║   ██║██║   ██║███████║   ██║   
   ██║   ╚════██║██║▄▄ ██║██║   ██║██╔══██║   ██║   
   ██║   ███████║╚██████╔╝╚██████╔╝██║  ██║   ██║   
   ╚═╝   ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   

Domain Typosquatting Tool for Penetration Testing
    """
    return banner