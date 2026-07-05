import os
import re

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPECTED_PATHS = [
    "index.html",
    "cv/index.html",
    "writing/index.html",
    "blog/index.html",
    "contact/index.html",
    "fun/index.html",
    "idea-generator/index.html",
    "systematic-how-systems-biology-is-transforming-modern-medicine/index.html",
    "fun/real-estate-jargon-cheat-sheet/index.html",
    "fun/systems-biology-phrase-book/index.html",
    "jcraigvintner/chardonnay_genomics.html",
    "assets/css/style.css",
]

def scan_for_broken_assets(file_path):
    print(f"Auditing file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Matches src="..." and href="..." references pointing to /assets/ or local relative assets
    # E.g. src="/assets/uploads/2018/02/pic.jpg"
    assets = re.findall(r'(?:src|href)=["\'](/assets/uploads/[^\s"\'#>?]+)["\']', content)
    assets += re.findall(r'(?:src|href)=["\'](/assets/css/[^\s"\'#>?]+)["\']', content)
    
    # Also check local relative assets in jcraigvintner folder
    if "jcraigvintner" in file_path:
        local_assets = re.findall(r'(?:src|href)=["\'](chardonnay_logo\.png|j_craig_vintner\.jpg)["\']', content)
        for la in local_assets:
            full_la_path = os.path.join(WORKSPACE_DIR, "jcraigvintner", la)
            if not os.path.exists(full_la_path):
                print(f"  [ERROR] Missing local asset: {full_la_path}")
                return False
                
    broken_count = 0
    for asset in set(assets):
        # Translate to local absolute path
        local_path = os.path.join(WORKSPACE_DIR, asset.lstrip("/"))
        if not os.path.exists(local_path):
            print(f"  [ERROR] Broken resource link: {asset} (expected at {local_path})")
            broken_count += 1
            
    return broken_count == 0

def main():
    print("=== STARTING SITE INTEGRITY AUDIT ===")
    
    # 1. Check expected paths
    all_ok = True
    for rel_path in EXPECTED_PATHS:
        full_path = os.path.join(WORKSPACE_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"[ERROR] Missing file: {full_path}")
            all_ok = False
        else:
            print(f"[OK] File exists: {rel_path}")
            
    # 2. Audit links in all generated html files
    print("\n=== AUDITING RESOURCE LINKS ===")
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        # Exclude git internals
        if ".git" in root:
            continue
        for file in files:
            if file.endswith(".html"):
                full_path = os.path.join(root, file)
                if not scan_for_broken_assets(full_path):
                    all_ok = False
                    
    if all_ok:
        print("\n[SUCCESS] Site audit completed successfully. All files exist and all resource links are valid!")
    else:
        print("\n[FAILURE] Site audit failed. Review errors above.")

if __name__ == "__main__":
    main()
