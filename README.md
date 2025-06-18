# TSquat - Domain Typosquatting Tool for Penetration Testing

A comprehensive Python tool for generating typosquatted domains and cloning websites for legitimate penetration testing and security research.

## ⚠️ Legal Disclaimer

**This tool is designed exclusively for authorized penetration testing and security research.**

- ✅ **Only use this tool in environments where you have explicit written permission**
- ❌ **Unauthorized use may violate computer fraud and abuse laws**
- 📋 **Users are responsible for ensuring compliance with applicable laws and regulations**
- 🛡️ **This tool is not intended for malicious activities**

**Please review [SECURITY.md](SECURITY.md) for comprehensive security guidelines before using this tool.**

## Features

### Phase 1: Domain Generation & Registration
- **Advanced Typosquatting Algorithms:**
  - Character substitution (keyboard adjacency, visual similarity)
  - Character insertion/deletion
  - Character transposition
  - Homophone replacement
  - TLD variations
  - Subdomain insertion
- **OpenSRS API Integration:**
  - Domain availability checking
  - Bulk domain registration
  - Support for test and production environments
- **Interactive CLI Interface:**
  - Colorized output
  - Progress tracking
  - Configurable domain limits

### Phase 2: Website Cloning
- **Comprehensive Website Scraping:**
  - HTML, CSS, JavaScript download
  - Image and asset preservation
  - Relative path conversion
- **Content Modification:**
  - Form action redirection for credential capture
  - Link modification to prevent external navigation
  - Domain replacement throughout content
- **Deployment Tools:**
  - Built-in Python web server
  - PHP capture script for form data
  - Ready-to-deploy website structure

## Installation

1. **Clone the repository:**
   ```bash
   cd tsquat
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenSRS credentials:**
   ```bash
   # Copy the example configuration
   cp config.example ~/.tsquat_config
   
   # Edit with your real credentials (see SECURITY.md for setup guide)
   # Then verify configuration
   python tsquat.py --config
   ```

## Configuration

### OpenSRS API Setup

1. Sign up for an OpenSRS reseller account
2. Obtain your API key and username from the Reseller Control Panel
3. Configure the tool with your credentials:
   ```bash
   python tsquat.py --config
   ```

The configuration is stored in `~/.tsquat_config` for future use.

⚠️ **Security Note**: Never commit the `~/.tsquat_config` file or share your API credentials. See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## Usage

### Basic Domain Generation
```bash
python tsquat.py example.com
```

### Generate and Check Availability
```bash
python tsquat.py example.com --max-variants 50
```

### Register Available Domains
```bash
python tsquat.py example.com --register
```

### Clone Website
```bash
python tsquat.py example.com --clone --output ./cloned_site
```

### Full Workflow
```bash
python tsquat.py example.com --register --clone --max-variants 25
```

### Command Line Options

- `domain` - Target domain to generate variants for
- `--register` - Register available domains interactively
- `--clone` - Clone the target website
- `--output DIR` - Output directory for cloned website (default: ./cloned_site)
- `--max-variants N` - Maximum number of domain variants to generate (default: 100)
- `--config` - Configure OpenSRS API credentials

## Project Structure

```
tsquat/
├── tsquat.py              # Main CLI application
├── requirements.txt       # Python dependencies
├── config/
│   └── config.py         # Configuration management
├── core/
│   ├── domain_generator.py  # Typosquatting algorithms
│   ├── opensrs_client.py   # OpenSRS API client
│   └── scraper.py          # Website cloning functionality
└── utils/
    └── helpers.py          # Utility functions
```

## Typosquatting Algorithms

The tool implements several sophisticated typosquatting techniques:

1. **Character Substitution:**
   - Keyboard adjacency errors (q→w, s→d)
   - Visual similarity replacements (o→0, l→1)

2. **Character Operations:**
   - Character insertion (extra letters)
   - Character deletion (missing letters)
   - Character transposition (swapped letters)

3. **Linguistic Variations:**
   - Homophone replacement (to→too, for→four)
   - Common misspellings

4. **Domain Structure:**
   - TLD variations (.com→.net, .org)
   - Subdomain insertion (www.target.com, mail.target.com)

## Website Cloning Features

### Asset Download
- Recursively downloads CSS, JavaScript, images
- Preserves website structure and styling
- Converts absolute URLs to relative paths

### Content Modification
- Redirects forms to capture credentials
- Blocks external navigation
- Replaces domain references
- Maintains visual authenticity

### Deployment
- Generates Python web server script
- Creates PHP capture script for form data
- Includes comprehensive documentation

## Security Considerations

### 🔒 Critical Security Requirements
- **Authorization Required** - Obtain explicit written permission before testing
- **Credential Protection** - API keys stored securely in `~/.tsquat_config` (gitignored)
- **Data Protection** - Captured data and cloned sites are automatically gitignored
- **Audit Trails** - All operations logged with sensitive information sanitized

### 🛡️ Built-in Security Features
- Comprehensive `.gitignore` to prevent credential exposure
- Rate limiting to respect API terms of service
- Input validation to prevent injection attacks
- Secure configuration file handling

### 📋 Before Using This Tool
1. **Read [SECURITY.md](SECURITY.md)** - Comprehensive security guidelines
2. **Verify legal authorization** - Ensure written permission for all testing
3. **Configure test environment** - Start with OpenSRS test environment
4. **Review target scope** - Confirm testing boundaries and limitations

### 🚨 Protected Information
The following are automatically excluded from version control:
- API credentials and configuration files
- SSL certificates and private keys  
- Captured form data and user submissions
- Cloned website content and assets
- Domain lists and target information
- Log files with sensitive debugging information

## Testing

The tool includes test mode functionality:
- OpenSRS test environment support
- Mock domain registrations
- Safe testing without actual charges

## Contributing

This tool is designed for legitimate security research. When contributing:

1. Ensure all features support authorized testing scenarios
2. Include appropriate warnings and disclaimers
3. Follow responsible disclosure practices
4. Maintain focus on defensive security applications

## Support

For issues and feature requests, please ensure you're using the tool for legitimate security purposes and provide detailed information about your testing environment.

## License

This tool is provided for educational and authorized security testing purposes only. Users assume full responsibility for compliance with applicable laws and regulations.