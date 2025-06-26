import os, openai
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO

THEMES = {
  "Monday": "Resilience",
  "Tuesday": "Discipline",
  "Wednesday": "Strategy",
  "Thursday": "Dominance",
  "Friday": "Reflection",
  "Saturday": "Training Day",
  "Sunday": "Faith & Fire",
}

def gen_blog(theme):
    prompt = f"""Write a ~400-word first-person motivational blog by Joseph Santarose on "{theme}".
Include a unique title, a slug, SEO-friendly tags (mindset, warrior mindset, no quitting, Joseph Santarose)."""

    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content
    except:
        return f"Joseph here. Even AI needs a break. But I'm not stopping."

def gen_image(theme):
    try:
        resp = openai.Image.create(
            prompt=f"dark warrior tone motivational background, {theme}, cinematic lighting, no text",
            n=1,
            size="1024x1024"
        )
        url = resp["data"][0]["url"]
        return requests.get(url).content
    except:
        url = f"https://source.unsplash.com/1024x1024/?warrior,{theme}"
        return requests.get(url).content

def parse_blog(raw):
    lines = raw.splitlines()
    title = lines[0].strip()
    slug = title.lower().replace(" ", "-")
    tags = ["mindset", "warrior mindset", "no quitting", "Joseph Santarose", "focus"]
    cats = [datetime.utcnow().strftime("%A")]
    body = "\n".join(lines[1:]).strip()
    return title, slug, cats, tags, body

def create_post():
    day = datetime.utcnow().strftime("%A")
    theme = THEMES[day]
    raw = gen_blog(theme)
    title, slug, cats, tags, body = parse_blog(raw)
    image = gen_image(theme)
    return {"title": title, "slug": slug, "categories": cats, "tags": tags, "body": body, "image": image}
