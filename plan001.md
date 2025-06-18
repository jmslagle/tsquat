# Plan 001: Phase 1 - Domain Generation & Registration

## Overview
Phase 1 focuses on generating typosquatted domain variants and registering available domains through the OpenSRS API for penetration testing purposes.

## Components

### 1. Domain Generation Engine (`core/domain_generator.py`)

#### Typosquatting Algorithms Implemented:
1. **Character Substitution**
   - Keyboard adjacency errors (q→w, s→d, etc.)
   - Visual similarity replacements (o→0, l→1, etc.)
   - Uses predefined mapping dictionaries for common mistakes

2. **Character Insertion**
   - Adds characters at each position in domain name
   - Iterates through alphabet for realistic typos

3. **Character Deletion**
   - Removes one character at a time
   - Generates variants with missing letters

4. **Character Transposition**
   - Swaps adjacent characters
   - Common typing error simulation

5. **Homophone Replacement**
   - Sound-alike word substitutions (to→too, for→four)
   - Predefined homophone dictionary

6. **TLD Variations**
   - Common TLD substitutions (.com→.net, .org, etc.)
   - Includes popular alternative TLDs (.io, .co, .me)

7. **Subdomain Insertion**
   - Adds common subdomains (www, mail, admin, secure)
   - Both prefix and infix variations

#### Key Methods:
- `extract_domain_parts()` - Separates domain name from TLD
- `generate_all_variants()` - Orchestrates all algorithms
- Configurable maximum variants limit

### 2. OpenSRS API Client (`core/opensrs_client.py`)

#### Authentication & Security:
- MD5 signature generation for API requests
- X-Username and X-Signature headers
- Support for test and production environments

#### Core Functionality:
- **Domain Availability Checking**
  - Single domain queries
  - Bulk checking with rate limiting
  - Status parsing (available/registered/error)

- **Domain Registration**
  - Complete contact information handling
  - Multi-year registration support
  - Test mode for safe development

#### API Integration:
- XML request/response handling
- Error handling and retry logic
- Credential validation methods

### 3. Configuration Management (`config/config.py`)

#### Features:
- Secure credential storage in `~/.tsquat_config`
- Test/production environment switching
- Default configuration creation
- Persistent settings management

#### Configuration Options:
- OpenSRS API key and username
- Host endpoints (test/live)
- Environment selection (test/production)

### 4. CLI Interface (`tsquat.py` - Phase 1 components)

#### Command Line Arguments:
- `domain` - Target domain (required)
- `--max-variants N` - Limit number of generated variants
- `--register` - Enable domain registration mode
- `--config` - Configure API credentials

#### Interactive Features:
- Credential setup wizard
- Domain selection for registration
- Contact information collection
- Progress tracking with tqdm
- Colorized output with status indicators

#### Workflow:
1. Validate input domain format
2. Generate typosquatted variants
3. Check domain availability via OpenSRS
4. Display results (available vs. registered)
5. Optional: Interactive domain registration

## Implementation Status: ✅ COMPLETED

### Files Created:
- `core/domain_generator.py` - All typosquatting algorithms
- `core/opensrs_client.py` - Complete API integration
- `config/config.py` - Configuration management
- Main CLI interface in `tsquat.py`

### Testing Approach:
- OpenSRS test environment integration
- Mock registration capabilities
- Input validation and error handling
- Rate limiting for API compliance

## Usage Examples

```bash
# Basic domain generation and availability checking
python tsquat.py example.com

# Generate more variants
python tsquat.py example.com --max-variants 200

# Configure API credentials
python tsquat.py --config

# Generate and register available domains
python tsquat.py example.com --register
```

## Security Considerations

1. **Credential Protection**
   - API keys stored in user home directory
   - File permissions restricted to user only
   - No credentials in command line arguments

2. **Rate Limiting**
   - Built-in delays between API calls
   - Batch processing to reduce load
   - Respectful API usage patterns

3. **Test Mode**
   - Safe testing without actual charges
   - Validation of credentials and workflow
   - Mock registration for development

4. **Audit Trail**
   - All operations logged
   - Domain generation tracking
   - Registration attempt records

## Next Steps
Phase 1 is complete and ready for Phase 2 integration. The domain generation and registration functionality provides a solid foundation for the website cloning components.