import os
import sys
import base64
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.print_page_options import PrintOptions
from webdriver_manager.chrome import ChromeDriverManager

PORT = 5051

def start_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()

def generate_pdf(html_rel_path, output_filename):
    # Determine absolute paths
    base_dir = os.getcwd()
    output_path = os.path.join(base_dir, output_filename)
    
    # Start HTTP server in a daemon thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)

    # Construct URL (assuming script runs from root)
    # html_rel_path is "static/ui/guide.html"
    file_url = f"http://localhost:{PORT}/{html_rel_path}"
    print(f"Target URL: {file_url}")

    # Configure Headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=0")  # Enable logs

    driver = None
    try:
        print("Initializing Chrome Driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("Loading page...")
        driver.get(file_url)
        
        # Give it time to render CSS and load images
        time.sleep(8) 

        print(f"Page Title: {driver.title}")
        
        # Print Browser Console Logs
        logs = driver.get_log('browser')
        for log in logs:
            print(f"BROWSER LOG: {log}")
        
        # Configure PDF options
        print_options = PrintOptions()
        print_options.background = True  # Print background graphics/colors
        print_options.shrink_to_fit = True
        
        print("Printing to PDF...")
        pdf = driver.print_page(print_options)
        
        # Handle different return types
        if hasattr(pdf, 'content'):
            pdf_base64 = pdf.content
        else:
            pdf_base64 = pdf

        # Decoded content
        pdf_bytes = base64.b64decode(pdf_base64)
        
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
            
        print(f"Successfully generated PDF: {output_path}")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()
        # Daemon thread will be killed when main process exits

if __name__ == "__main__":
    html_source = "static/ui/guide.html"
    temp_html = "static/ui/temp_guide.html"
    pdf_output = "RelayBell_User_Manual.pdf"
    
    print(f"CWD: {os.getcwd()}")
    
    # Create a temporary HTML file without auth.js to avoid redirect
    try:
        with open(html_source, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remove auth script and toolbar
        content = content.replace('<script defer src="auth.js"></script>', '<!-- auth.js removed for PDF -->')
        content = content.replace('id="auth-toolbar"', 'id="auth-toolbar" style="display:none;"')
        
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Created temporary file {temp_html} for PDF generation.")
        
        print(f"Starting PDF generation for {temp_html}...")
        success = generate_pdf(temp_html, pdf_output)
        
    finally:
        # Cleanup
        if os.path.exists(temp_html):
            os.remove(temp_html)
            print(f"Removed temporary file {temp_html}")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
