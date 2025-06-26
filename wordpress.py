import os
import requests
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

auth = (WP_USERNAME, WP_APP_PASSWORD)

def convert_image_to_base64(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"⚠️ Image conversion failed: {e}")
        return None

def upload_image(image_url):
    try:
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data)).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)

        media_headers = {
            "Content-Disposition": 'attachment; filename="featured.jpg"',
            "Content-Type": "image/jpeg"
        }

        media_response = requests.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            headers=media_headers,
            auth=auth,
            data=buffer
        )

        if media_response.status_code == 201:
            media_id = media_response.json()["id"]
            print(f"🖼️ Image uploaded. Media ID: {media_id}")
            return media_id
        else:
            print(f"⚠️ Image upload failed: {media_response.text}")
            return None
    except Exception as e:
        print(f"⚠️ Error uploading image: {e}")
        return None

def post_to_wordpress(post):
    print("📝 Posting to WordPress...")

    if not isinstance(post, dict):
        print("❌ Post format is invalid. Expected dictionary.")
        return

    title = post.get("title", "Untitled")
    slug = post.get("slug", "warrior-post")
    content = post.get("body", "")
    categories = post.get("categories", [])
    tags = post.get("tags", [])
    image_url = post.get("image", None)

    # Upload featured image if available
    featured_media_id = None
    if image_url:
        featured_media_id = upload_image(image_url)

    data = {
        "title": title,
        "slug": slug,
        "content": content,
        "status": "publish",
        "categories": [int(c) for c in categories if str(c).isdigit()],
        "tags": [int(t) for t in tags if str(t).isdigit()],
    }

    if featured_media_id:
        data["featured_media"] = featured_media_id

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        headers=headers,
        auth=auth,
        json=data
    )

    if response.status_code == 201:
        print("✅ Post published successfully!")
    else:
        print(f"❌ Post failed: {response.text}")
