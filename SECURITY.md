# Security Guidelines for TSquat

## ⚠️ IMPORTANT SECURITY NOTICE

TSquat is a penetration testing tool designed for **authorized security testing only**. Misuse of this tool may violate computer fraud and abuse laws.

## 🔒 Before Using This Tool

### Legal Requirements
- ✅ **Obtain explicit written permission** before testing any domains or websites
- ✅ **Ensure you have legal authority** to conduct penetration testing
- ✅ **Review applicable laws** in your jurisdiction
- ✅ **Document your authorization** before beginning any assessment

### Ethical Guidelines
- Only use this tool for legitimate security testing
- Do not register domains that could harm legitimate businesses
- Do not use cloned websites to actually deceive users
- Responsibly disclose any vulnerabilities found during testing
- Clean up all test artifacts when testing is complete

## 🛡️ Protecting Sensitive Information

### API Credentials
- **Never commit** API keys or credentials to version control
- Use the provided `config.example` as a template
- Store real credentials in `~/.tsquat_config` (automatically gitignored)
- Rotate API keys regularly
- Use test environment first before production

### Generated Content
- **Cloned websites** may contain sensitive information from target sites
- **Captured form data** contains potentially sensitive user input
- **Domain lists** may reveal testing targets
- **Log files** may contain API keys or sensitive data

### File Protection
The `.gitignore` file protects:
- Configuration files with credentials
- SSL certificates and private keys
- Captured penetration testing data
- Generated cloned websites
- Domain lists and target information
- Log files with sensitive information

## 🔐 Secure Configuration

### OpenSRS API Setup
1. **Start with test environment** (`use_test = true`)
2. **Validate credentials** before production use
3. **Configure IP restrictions** in OpenSRS control panel for production
4. **Monitor API usage** to detect unauthorized access
5. **Use separate credentials** for different projects/clients

### SSL Certificates
- Generated SSL certificates are automatically gitignored
- Self-signed certificates are for testing only
- Let's Encrypt certificates should be managed securely
- Never commit private keys to version control

## 📊 Data Handling

### Captured Data
- All form submissions are logged to `captured_data.txt`
- This file is automatically gitignored
- **Review and sanitize** captured data before sharing
- **Delete captured data** when testing is complete
- **Encrypt sensitive** captured data if long-term storage is needed

### Cloned Websites
- Cloned sites are automatically gitignored in `cloned_site/` directories
- May contain copyrighted content from target websites
- Should only be used in authorized testing environments
- Delete cloned content when testing is complete

## 🔍 Monitoring and Logging

### What Gets Logged
- Domain generation and checking activities
- API requests and responses (with sanitized credentials)
- Form submissions and user interactions
- SSL certificate generation and management
- Server access and error logs

### Log Security
- All log files are gitignored by default
- Logs may contain sensitive debugging information
- Review logs before sharing for troubleshooting
- Implement log rotation for long-running deployments

## 🚨 Incident Response

### If Credentials Are Compromised
1. **Immediately revoke** the compromised API key in OpenSRS control panel
2. **Generate new credentials** for continued testing
3. **Review access logs** for unauthorized usage
4. **Notify stakeholders** if client data may be affected
5. **Update documentation** with new security procedures

### If Sensitive Data Is Exposed
1. **Identify scope** of exposed information
2. **Secure or remove** exposed data immediately
3. **Notify affected parties** as required by law
4. **Document the incident** for future prevention
5. **Review and update** security procedures

## 🛠️ Security Best Practices

### Development
- Use virtual environments for Python dependencies
- Keep dependencies updated for security patches
- Review code changes for security implications
- Use static analysis tools to detect security issues
- Test in isolated environments only

### Deployment
- Use minimal permissions for service accounts
- Implement network segmentation for testing infrastructure
- Monitor resource usage for anomalies
- Implement backup and recovery procedures
- Document security architecture and procedures

### Maintenance
- Regularly update dependencies
- Monitor security advisories for used libraries
- Perform security reviews of configuration changes
- Test backup and recovery procedures
- Train team members on security best practices

## 📋 Security Checklist

Before each penetration test:
- [ ] Written authorization obtained and documented
- [ ] Target scope clearly defined and agreed upon
- [ ] Test environment configured and isolated
- [ ] Credentials configured with minimal necessary permissions
- [ ] Monitoring and logging enabled
- [ ] Incident response procedures reviewed
- [ ] Data handling procedures documented
- [ ] Legal and compliance requirements verified

After each penetration test:
- [ ] All test artifacts cleaned up
- [ ] Captured data reviewed and handled appropriately
- [ ] Cloned websites removed from systems
- [ ] Temporary domains released or transferred
- [ ] API credentials rotated if necessary
- [ ] Final report sanitized before sharing
- [ ] Lessons learned documented for future tests

## 📞 Reporting Security Issues

If you discover security vulnerabilities in TSquat itself:

1. **Do not** open a public GitHub issue
2. **Email security details** to the maintainers
3. **Provide detailed** reproduction steps
4. **Allow reasonable time** for response and fixing
5. **Follow responsible disclosure** practices

## 📚 Additional Resources

- [OWASP Penetration Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SANS Penetration Testing Resources](https://www.sans.org/white-papers/penetration-testing/)
- [OpenSRS Security Documentation](https://opensrs.com/security/)

---

Remember: **With great power comes great responsibility.** Use this tool ethically and legally.