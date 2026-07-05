import json
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WP_DATA_DIR = os.path.join(SCRIPT_DIR, "wp_data")
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "base_template.html")

def load_json(filename):
    with open(os.path.join(WP_DATA_DIR, filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def load_template():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def clean_wp_html(html_content):
    if not html_content:
        return ""
    
    # 1. Replace WordPress upload URLs with relative local paths
    # Matches URLs like: https://www.jamesvalcourt.com/wp-content/uploads/2021/08/valcourt_CV.pdf
    # Or i0.wp.com CDN versions: https://i0.wp.com/www.jamesvalcourt.com/wp-content/uploads/...
    # Or query parameters: ?fit=... ?ssl=1
    pattern = r'https?://(?:i[0-9]\.wp\.com/)?(?:www\.)?jamesvalcourt\.com/wp-content/uploads/([^\s"\'\)>?#]+)'
    html_content = re.sub(pattern, r'/assets/uploads/\1', html_content)
    
    # Remove image size query variables from URLs
    html_content = re.sub(r'(/assets/uploads/[^\s"\'\)>?#]+)\?[^\s"\'>]*', r'\1', html_content)
    
    # 2. Rewrite same-domain page/post links to relative root links
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/contact/?', '/contact/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/cv/?', '/cv/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/writing/?', '/writing/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/blog/?', '/blog/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/fun/?', '/fun/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/idea-generator/?', '/idea-generator/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/money/?', '/money/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/ideation-workshop/?', '/ideation-workshop/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/fun/real-estate-jargon-cheat-sheet/?', '/fun/real-estate-jargon-cheat-sheet/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/fun/systems-biology-phrase-book/?', '/fun/systems-biology-phrase-book/', html_content)
    html_content = re.sub(r'https?://(?:www\.)?jamesvalcourt\.com/systematic-how-systems-biology-is-transforming-modern-medicine/?', '/systematic-how-systems-biology-is-transforming-modern-medicine/', html_content)
    
    # Rewrite WordPress post paths: e.g. https://www.jamesvalcourt.com/2019/03/19/...
    post_pattern = r'https?://(?:www\.)?jamesvalcourt\.com/(\d{4}/\d{2}/\d{2}/[^/\s"]+)/?'
    html_content = re.sub(post_pattern, r'/\1/', html_content)

    # 3. Clean up WordPress internal classes and helper attributes
    html_content = re.sub(r'\s*data-recalc-dims="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*decoding="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-attachment-id="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-permalink="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-orig-file="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-orig-size="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-comments-opened="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-image-meta="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-image-title="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-image-description="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-image-caption="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-medium-file="[^"]*"', '', html_content)
    html_content = re.sub(r'\s*data-large-file="[^"]*"', '', html_content)
    
    # Clean up empty paragraph tags or double breaks
    html_content = html_content.replace("<p></p>", "")
    html_content = html_content.replace("<p>&nbsp;</p>", "")
    
    return html_content.strip()

def render_template(template, title, description, content, nav_active="", page_class=""):
    # Render navigation actives
    nav_active_home = "active" if nav_active == "home" else ""
    nav_active_cv = "active" if nav_active == "cv" else ""
    nav_active_writing = "active" if nav_active == "writing" else ""
    nav_active_blog = "active" if nav_active == "blog" else ""
    nav_active_systematic = "active" if nav_active == "systematic" else ""
    nav_active_fun = "active" if nav_active == "fun" else ""
    nav_active_contact = "active" if nav_active == "contact" else ""
    
    html = template.replace("{{title}}", title)
    html = html.replace("{{description}}", description)
    html = html.replace("{{content}}", content)
    html = html.replace("{{page_class}}", page_class)
    html = html.replace("{{nav_active_home}}", nav_active_home)
    html = html.replace("{{nav_active_cv}}", nav_active_cv)
    html = html.replace("{{nav_active_writing}}", nav_active_writing)
    html = html.replace("{{nav_active_blog}}", nav_active_blog)
    html = html.replace("{{nav_active_systematic}}", nav_active_systematic)
    html = html.replace("{{nav_active_fun}}", nav_active_fun)
    html = html.replace("{{nav_active_contact}}", nav_active_contact)
    
    return html

def write_html_file(relative_dir, content):
    full_dir = os.path.join(WORKSPACE_DIR, relative_dir.strip("/"))
    os.makedirs(full_dir, exist_ok=True)
    file_path = os.path.join(full_dir, "index.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {file_path}")

def format_date(iso_date):
    # E.g. "2019-04-11T20:28:12" -> "April 11, 2019"
    try:
        dt = datetime.strptime(iso_date.split('T')[0], "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except Exception:
        return iso_date

def build_home_page(page, template):
    content = page.get("content", {}).get("rendered", "")
    content = clean_wp_html(content)
    
    # Extract the main photo of James (the large JPEG file)
    # Homepage content has: <p><a href="..."><img class="..." src="/assets/uploads/2018/02/...jpg"></a></p>
    # Let's extract this photo url, and put it in a clean two-column grid.
    img_match = re.search(r'<img[^>]+src="([^"]+)"', content)
    image_html = ""
    if img_match:
        img_url = img_match.group(1)
        image_html = f'<div class="welcome-image"><img src="{img_url}" alt="James Valcourt"></div>'
        # Strip the paragraph containing this image from the content text
        content = re.sub(r'<p>\s*<a[^>]+>\s*<img[^>]+>\s*</a>\s*</p>', '', content)
        content = re.sub(r'<p>\s*<img[^>]+>\s*</p>', '', content)
        content = re.sub(r'<img[^>]+>', '', content) # Fallback clean
    
    welcome_content = f"""
    <div class="container welcome-grid">
        {image_html}
        <div class="welcome-content">
            <h1>James Valcourt</h1>
            <span class="subheading">Scientist / garlic enthusiast</span>
            <div class="welcome-text">
                {content}
            </div>
        </div>
    </div>
    """
    
    html = render_template(
        template,
        title="Welcome",
        description="Official website of James Valcourt - Scientist & writer.",
        content=welcome_content,
        nav_active="home",
        page_class="home-page"
    )
    
    # Save directly to workspace index.html (root level)
    root_index = os.path.join(WORKSPACE_DIR, "index.html")
    with open(root_index, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated: {root_index}")

def build_cv_page(page, template):
    # WP Content: <p><a href="...">View PDF</a><div class="wp-block-pdfemb-pdf-embedder-viewer">...
    # We will replace with a modern, elegant view link and responsive PDF iframe embedding.
    pdf_url = "/assets/uploads/2021/08/valcourt_CV.pdf"
    
    content = f"""
    <div class="container">
        <h1>Curriculum Vitae</h1>
        <p><a href="{pdf_url}" class="btn" download>Download CV (PDF)</a></p>
        
        <div class="pdf-viewer">
            <iframe src="{pdf_url}" width="100%" height="800px" style="border: none;">
                This browser does not support embedding PDFs. Please download the PDF file to view it.
            </iframe>
        </div>
    </div>
    """
    
    html = render_template(
        template,
        title="CV",
        description="James Valcourt CV - Professional and Academic Background.",
        content=content,
        nav_active="cv",
        page_class="cv-page"
    )
    write_html_file("cv", html)

def build_contact_page(page, template):
    content = page.get("content", {}).get("rendered", "")
    content = clean_wp_html(content)
    
    # Parse contact methods out of paragraphs to format them beautifully in cards
    # Content format:
    # Email: valcourt [at] alumni [dot] harvard [dot] edu
    # Twitter: <a href="...">@jrvalcourt</a>
    # Bicycle courier: ...
    # Trebuchet: ...
    # What3Words: ...
    # We will format this into a gorgeous grid list.
    
    lines = content.split("<br />")
    clean_lines = []
    for line in lines:
        cleaned = re.sub('<[^<]+?>', '', line).strip() # strip tags
        if cleaned:
            clean_lines.append(cleaned)
            
    contact_items_html = ""
    
    # Hardcoded beautiful rendering based on parsed output
    methods = [
        {"title": "Email", "val": "valcourt [at] alumni [dot] harvard [dot] edu"},
        {"title": "BlueSky", "val": "@jrvalcourt.bsky.social", "link": "https://bsky.app/profile/jrvalcourt.bsky.social"},
        {"title": "Bicycle Courier", "val": "D.E. Shaw Research, 120 W 45th St, 39th Floor, New York, NY 10036"},
        {"title": "Trebuchet", "val": "40.757099, -73.983704"},
        {"title": "What3Words", "val": "plants.agrees.rarely", "link": "https://what3words.com/plants.agrees.rarely"}
    ]

    for m in methods:
        val_str = f'<a href="{m["link"]}" target="_blank">{m["val"]}</a>' if "link" in m else f'<span>{m["val"]}</span>'
        contact_items_html += f"""
        <li>
            <strong>{m["title"]}</strong>
            {val_str}
        </li>
        """
        
    contact_content = f"""
    <div class="container">
        <h1>Contact</h1>
        <p>You can reach me via the following channels:</p>
        <ul class="contact-info">
            {contact_items_html}
        </ul>
    </div>
    """
    
    html = render_template(
        template,
        title="Contact",
        description="Get in touch with James Valcourt.",
        content=contact_content,
        nav_active="contact",
        page_class="contact-page"
    )
    write_html_file("contact", html)

def build_fun_page(page, template):
    # WP Content contains the list of fun pages. We will display it as cards.
    cards_data = [
        {
            "title": "Idea Generator",
            "desc": "A random generator of cool scientific projects using click chemistry, optogenetics, blockchain, and climate change.",
            "url": "/idea-generator/"
        },
        {
            "title": "Chardonnay Genomics",
            "desc": "satirical wine genomics preference prediction company: From Bases to Booze.",
            "url": "/jcraigvintner/chardonnay_genomics.html"
        },
        {
            "title": "Systems Biology Phrase Book",
            "desc": "Translating systems biology jargon into plain English.",
            "url": "/fun/systems-biology-phrase-book/"
        },
        {
            "title": "Real Estate Jargon Cheat Sheet",
            "desc": "Deciphering agent listings: 'cozy' means small, 'rustic' means falling apart.",
            "url": "/fun/real-estate-jargon-cheat-sheet/"
        }
    ]
    
    cards_html = ""
    for c in cards_data:
        cards_html += f"""
        <div class="card">
            <h3>{c["title"]}</h3>
            <p>{c["desc"]}</p>
            <a href="{c["url"]}" class="card-link">Launch Project &rarr;</a>
        </div>
        """
        
    content = f"""
    <div class="container">
        <h1>Fun Projects & Satire</h1>
        <p>A collection of side projects, satirical worksheets, and jargon cheat sheets:</p>
        
        <div class="grid-2col" style="margin-top: 2rem;">
            {cards_html}
        </div>
    </div>
    """
    
    html = render_template(
        template,
        title="Fun",
        description="Fun projects, generators, and satirical phrasebooks by James Valcourt.",
        content=content,
        nav_active="fun",
        page_class="fun-page"
    )
    write_html_file("fun", html)

def build_idea_generator_page(page, template):
    content = page.get("content", {}).get("rendered", "")
    content = clean_wp_html(content)
    
    # The script details from the WordPress page are embedded here. 
    # We will build a premium styled container for the dynamic phrase generator.
    generator_content = """
    <div class="container" style="max-width: 650px;">
        <h1 style="text-align: center;">Idea Generator</h1>
        <p style="text-align: center; color: var(--text-muted);">Feeling stuck? Generate a groundbreaking new research proposal at the click of a button.</p>
        
        <div class="generator-box">
            <p id="phrase">Loading generator...</p>
            <p id="x"></p>
            <p id="for" style="margin: 0.5rem 0;">for</p>
            <p id="y"></p>
            
            <button type="button" class="btn" style="margin-top: 2.5rem;" onclick="update(phrase[randomInt(phrase.length - 1)], tech[randomInt(tech.length - 1)], app[randomInt(app.length - 1)])">Generate Idea</button>
        </div>
    </div>
    
    <script>
    var phrase = ["Wouldn't it be cool if there were...", "Have you thought about...", "What about..."];
    var tech = ["CRISPR", "Uber", "RNA-seq", "single-cell techniques", "click chemistry", "microscopy", "optogenetics", "flow cytometry", "compressed sensing", "big data", "cryptography", "quantum dots", "barcoding", "mass spec", "deep learning", "a good animal model", "-omics", "drones", "robotics", "biological sensors", "automation", "MRI", "deconvolution", "a comprehensive database", "gene drives", "a peer-to-peer solution", "crowdsourcing", "3D printing", "high-throughput screens", "NMR", "Bayesian inference", "the blockchain", "directed evolution", "wearables", "new funding models", "nanoparticles", "wireless"];
    var app  = ["the environment", "climate change", "batteries", "recycling", "the brain", "transportation", "the government", "stem cell therapeutics", "antibiotic resistance", "orphan diseases", "Alzheimer's", "vaccine delivery", "food deserts", "blindness", "organ transplantation", "terrorism prediction", "agricultural productivity", "missile defense", "radiation detection", "headaches", "opioid addiction", "PTSD", "rare mineral supply problems", "autism", "hazardous waste disposal", "energy generation", "drug discovery", "bioterrorism defense", "paralyzed patients", "exoplanet detection", "protein structure prediction", "obesity", "carbon capture", "traffic", "clean water availability", "green chemical synthesis", "drug manufacturing", "energy storage", "pollution remediation", "cancer", "heart disease", "stress management", "aging", "the microbiome", "the post-scarcity economy", "agricultural pests", "demographic challenges"];
    
    function update(phrase, a, b) {
        document.getElementById("phrase").innerHTML = phrase;
        document.getElementById("x").innerHTML = a;
        document.getElementById("y").innerHTML = b;
    }
    
    function randomInt(max) {
        return Math.floor(Math.random() * (max + 1));
    }
    
    document.getElementById("for").innerHTML = "for";
    update(phrase[randomInt(phrase.length - 1)], tech[randomInt(tech.length - 1)], app[randomInt(app.length - 1)]);
    </script>
    """
    
    html = render_template(
        template,
        title="Idea Generator",
        description="Generate novel, randomized systems biology and bioengineering project ideas instantly.",
        content=generator_content,
        nav_active="fun",
        page_class="generator-page"
    )
    write_html_file("idea-generator", html)

def build_systematic_page(page, template):
    content = page.get("content", {}).get("rendered", "")
    content = clean_wp_html(content)
    
    # We will format the systematic page beautifully with the cover image in a left column
    # Cover path: /assets/uploads/2017/01/cover.jpg
    cover_img_url = "/assets/uploads/2017/01/cover.jpg"
    
    book_content = f"""
    <div class="container book-layout">
        <div class="book-cover">
            <img src="{cover_img_url}" alt="Systematic Book Cover">
        </div>
        <div class="book-details">
            <h1>Systematic</h1>
            <h3 style="color: var(--text-muted); font-weight: 400; margin-top: 0;">How Systems Biology is Transforming Modern Medicine</h3>
            <div style="margin-top: 1.5rem;">
                {content}
            </div>
        </div>
    </div>
    """
    
    html = render_template(
        template,
        title="Systematic Book",
        description="Systematic: How Systems Biology is Transforming Modern Medicine - book by James Valcourt.",
        content=book_content,
        nav_active="systematic",
        page_class="book-page"
    )
    write_html_file("systematic-how-systems-biology-is-transforming-modern-medicine", html)

def build_generic_page(page, template):
    slug = page.get("slug")
    title = page.get("title", {}).get("rendered", "")
    content = page.get("content", {}).get("rendered", "")
    content = clean_wp_html(content)
    
    page_content = f"""
    <div class="container">
        <h1>{title}</h1>
        <div style="margin-top: 2rem;">
            {content}
        </div>
    </div>
    """
    
    html = render_template(
        template,
        title=title,
        description=f"{title} - James Valcourt",
        content=page_content,
        nav_active="writing" if slug == "writing" else "fun",
        page_class=f"generic-page page-{slug}"
    )
    
    # Handles writing, money, fun sub-pages (real estate list, systems phrase book, ideation workshop)
    if slug in ["real-estate-jargon-cheat-sheet", "systems-biology-phrase-book"]:
        write_html_file(f"fun/{slug}", html)
    else:
        write_html_file(slug, html)

def build_blog_index(posts, template):
    posts_list_html = ""
    for post in posts:
        title = post.get("title", {}).get("rendered", "")
        date = format_date(post.get("date", ""))
        excerpt = post.get("excerpt", {}).get("rendered", "")
        excerpt = clean_wp_html(excerpt)
        
        # Build path based on date structure: /YYYY/MM/DD/slug/
        date_obj = datetime.strptime(post.get("date").split('T')[0], "%Y-%m-%d")
        post_url = date_obj.strftime("/%Y/%m/%d/") + post.get("slug") + "/"
        
        posts_list_html += f"""
        <article class="blog-summary">
            <span class="post-meta">{date}</span>
            <h2><a href="{post_url}">{title}</a></h2>
            <div class="entry-summary">
                {excerpt}
            </div>
            <a href="{post_url}" class="read-more">Read More &rarr;</a>
        </article>
        """
        
    blog_content = f"""
    <div class="container" style="max-width: 720px;">
        <h1 style="margin-bottom: 3rem; text-align: center;">News & Blog</h1>
        <div class="blog-list">
            {posts_list_html}
        </div>
    </div>
    """
    
    html = render_template(
        template,
        title="Blog",
        description="Thoughts, updates, and articles by James Valcourt.",
        content=blog_content,
        nav_active="blog",
        page_class="blog-index"
    )
    write_html_file("blog", html)

def build_blog_post(post, template):
    title = post.get("title", {}).get("rendered", "")
    date = format_date(post.get("date", ""))
    content = post.get("content", {}).get("rendered", "")
    content = clean_wp_html(content)
    slug = post.get("slug")
    
    # Format date folders: /YYYY/MM/DD/slug/
    date_obj = datetime.strptime(post.get("date").split('T')[0], "%Y-%m-%d")
    relative_dir = date_obj.strftime("%Y/%m/%d/") + slug
    
    post_html_content = f"""
    <article class="container">
        <header class="post-header">
            <span class="post-meta">{date}</span>
            <h1>{title}</h1>
        </header>
        <div class="post-content">
            {content}
        </div>
    </article>
    """
    
    html = render_template(
        template,
        title=title,
        description=f"Blog post: {title}",
        content=post_html_content,
        nav_active="blog",
        page_class="blog-post"
    )
    write_html_file(relative_dir, html)

def main():
    print("Loading datasets...")
    pages = load_json("pages.json")
    posts = load_json("posts.json")
    template = load_template()
    
    print("\n--- GENERATING PAGES ---")
    for page in pages:
        slug = page.get("slug")
        if slug == "home":
            build_home_page(page, template)
        elif slug == "cv":
            build_cv_page(page, template)
        elif slug == "contact":
            build_contact_page(page, template)
        elif slug == "fun":
            build_fun_page(page, template)
        elif slug == "idea-generator":
            build_idea_generator_page(page, template)
        elif slug == "systematic-how-systems-biology-is-transforming-modern-medicine":
            build_systematic_page(page, template)
        else:
            build_generic_page(page, template)
            
    print("\n--- GENERATING POSTS ---")
    for post in posts:
        build_blog_post(post, template)
        
    print("\n--- GENERATING BLOG ARCHIVE ---")
    # Sort posts by date descending
    posts.sort(key=lambda x: x.get("date", ""), reverse=True)
    build_blog_index(posts, template)
    
    print("\nStatic compilation completed successfully!")

if __name__ == "__main__":
    main()
