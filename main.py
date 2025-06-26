from generator import create_post
from wordpress import post_to_wordpress

def main():
    print("⚙️ Generating warrior blog post...")
    post = create_post()

    if not post:
        print("🚫 Failed to generate post.")
        return

    if not post.get("body") or len(post["body"]) < 100:
        print("🚫 Post body is too short. Skipping.")
        return

    print("🚀 Posting to WordPress...")
    success = post_to_wordpress(post)

    if success:
        print("✅ Post published successfully!")
    else:
        print("❌ Failed to publish post.")

if __name__ == "__main__":
    main()
