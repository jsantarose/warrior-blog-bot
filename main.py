from generator import create_post
from wordpress import post_to_wordpress

if __name__ == "__main__":
    print("⚔️ Generating warrior blog post...")
    post = create_post()
    print("📝 Posting to WordPress...")
    post_to_wordpress(post)
