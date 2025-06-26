import os
import requests
import base64

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

def post_to_wordpress(post):
    auth = (WP_USERNAME, WP_APP_PASSWORD)

    # Upload the image
    media_headers = {
        'Content-Disposition': 'attachment; filename=featured.jpg',
        'Content-Type': 'image/jpeg'
    }

    media_response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        headers=media_headers,
        data=post["image"],
        auth=auth
    )

    if media_response.status_code != 201:
        print("Image upload failed:", media_response.text)
        return

    media_id = media_response.json().get("id")

    # Create the blog post
    data = {
        "title": post["title"],
        "slug": post["slug"],
        "content": post["body"],
        "status": "publish",
        "featured_media": media_id,
        "tags": post["tags"],
        "categories": post["categories"]
    }

    headers = {
        "Content-Type": "application/json"
    }

    post_response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",

