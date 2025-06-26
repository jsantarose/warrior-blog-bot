import os
import openai
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("CLAUDE_API_KEY")

def call_openai(prompt):
    try:
        print("⚡ Using GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ GPT failed: {e}")
        return None

def call_claude(prompt):
    try:
        print("⚡ Using Claude fallback...")
        headers = {
            "Authorization": f"Bearer {claude_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "claude-3-opus-20240229",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 800
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"].strip()
    except Exception as e:
        print(f"❌ Claude failed: {e}")
        return None

def parse_blog(raw):
    lines = raw.strip().splitlines()

    if len(lines) < 5:
        title = f"Warrior Reflections on {datetime.utcnow().strftime('%A')}"
        slug = title.lower().replace(" ", "-")
        cats = [datetime.utcnow().strftime("%A")]
        tags = ["mindset", "warrior mindset", "Joseph Santarose"]
        body = raw.strip()
        return {
            "title": title,
            "slug": slug,
            "categories": cats,
            "tags": tags,
            "body": body,
            "image": None
        }

    title = lines[0].strip()
    slug = lines[1].split(":", 1)[1].strip() if ":" in lines[1] else title.lower().replace(" ", "-")
    cats = lines[2].split(":", 1)[1].split(",") if ":" in lines[2] else ["Mindset"]
    tags = lines[3].split(":", 1)[1].split(",") if ":" in lines[3] else ["Joseph Santarose"]
    body = "\n".join(lines[5:]).strip()

    return {
        "title": title,
        "slug": slug,
        "categories": [c.strip() for c in cats],
        "tags": [t.strip() for t in tags],
        "body": body,
        "image": None  # You can later add a DALL·E call or stock fallback here
    }

def create_post():
    prompt = (
        "Write a motivational blog post from the perspective of Joseph Santarose.\n"
        "Line 1: Title\n"
        "Line 2: Slug: slug-text\n"
        "Line 3: Categories: list,separated,by,commas\n"
        "Line 4: Tags: keyword1, keyword2\n"
        "Line 6 onward: Full blog post body.\n"
        "Theme: Warrior mindset, no excuses, daily fire."
    )

    raw = call_openai(prompt)
    if not raw:
        raw = call_claude(prompt)
    if not raw:
        print("🚫 Both AI calls failed — using fallback.")
        raw = (
            f"Warrior Mode Activated\n"
            f"Slug: warrior-mode-activated\n"
            f"Categories: Warrior, Mindset\n"
            f"Tags: joseph santarose, mindset, no excuses\n\n"
            f"When the tools fail, the warrior prevails.\n"
            f"Let your action be your proof. Show up and conquer.\n"
        )

    return parse_blog(raw)
