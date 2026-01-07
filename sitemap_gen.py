import os
import random
import string
import datetime
import re

def get_domain_from_cname():
    """Reads the domain name from the CNAME file."""
    try:
        with open('CNAME', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Warning: CNAME file not found. Using default.")
        return "example.com"

def get_all_html_files():
    """Finds all HTML files in the repository."""
    html_files = []
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith('.html'):
                full_path = os.path.join(root, file).replace('./', '')
                if full_path.endswith('index.html'):
                    url_path = full_path[:-10]
                else:
                    url_path = full_path
                html_files.append(url_path)
    return html_files

def generate_random_name(length=12):
    """Generates a random string for sitemap filenames."""
    letters = string.ascii_lowercase + string.digits
    return 'sm_' + ''.join(random.choice(letters) for i in range(length)) + '.xml'

def create_sitemap_chunk(urls, domain, filename):
    """Creates a single sitemap file for a list of URLs."""
    content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    for url in urls:
        # Avoid double slashes
        clean_url = url.lstrip('/')
        full_url = f"https://{domain}/{clean_url}"
        content += f'  <url>\n    <loc>{full_url}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.8</priority>\n  </url>\n'
    
    content += '</urlset>'
    with open(filename, 'w') as f:
        f.write(content)

def get_existing_sitemaps():
    """Finds already existing sitemap files in the directory."""
    # Matches files like sm_abc123.xml
    pattern = re.compile(r'^sm_[a-z0-9]+\.xml$')
    return [f for f in os.listdir('.') if pattern.match(f)]

def create_main_index(sitemap_files, domain):
    """Creates/Updates the main sitemap.xml index file with ALL sitemaps."""
    content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    content += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Sort to keep the file organized
    for sm in sorted(list(set(sitemap_files))):
        content += f'  <sitemap>\n    <loc>https://{domain}/{sm}</loc>\n  </sitemap>\n'
    
    content += '</sitemapindex>'
    with open('sitemap.xml', 'w') as f:
        f.write(content)

def create_robots_txt(domain):
    """Creates a robots.txt file pointing to the main sitemap."""
    content = "User-agent: *\nAllow: /\n"
    content += f"\nSitemap: https://{domain}/sitemap.xml"
    with open('robots.txt', 'w') as f:
        f.write(content)

def main():
    domain = get_domain_from_cname()
    all_urls = get_all_html_files()
    
    # Configuration: Max URLs per sitemap
    MAX_URLS = 2000
    
    # 1. Get current existing sitemaps before creating new ones
    existing_sitemaps = get_existing_sitemaps()
    
    # 2. Split current site HTML files into chunks
    chunks = [all_urls[i:i + MAX_URLS] for i in range(0, len(all_urls), MAX_URLS)]
    
    new_sitemap_filenames = []
    for chunk in chunks:
        new_name = generate_random_name()
        create_sitemap_chunk(chunk, domain, new_name)
        new_sitemap_filenames.append(new_name)
        print(f"Generated new chunk: {new_name}")

    # 3. Combine old and new sitemaps for the index
    total_sitemaps = existing_sitemaps + new_sitemap_filenames
    
    # 4. Update the main index file
    create_main_index(total_sitemaps, domain)
    print(f"Updated sitemap.xml with {len(total_sitemaps)} total sitemap files.")

    # 5. Ensure robots.txt is there
    create_robots_txt(domain)

if __name__ == "__main__":
    main()
