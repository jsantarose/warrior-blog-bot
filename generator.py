import os
import openai
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

THEMES = {
    "Monday": "Resilience",
    "Tuesday": "Discipline",
    "Wednesday": "Strategy",
    "Thursday": "Dominance",
    "Friday": "Reflection",
    "Saturday": "Training Day",
    "Sunday": "Faith & Fire"
}

def gen_blog(theme):
    prompt = f"""Write a ~400-word blog post in a motivational, first-person voice by Joseph Santarose. 
The topic is: "{theme}".

Tone: warrior mindset, personal, bold, no fluff.
At the top of your response, include:
- Title
- Slug (dash-separated)
- Categories (comma-separated)
- Tags (comma-separated, include: mindset, warrior mindset, no quitting, Joseph Santarose)

Then add the blog body after a blank line.
Do not include quotes or markdown.
Do not repeat yourself.
"""

    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("⚠️ GPT failed. Using fallback:", e)
        return f"Joseph here. Even AI hits a wall — but I don’t quit. Today’s lesson on {theme} is still worth living out. Stay sharp."

def gen_image(theme):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Image.create(
            prompt=f"cinematic warrior training, {theme}, dramatic lighting, no text, dark and focused",
            n=1,
            size="1024x1024"
        )
        image_url = response["data"][0]["url"]
        image_data = requests.get(image_url).content

        # Validate image bytes
        if not image_data or len(image_data) < 10000:
            raise ValueError("Returned image data is too small or corrupt.")

        return image_data
    except Exception as e:
        print("⚠️ OpenAI image failed, using Unsplash fallback:", e)
        fallback_url = f"https://source.unsplash.com/1024x1024/?warrior,{theme}"
        return requests.get(fallback_url).content

def parse_blog(raw):
    lines = raw.strip().splitlines()
    title = lines[0].strip()
    slug = lines[1].split(":")[1].strip() if "Slug" in lines[1] else title.lower().replace(" ", "-")
    cats = lines[2].split(":")[1].split(",") if "Categories" in lines[2] else [datetime.utcnow().strftime("%A")]
    tags = lines[3].split(":")[1].split(",") if "Tags" in lines[3] else ["mindset", "warrior mindset", "Joseph Santarose"]
    body = "\n".join(lines[5:]).strip()
    return title, slug, [c.strip() for c in cats], [t.strip() for t in tags], body

def create_post():
    day = datetime.utcnow().strftime("%A")
    theme = THEMES[day]
    raw = gen_blog(theme)
    title, slug, cats, tags, body = parse_blog(raw)
    image = gen_image(theme)
    return {
        "title": title,
        "slug": slug,
        "categories": cats,
        "tags": tags,
        "body": body,
        "image": image
    }
