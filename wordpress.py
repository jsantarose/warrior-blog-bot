import os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

auth = (WP_USERNAME, WP_APP_PASSWORD)

def get_or_create_term(name, endpoint):
    url = f"{WP_URL}/wp-json/wp/v2/{endpoint}?search={name}"
    response = requests.get(url, auth=auth)
    results = response.json()
    if results and isinstance(results, list):
        return results[0]['id']
    # Create if not found
    data = {"name": name}
    create_resp = requests.post(f"{WP_URL}/wp-json/wp/v2/{endpoint}", json=data, auth=auth)
    return create_resp.json().get("id")

def convert_terms_to_ids(terms, endpoint):
    ids = []
    for term in terms:
        ids.append(get_or_create_term(term, endpoint))
    return ids

def post_to_wordpress(post):
    if not post["image"] or len(post["image"]) < 100:
        print("❌ Image data is empty or too small.")
        return

    try:
        img = Image.open(BytesIO(post["image"])).convert("RGB")
        img_io = BytesIO()
        img.save(img_io, format="JPEG")
        img_io.seek(0)
    except Exception as e:
        print("❌ Image conversion failed:", e)
        return

    media_headers = {
        'Content-Disposition': 'attachment; filename=featured.jpg',
        'Content-Type': 'image/jpeg'
    }

    media_response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        headers=media_headers,
        data=img_io.read(),
        auth=auth
    )

    if media_response.status_code != 201:
        print("❌ Image upload failed:", media_response.text)
        return

    media_id = media_response.json().get("id")

    tag_ids = convert_terms_to_ids(post["tags"], "tags")
    category_ids = convert_terms_to_ids(post["categories"], "categories")

    data = {
        "title": post["title"],
        "slug": post["slug"],
        "content": post["body"],
        "status": "publish",
        "featured_media": media_id,
        "tags": tag_ids,
        "categories": category_ids
    }

    headers = {
        "Content-Type": "application/json"
    }

    post_response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        headers=headers,
        json=data,
        auth=auth
    )

    if post_response.status_code != 201:
        print("❌ Post failed:", post_response.text)
    else:
        print("✅ Blog post published:", post_response.json().get("link"))
