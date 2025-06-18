import pytest
import sys
import os

# Add the parent directory to sys.path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.domain_generator import DomainGenerator

class TestDomainGenerator:
    
    def setup_method(self):
        """Setup method run before each test"""
        self.generator = DomainGenerator()
    
    def test_extract_domain_parts(self):
        """Test domain part extraction"""
        # Test simple domain
        name, tld = self.generator.extract_domain_parts("example.com")
        assert name == "example"
        assert tld == ".com"
        
        # Test with protocol
        name, tld = self.generator.extract_domain_parts("https://example.com")
        assert name == "example"
        assert tld == ".com"
        
        # Test subdomain (should extract main domain)
        name, tld = self.generator.extract_domain_parts("www.example.com")
        assert name == "www.example"
        assert tld == ".com"
    
    def test_is_valid_domain(self):
        """Test domain validation"""
        # Valid domains
        assert self.generator.is_valid_domain("example.com") == True
        assert self.generator.is_valid_domain("test123.org") == True
        assert self.generator.is_valid_domain("my-site.net") == True
        
        # Invalid domains
        assert self.generator.is_valid_domain("") == False
        assert self.generator.is_valid_domain("example") == False  # No TLD
        assert self.generator.is_valid_domain(".com") == False  # No name
        assert self.generator.is_valid_domain("example.xyz") == False  # Invalid TLD
        assert self.generator.is_valid_domain("-example.com") == False  # Starts with hyphen
        assert self.generator.is_valid_domain("example-.com") == False  # Ends with hyphen
        assert self.generator.is_valid_domain("ex--ample.com") == False  # Double hyphen
        assert self.generator.is_valid_domain("123456.com") == False  # Purely numeric
        assert self.generator.is_valid_domain("sub.example.com") == False  # Contains subdomain
        assert self.generator.is_valid_domain("example.ftp.com") == False  # Invalid structure
        assert self.generator.is_valid_domain("ftp.example.com") == False  # Subdomain
    
    def test_character_substitution(self):
        """Test character substitution generates valid domains"""
        variants = self.generator.character_substitution("example.com")
        
        # Should generate some variants
        assert len(variants) > 0
        
        # All variants should be valid
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
        
        # Should not include original domain
        assert "example.com" not in variants
    
    def test_character_deletion(self):
        """Test character deletion generates valid domains"""
        variants = self.generator.character_deletion("example.com")
        
        # Should generate variants
        assert len(variants) > 0
        
        # All variants should be valid
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
        
        # Should include things like "exampl.com", "exmple.com", etc.
        assert "exampl.com" in variants
    
    def test_character_transposition(self):
        """Test character transposition generates valid domains"""
        variants = self.generator.character_transposition("example.com")
        
        # Should generate variants
        assert len(variants) > 0
        
        # All variants should be valid
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
        
        # Should include transposed characters like "exmaple.com"
        assert "exmaple.com" in variants
    
    def test_tld_variations(self):
        """Test TLD variations generates valid domains"""
        variants = self.generator.tld_variations("example.com")
        
        # Should generate variants
        assert len(variants) > 0
        
        # All variants should be valid
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
        
        # Should include other TLDs
        assert "example.net" in variants
        assert "example.org" in variants
        
        # Should not include original TLD
        assert "example.com" not in variants
    
    def test_subdomain_insertion_fixed(self):
        """Test that subdomain insertion creates valid registrable domains"""
        variants = self.generator.subdomain_insertion("example.com")
        
        # Should generate variants
        assert len(variants) > 0
        
        # All variants should be valid
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
        
        # Should create domains like "wwwexample.com", "examplemail.com"
        # NOT "www.example.com" (which is a subdomain, not registrable)
        valid_examples = ["wwwexample.com", "examplemail.com", "ftpexample.com"]
        invalid_examples = ["www.example.com", "ftp.example.com", "mail.example.com"]
        
        for valid in valid_examples:
            if valid in variants:
                assert self.generator.is_valid_domain(valid)
        
        for invalid in invalid_examples:
            assert invalid not in variants
    
    def test_homophone_replacement(self):
        """Test homophone replacement"""
        variants = self.generator.homophone_replacement("fortwo.com")
        
        # All variants should be valid
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
        
        # Should replace homophones
        if variants:  # Only test if we have variants
            assert "for2.com" in variants or "4two.com" in variants
    
    def test_generate_all_variants_filtered(self):
        """Test that generate_all_variants only returns valid domains"""
        variants = self.generator.generate_all_variants("example.com", max_variants=20)
        
        # Should generate some variants
        assert len(variants) > 0
        assert len(variants) <= 20
        
        # ALL variants should be valid
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
        
        # Should not include original domain
        assert "example.com" not in variants
        
        # Should not include any subdomain-style domains
        for variant in variants:
            assert "." not in variant.split(".")[0], f"Subdomain-style domain generated: {variant}"
    
    def test_character_insertion_limits(self):
        """Test that character insertion respects length limits"""
        # Test with a long domain name
        long_domain = "verylongdomainname.com"
        variants = self.generator.character_insertion(long_domain)
        
        # All variants should be valid (respecting length limits)
        for variant in variants:
            assert self.generator.is_valid_domain(variant), f"Invalid domain generated: {variant}"
            name_part = variant.split(".")[0]
            assert len(name_part) <= 63, f"Domain name too long: {variant}"
    
    def test_no_invalid_tlds(self):
        """Test that no invalid TLDs are generated"""
        variants = self.generator.generate_all_variants("example.com", max_variants=50)
        
        for variant in variants:
            name, tld = self.generator.extract_domain_parts(variant)
            assert tld in self.generator.valid_tlds, f"Invalid TLD in domain: {variant}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])