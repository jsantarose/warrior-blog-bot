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
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=800,
            temperature=0.8,
        )
        return response.choices[0].text.strip()
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
        # fallback structure if not formatted well
        title = f"Warrior Reflections on {datetime.utcnow().strftime('%A')}"
        slug = title.lower().replace(" ", "-")
        cats = [datetime.utcnow().strftime("%A")]
        tags = ["mindset", "warrior mindset", "Joseph Santarose"]
        body = raw.strip()
        return title, slug, cats, tags, body

    title = lines[0].strip()
    slug = lines[1].split(":", 1)[1].strip() if ":" in lines[1] else title.lower().replace(" ", "-")
    cats = lines[2].split(":", 1)[1].split(",") if ":" in lines[2] else [datetime.utcnow().strftime("%A")]
    tags = lines[3].split(":", 1)[1].split(",") if ":" in lines[3] else ["mindset", "warrior mindset", "Joseph Santarose"]
    body = "\n".join(lines[5:]).strip()

    return title, slug, [c.strip() for c in cats], [t.strip() for t in tags], body

def create_post():
    prompt = (
        "Write a motivational blog post from the perspective of Joseph Santarose. "
        "Structure it like this:\n\n"
        "Title: (on line 1)\n"
        "Slug: (on line 2)\n"
        "Categories: (on line 3)\n"
        "Tags: (on line 4)\n"
        "Body:\n(line 6 and onward)\n"
        "Focus on warrior mindset, no excuses, discipline, and daily fire."
    )

    raw = call_openai(prompt)
    if not raw:
        raw = call_claude(prompt)
    if not raw:
        print("🚫 Both AI calls failed — using hardcoded fallback.")
        raw = (
            f"Warrior Mindset Activated\n"
            f"Slug: warrior-mindset-activated\n"
            f"Categories: Mindset, Warrior Life\n"
            f"Tags: mindset, Joseph Santarose, no excuses\n\n"
            f"Even when the tools fail, the warrior moves forward.\n"
            f"You don’t need perfect conditions to win.\n"
            f"You need relentless action.\n"
        )

    return parse_blog(raw)

