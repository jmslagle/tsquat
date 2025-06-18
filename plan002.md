# Plan 002: Phase 2 - Website Cloning & Deployment

## Overview
Phase 2 focuses on scraping target websites, modifying content for phishing simulation, and creating deployment-ready cloned sites for penetration testing.

## Components

### 1. Web Scraper Engine (`core/scraper.py`)

#### Core Scraping Functionality:
1. **HTTP Session Management**
   - Persistent session with realistic User-Agent
   - Timeout handling and retry logic
   - HTTP/HTTPS protocol support

2. **HTML Processing**
   - BeautifulSoup for DOM manipulation
   - Recursive asset discovery and download
   - URL normalization and resolution

3. **Asset Management**
   - CSS stylesheet download and processing
   - JavaScript file preservation
   - Image and media file handling
   - Font and icon asset support

#### URL Processing:
- **Absolute to Relative Conversion**
  - Protocol-relative URL handling (`//example.com`)
  - Absolute path conversion (`/path/file.css`)
  - Relative path preservation
  - Base URL resolution

- **Asset Path Management**
  - Organized directory structure (`assets/`)
  - Collision-free filename generation
  - Path depth preservation
  - Cross-platform compatibility

### 2. Content Modification Engine

#### HTML Modification:
1. **Form Interception**
   - Action attribute redirection to local capture script
   - Method normalization (POST enforcement)
   - Hidden field injection for tracking
   - Original action preservation for reference

2. **Link Management**
   - External link blocking and alerting
   - Internal link preservation
   - Domain replacement throughout content
   - Navigation flow control

3. **Asset Reference Updates**
   - CSS link tag modification
   - JavaScript src attribute updates
   - Image source path conversion
   - Inline style URL replacement

#### CSS Processing:
- **URL Extraction and Replacement**
  - Regex pattern matching for `url()` references
  - Background image handling
  - Font face source updates
  - Relative path conversion within CSS

- **Style Preservation**
  - Visual appearance maintenance
  - Layout integrity protection
  - Responsive design support

### 3. Deployment Tools

#### Web Server Components:
1. **Python HTTP Server (`serve.py`)**
   - Built-in HTTP server for testing
   - Static file serving
   - POST request handling for forms
   - Data capture and logging

2. **Multi-Domain Web Server (`multi_server.py`)**
   - SNI (Server Name Indication) support
   - Multiple domain hosting on single server
   - SSL/TLS certificate management
   - Virtual host configuration
   - Domain-based routing

3. **Nginx Configuration Generator (`nginx_generator.py`)**
   - Automatic nginx config generation
   - Multi-domain virtual host setup
   - SSL certificate integration (Let's Encrypt)
   - Reverse proxy configuration
   - Load balancing for multiple cloned sites

4. **PHP Capture Script (`capture.php`)**
   - Form data interception
   - Structured logging format
   - IP address and user agent tracking
   - Redirect handling after capture

#### Data Capture System:
- **Logging Format**
  - Timestamp-based entries
  - IP address tracking
  - User agent identification
  - Form field name/value pairs
  - Referrer information

- **Storage Management**
  - Append-only log files
  - File locking for concurrent access
  - Structured data format
  - Easy parsing for analysis

### 4. Content Security & Modification

#### Phishing Simulation Features:
1. **Visual Authenticity**
   - Complete asset preservation
   - Layout and styling maintenance
   - Branding element retention
   - User experience consistency

2. **Functional Modification**
   - Credential capture forms
   - Login simulation
   - Data collection mechanisms
   - Behavioral tracking

#### Domain Replacement:
- **Text Content Processing**
  - Domain name substitution throughout HTML
  - JavaScript variable updates
  - CSS content replacement
  - Meta tag modification

- **Reference Updates**
  - Canonical URL changes
  - Social media meta tags
  - API endpoint modifications
  - CDN reference updates

### 5. CLI Integration (`tsquat.py` - Phase 2 components)

#### Command Line Arguments:
- `--clone` - Enable website cloning mode
- `--output DIR` - Specify output directory
- `--generate-nginx` - Generate nginx configuration files
- `--domains LIST` - Comma-separated list of domains for multi-domain setup
- `--ssl-mode MODE` - SSL certificate mode (selfsigned/letsencrypt/custom)
- Combined workflow with Phase 1

#### Workflow Integration:
1. Domain generation and registration (Phase 1)
2. Website cloning for registered domains
3. Content modification and preparation
4. Deployment package creation

## Implementation Status: ✅ COMPLETED

### Files Created:
- `core/scraper.py` - Complete web scraping engine
- Deployment scripts automatically generated:
  - `serve.py` - Python web server
  - `capture.php` - PHP form capture
  - `README.md` - Deployment documentation

### Key Features Implemented:

#### Asset Download System:
- Recursive CSS/JS/image download
- Duplicate detection and prevention
- Organized directory structure
- Progress tracking and error handling

#### Content Modification:
- Form action redirection
- External link blocking
- Domain replacement
- Asset path conversion

#### Deployment Package:
- Self-contained website clone
- Multiple server options (Python/PHP)
- Data capture functionality
- Complete documentation

## Usage Examples

```bash
# Clone website only
python tsquat.py example.com --clone

# Specify output directory
python tsquat.py example.com --clone --output ./my_clone

# Full workflow: generate domains, register, and clone
python tsquat.py example.com --register --clone

# Clone with custom variant limit
python tsquat.py example.com --clone --max-variants 25
```

## Generated Deployment Structure

```
cloned_site/
├── index.html           # Modified main page
├── capture.php          # Form data capture script
├── serve.py            # Python web server (single domain)
├── multi_server.py     # Multi-domain SNI web server
├── captured_data.txt   # Form submission log
├── README.md           # Deployment instructions
├── ssl/                # SSL certificates directory
│   ├── domain1.crt     # SSL certificates per domain
│   ├── domain1.key     # Private keys per domain
│   └── ca-bundle.crt   # Certificate authority bundle
├── generated_configs/  # Auto-generated configurations
│   ├── nginx.conf      # Nginx virtual host configuration
│   ├── apache.conf     # Apache virtual host configuration
│   └── domains.json    # Domain mapping configuration
└── assets/             # Downloaded website assets
    ├── css/            # Stylesheets
    ├── js/             # JavaScript files
    ├── images/         # Images and media
    └── fonts/          # Font files
```

## Security Considerations

### 1. Legal Compliance
- Comprehensive warnings in all scripts
- Usage disclaimers in documentation
- Authorization requirement emphasis
- Responsible disclosure practices

### 2. Data Protection
- Local data capture only
- No external data transmission
- Secure file permissions
- Audit trail maintenance

### 3. Deployment Security
- Isolated testing environment support
- No production system modification
- Controlled data collection
- Easy cleanup and removal

## Deployment Options

### Python Server (Recommended for Testing)
```bash
cd cloned_site
python3 serve.py
# Access at http://localhost:8080
```

### Multi-Domain Python Server (SNI Support)
```bash
# Generate certificates and serve multiple domains
python3 multi_server.py --domains domain1.com,domain2.com --port 443
# Serves multiple cloned sites with SSL support
```

### Nginx Configuration (Production Deployment)
```bash
# Generate nginx configuration for multiple domains
python tsquat.py example.com --clone --generate-nginx --domains "fake-example.com,typo-example.com"

# Apply generated configuration
sudo cp generated_configs/nginx.conf /etc/nginx/sites-available/tsquat
sudo ln -s /etc/nginx/sites-available/tsquat /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### PHP Server (For Form Capture)
```bash
cd cloned_site
php -S localhost:8080
# Enables full form capture functionality
```

## Advanced Features

### 1. Multi-Domain Server Infrastructure

#### SNI-Enabled Web Server:
- **SSL/TLS Certificate Management**
  - Self-signed certificate generation
  - Let's Encrypt integration for valid certificates
  - Custom certificate support
  - Automatic certificate renewal

- **Virtual Host Configuration**
  - Domain-based routing
  - Host header validation
  - Port 80/443 dual listening
  - HTTP to HTTPS redirects

- **Performance Features**
  - Connection pooling
  - Gzip compression
  - Static file caching
  - Request rate limiting

#### Nginx Configuration Generator:
- **Multi-Site Configuration**
  - Automatic virtual host generation
  - SSL certificate path configuration
  - Upstream server definitions
  - Load balancing configuration

- **Security Headers**
  - HSTS (HTTP Strict Transport Security)
  - CSP (Content Security Policy) headers
  - X-Frame-Options protection
  - MIME type sniffing prevention

- **Logging and Monitoring**
  - Access log configuration per domain
  - Error log separation
  - Performance metrics collection
  - Real-time monitoring hooks

### 2. Asset Processing
- CSS URL rewriting
- JavaScript modification for local execution
- Image optimization and conversion
- Font subsetting and local hosting

### 3. Content Analysis
- Form field identification
- Login mechanism detection
- Data flow analysis
- User interaction tracking

### 4. Customization Options
- Target domain replacement
- Branding modification
- Content personalization
- Behavior simulation

## Integration with Phase 1

Phase 2 seamlessly integrates with Phase 1 to provide a complete workflow:

1. **Domain Generation** - Create typosquatted variants
2. **Availability Checking** - Identify registerable domains
3. **Domain Registration** - Secure available domains
4. **Website Cloning** - Create convincing replicas
5. **Deployment** - Ready-to-use phishing simulation

## Testing and Validation

### Quality Assurance:
- Visual comparison with original site
- Functional testing of modified forms
- Asset loading verification
- Cross-browser compatibility

### Performance Considerations:
- Efficient asset downloading
- Minimal modification overhead
- Fast deployment preparation
- Resource usage optimization

## Future Enhancements

Potential improvements for Phase 2:
- Dynamic content rendering (JavaScript execution)
- Advanced form field detection
- Multi-page site crawling
- Certificate generation for HTTPS
- Automated hosting deployment
- Real-time capture dashboard

Phase 2 provides comprehensive website cloning capabilities that complement Phase 1's domain generation, creating a complete typosquatting simulation platform for authorized penetration testing.