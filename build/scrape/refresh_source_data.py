import urllib.request
import json
import ssl
import os
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.dirname(SCRIPT_DIR)
REPO_DIR = os.path.dirname(BUILD_DIR)
DATA_DIR = os.path.join(BUILD_DIR, "wp_data")
UPLOADS_DIR = os.path.join(REPO_DIR, "assets", "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

def fetch_url(url):
    print(f"Fetching: {url}")
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def download_file(url, local_path):
    if os.path.exists(local_path):
        print(f"File already exists, skipping: {local_path}")
        return True
    print(f"Downloading: {url} -> {local_path}")
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, context=ctx) as response:
            with open(local_path, "wb") as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return False

def main():
    # 1. Fetch Pages
    pages_data = fetch_url("https://jamesvalcourt.com/wp-json/wp/v2/pages?per_page=100")
    if pages_data:
        pages = json.loads(pages_data.decode('utf-8'))
        with open(os.path.join(DATA_DIR, "pages.json"), "w") as f:
            json.dump(pages, f, indent=2)
        print(f"Saved {len(pages)} pages to pages.json")

    # 2. Fetch Posts
    posts_data = fetch_url("https://jamesvalcourt.com/wp-json/wp/v2/posts?per_page=100")
    if posts_data:
        posts = json.loads(posts_data.decode('utf-8'))
        with open(os.path.join(DATA_DIR, "posts.json"), "w") as f:
            json.dump(posts, f, indent=2)
        print(f"Saved {len(posts)} posts to posts.json")

    # 3. Fetch Media
    media_data = fetch_url("https://jamesvalcourt.com/wp-json/wp/v2/media?per_page=100")
    if media_data:
        media_list = json.loads(media_data.decode('utf-8'))
        with open(os.path.join(DATA_DIR, "media.json"), "w") as f:
            json.dump(media_list, f, indent=2)
        print(f"Saved {len(media_list)} media metadata items to media.json")

        # Download media files straight into the site's asset directory
        for media in media_list:
            source_url = media.get("source_url")
            if not source_url:
                continue
            # Example: https://www.jamesvalcourt.com/wp-content/uploads/2021/08/valcourt_CV.pdf
            # Local path: assets/uploads/2021/08/valcourt_CV.pdf
            parts = source_url.split("/wp-content/uploads/")
            if len(parts) > 1:
                rel_path = parts[1]
            else:
                rel_path = os.path.basename(source_url)

            local_path = os.path.join(UPLOADS_DIR, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            download_file(source_url, local_path)

    print("Refresh completed successfully!")

if __name__ == "__main__":
    main()
