# Plan 004: Multi-Domain Server Infrastructure

## Overview
Plan 004 addresses the need for serving multiple typosquatted domains from a single server with SNI (Server Name Indication) support and automated nginx configuration generation for production deployments.

## Requirements

### Primary Goals:
1. **Multi-Domain Hosting** - Serve multiple cloned sites from one server
2. **SNI Support** - Handle SSL/TLS certificates for multiple domains
3. **Nginx Integration** - Generate production-ready nginx configurations
4. **Certificate Management** - Automate SSL certificate handling
5. **Performance Optimization** - Efficient serving of multiple sites

### Use Cases:
- Penetration testers managing multiple typosquatted domains
- Large-scale phishing simulation campaigns
- Consolidated hosting for multiple client assessments
- Production deployment with proper SSL certificates

## Implementation Plan

### 1. Multi-Domain SNI Web Server (`core/multi_server.py`)

#### Core Architecture:
```python
class MultiDomainServer:
    def __init__(self, domains, ssl_mode='selfsigned'):
        self.domains = {}  # domain -> site_path mapping
        self.ssl_contexts = {}  # domain -> ssl_context mapping
        self.ssl_mode = ssl_mode
    
    def add_domain(self, domain, site_path, cert_path=None, key_path=None):
        """Add a domain with its corresponding cloned site"""
        pass
    
    def generate_certificates(self, domains):
        """Generate SSL certificates for domains"""
        pass
    
    def create_ssl_context(self, domain, cert_path, key_path):
        """Create SSL context for SNI"""
        pass
    
    def handle_request(self, request):
        """Route requests based on Host header"""
        pass
```

#### SSL/TLS Certificate Management:
1. **Self-Signed Certificates**
   - Automatic generation for testing
   - Per-domain certificate creation
   - Subject Alternative Name (SAN) support
   - 2048-bit RSA key generation

2. **Let's Encrypt Integration**
   - ACME protocol implementation
   - HTTP-01 challenge handling
   - Automatic certificate renewal
   - Rate limiting compliance

3. **Custom Certificate Support**
   - User-provided certificate loading
   - Certificate chain validation
   - Private key security
   - Certificate expiration monitoring

#### SNI Implementation:
```python
def sni_callback(ssl_socket, server_name, ssl_context):
    """SNI callback to select appropriate SSL context"""
    if server_name in self.ssl_contexts:
        ssl_socket.context = self.ssl_contexts[server_name]
    else:
        # Default fallback context
        ssl_socket.context = self.default_ssl_context
```

#### Virtual Host Routing:
- Host header parsing and validation
- Domain-to-directory mapping
- Default site fallback handling
- Request logging per domain

### 2. Nginx Configuration Generator (`core/nginx_generator.py`)

#### Configuration Generation:
```python
class NginxConfigGenerator:
    def __init__(self, domains, base_path, ssl_mode='letsencrypt'):
        self.domains = domains
        self.base_path = base_path
        self.ssl_mode = ssl_mode
    
    def generate_server_block(self, domain, site_path):
        """Generate nginx server block for domain"""
        pass
    
    def generate_ssl_config(self, domain):
        """Generate SSL configuration for domain"""
        pass
    
    def generate_master_config(self):
        """Generate complete nginx configuration"""
        pass
```

#### Generated Configuration Features:
1. **Server Blocks**
   - Per-domain virtual hosts
   - Document root configuration
   - Index file specifications
   - Error page handling

2. **SSL Configuration**
   - Certificate path configuration
   - SSL protocol settings
   - Cipher suite optimization
   - OCSP stapling

3. **Security Headers**
   - HSTS (HTTP Strict Transport Security)
   - CSP (Content Security Policy)
   - X-Frame-Options
   - X-Content-Type-Options

4. **Performance Optimization**
   - Gzip compression
   - Browser caching
   - Static file handling
   - Connection keep-alive

#### Example Generated Configuration:
```nginx
server {
    listen 80;
    server_name fake-example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fake-example.com;
    
    root /var/www/tsquat/fake-example.com;
    index index.html;
    
    ssl_certificate /etc/ssl/certs/fake-example.com.crt;
    ssl_certificate_key /etc/ssl/private/fake-example.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
    }
    
    access_log /var/log/nginx/fake-example.com.access.log;
    error_log /var/log/nginx/fake-example.com.error.log;
}
```

### 3. Certificate Management System

#### Let's Encrypt Integration:
```python
class LetsEncryptManager:
    def __init__(self, email, staging=False):
        self.email = email
        self.staging = staging
        self.acme_client = self.setup_acme_client()
    
    def request_certificate(self, domain):
        """Request certificate from Let's Encrypt"""
        pass
    
    def setup_http_challenge(self, domain, challenge):
        """Setup HTTP-01 challenge response"""
        pass
    
    def install_certificate(self, domain, cert_data):
        """Install certificate and private key"""
        pass
```

#### Certificate Renewal:
- Automatic renewal scheduling
- Expiration monitoring (30-day warning)
- Graceful reload without downtime
- Backup and rollback capabilities

### 4. CLI Integration Enhancements

#### New Command Line Arguments:
```bash
python tsquat.py example.com --clone --multi-domain \
  --domains "fake-example.com,typo-example.com,examp1e.com" \
  --ssl-mode letsencrypt \
  --email admin@company.com \
  --generate-nginx \
  --server-mode production
```

#### Arguments Specification:
- `--multi-domain` - Enable multi-domain server mode
- `--domains LIST` - Comma-separated domain list
- `--ssl-mode MODE` - Certificate mode: selfsigned|letsencrypt|custom
- `--email EMAIL` - Email for Let's Encrypt registration
- `--generate-nginx` - Generate nginx configuration
- `--server-mode MODE` - Server mode: development|testing|production

### 5. Directory Structure Enhancement

#### Enhanced Output Structure:
```
deployment/
├── sites/                  # Individual site directories
│   ├── fake-example.com/
│   │   ├── index.html
│   │   ├── assets/
│   │   └── capture.php
│   ├── typo-example.com/
│   └── examp1e.com/
├── ssl/                    # SSL certificates
│   ├── fake-example.com/
│   │   ├── cert.pem
│   │   ├── privkey.pem
│   │   └── fullchain.pem
│   └── [other domains]/
├── configs/                # Generated configurations
│   ├── nginx/
│   │   ├── sites-available/
│   │   └── nginx.conf
│   ├── apache/
│   └── domains.json
├── logs/                   # Server logs
│   ├── access/
│   ├── error/
│   └── capture/
├── scripts/                # Management scripts
│   ├── multi_server.py
│   ├── cert_manager.py
│   └── deploy.sh
└── README.md              # Deployment instructions
```

## Implementation Details

### 1. SNI Server Implementation

#### HTTP/HTTPS Dual Listener:
```python
import ssl
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

class MultiDomainHTTPServer:
    def __init__(self, port_http=80, port_https=443):
        self.port_http = port_http
        self.port_https = port_https
        self.domain_mappings = {}
        
    def start_servers(self):
        # Start HTTP server (redirect to HTTPS)
        http_thread = threading.Thread(target=self.start_http_server)
        http_thread.daemon = True
        http_thread.start()
        
        # Start HTTPS server with SNI
        self.start_https_server()
```

#### SSL Context Management:
```python
def setup_ssl_contexts(self):
    """Setup SSL contexts for each domain"""
    for domain, config in self.domain_mappings.items():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(config['cert_path'], config['key_path'])
        self.ssl_contexts[domain] = context
```

### 2. Configuration Generation

#### Template-Based Generation:
```python
NGINX_SERVER_TEMPLATE = """
server {{
    listen 443 ssl http2;
    server_name {domain};
    
    root {document_root};
    index index.html index.php;
    
    ssl_certificate {cert_path};
    ssl_certificate_key {key_path};
    
    {ssl_config}
    {security_headers}
    {location_blocks}
    
    access_log {access_log};
    error_log {error_log};
}}
"""
```

### 3. Certificate Automation

#### Self-Signed Certificate Generation:
```python
def generate_self_signed_cert(domain, cert_path, key_path):
    """Generate self-signed certificate for domain"""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(domain),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write certificate and private key
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
```

## Deployment Workflows

### 1. Development Workflow:
```bash
# Generate multiple typosquatted domains and clone sites
python tsquat.py example.com --register --clone --multi-domain \
  --max-variants 10 --ssl-mode selfsigned

# Start development server
cd deployment
python scripts/multi_server.py --dev-mode --port 8443
```

### 2. Testing Workflow:
```bash
# Generate nginx configuration for testing
python tsquat.py example.com --clone --multi-domain \
  --domains "fake-example.com,typo-example.com" \
  --generate-nginx --ssl-mode selfsigned

# Test nginx configuration
sudo nginx -t -c deployment/configs/nginx/nginx.conf
```

### 3. Production Deployment:
```bash
# Generate production configuration with Let's Encrypt
python tsquat.py example.com --clone --multi-domain \
  --domains "fake-example.com,typo-example.com" \
  --ssl-mode letsencrypt --email admin@company.com \
  --generate-nginx --server-mode production

# Deploy to server
sudo cp deployment/configs/nginx/sites-available/* /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/tsquat-* /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Security Considerations

### 1. Certificate Security:
- Private key protection (600 permissions)
- Certificate chain validation
- OCSP stapling configuration
- Forward secrecy support

### 2. Server Security:
- Non-root user execution
- Chroot jail for web server
- Rate limiting per domain
- DDoS protection mechanisms

### 3. Monitoring and Logging:
- Per-domain access logs
- Certificate expiration alerts
- Failed authentication tracking
- Anomaly detection

## Performance Optimization

### 1. Connection Handling:
- HTTP/2 support
- Connection pooling
- Keep-alive optimization
- Request multiplexing

### 2. Content Delivery:
- Static file caching
- Gzip compression
- Browser caching headers
- CDN integration support

### 3. Resource Management:
- Memory usage monitoring
- CPU usage optimization
- Disk I/O efficiency
- Network bandwidth management

## Testing Strategy

### 1. Unit Tests:
- Certificate generation testing
- Configuration generation validation
- SNI callback functionality
- Domain routing verification

### 2. Integration Tests:
- Multi-domain SSL handshake
- Nginx configuration deployment
- Let's Encrypt certificate request
- Load balancing verification

### 3. Performance Tests:
- Concurrent connection handling
- SSL handshake performance
- Memory usage under load
- Certificate validation speed

## Future Enhancements

### 1. Advanced Features:
- HTTP/3 (QUIC) support
- Advanced load balancing
- Geographic load distribution
- Edge server deployment

### 2. Management Interface:
- Web-based configuration UI
- Real-time monitoring dashboard
- Certificate management interface
- Domain health checking

### 3. Enterprise Features:
- Multi-tenant support
- Role-based access control
- Audit logging
- Compliance reporting

This multi-domain server infrastructure will significantly enhance the TSquat tool's capabilities for large-scale penetration testing campaigns while maintaining security and performance standards.