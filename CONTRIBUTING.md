# Contributing to TSquat

## 🔒 Security First

Before contributing to TSquat, please review our security guidelines:

1. **Read [SECURITY.md](SECURITY.md)** - Understand security requirements
2. **Never commit sensitive data** - Follow `.gitignore` rules strictly
3. **Test responsibly** - Only test against authorized targets
4. **Document security implications** - Note any security considerations in PRs

## 🚨 Pre-Commit Checklist

Before submitting any code:

### Security Verification
- [ ] No API keys, credentials, or secrets in code
- [ ] No hardcoded configuration values
- [ ] No captured penetration testing data
- [ ] No cloned website content
- [ ] All sensitive files are gitignored

### Code Quality
- [ ] All tests pass (`python -m pytest`)
- [ ] Code follows existing style conventions
- [ ] New features include appropriate tests
- [ ] Documentation updated for new functionality
- [ ] Error handling implemented properly

### Legal Compliance
- [ ] Code supports only authorized testing scenarios
- [ ] Appropriate warnings and disclaimers included
- [ ] No functionality that could enable malicious use
- [ ] Follows responsible disclosure practices

## 🧪 Testing Guidelines

### Unit Tests
- Add tests for new functionality in `tests/`
- Use mocking for external API calls
- Test both success and failure scenarios
- Include edge cases and validation tests

### Integration Tests
- Test with OpenSRS test environment only
- Never test against unauthorized targets
- Clean up all test artifacts
- Document test requirements and setup

### Security Tests
- Validate input sanitization
- Test credential handling
- Verify gitignore effectiveness
- Check for information disclosure

## 📝 Documentation Standards

### Code Documentation
- Clear function and class docstrings
- Inline comments for complex logic
- Type hints where appropriate
- Security considerations noted

### User Documentation
- Update README.md for new features
- Include usage examples
- Document security implications
- Provide troubleshooting guidance

### Security Documentation
- Update SECURITY.md for new security considerations
- Document any new sensitive data handling
- Include security configuration requirements
- Provide incident response guidance

## 🐛 Bug Reports

When reporting bugs:

1. **Check existing issues** first
2. **Provide reproduction steps** with sanitized examples
3. **Include environment information** (OS, Python version, etc.)
4. **Sanitize any logs** before including them
5. **Note security implications** if applicable

### Security Vulnerabilities

For security issues:
- **Do not** create public GitHub issues
- **Email maintainers** directly
- **Provide detailed** reproduction information
- **Follow responsible disclosure** timeline

## 🚀 Feature Requests

When requesting features:

1. **Explain the use case** for legitimate penetration testing
2. **Consider security implications** of the feature
3. **Provide implementation suggestions** if possible
4. **Note any legal or ethical considerations**

### Feature Categories

We welcome contributions in these areas:
- **Domain generation algorithms** - New typosquatting techniques
- **Content analysis** - Website fingerprinting and analysis
- **Deployment automation** - Easier setup and configuration
- **Security enhancements** - Better protection and validation
- **Testing improvements** - More comprehensive test coverage

We **do not** accept:
- Features designed for malicious use
- Functionality that bypasses security controls
- Tools for unauthorized access or exploitation
- Features that could harm legitimate services

## 🔧 Development Setup

### Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd tsquat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration (test environment only)
cp config.example ~/.tsquat_config
# Edit ~/.tsquat_config with test credentials
```

### Development Workflow
1. **Create feature branch** from main
2. **Implement changes** with tests
3. **Run full test suite** (`python -m pytest`)
4. **Update documentation** as needed
5. **Create pull request** with clear description

### Code Style
- Follow existing code conventions
- Use meaningful variable names
- Keep functions focused and small
- Include type hints for new code
- Document security considerations

## 📋 Pull Request Guidelines

### PR Description
- **Clear title** describing the change
- **Detailed description** of functionality
- **Security considerations** if applicable
- **Testing performed** and results
- **Documentation updates** included

### Review Process
1. **Automated checks** must pass
2. **Security review** for sensitive changes
3. **Code review** by maintainers
4. **Testing verification** in safe environment
5. **Documentation review** for completeness

### Merge Requirements
- All tests passing
- Code review approved
- Documentation updated
- Security considerations addressed
- No sensitive data included

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and professional
- Focus on constructive feedback
- Help newcomers learn secure practices
- Promote ethical security research
- Follow responsible disclosure practices

### Communication
- Use GitHub issues for bug reports and feature requests
- Join discussions with security mindset
- Share knowledge about secure development
- Respect confidentiality of security research
- Promote legitimate security testing practices

## 📚 Resources

- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Python Security Guidelines](https://python.org/dev/security/)
- [Penetration Testing Execution Standard](http://www.pentest-standard.org/)
- [OpenSRS API Documentation](https://domains.opensrs.guide/)

---

Thank you for contributing to TSquat responsibly! 🛡️