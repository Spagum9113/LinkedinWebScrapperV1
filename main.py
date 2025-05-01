
import os
import sys
import time
import pickle
import json
import openai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from openai import OpenAI


# File to store session cookies after login
COOKIE_FILE = "cookies.pkl"


def init_driver(load_cookies=True):
    """
    Initialize a headless Chrome browser. Optionally load saved cookies to stay logged in.
    """
    opts = Options()
    opts.headless = True  # run browser in background

    # This tells Selenium exactly “use this driver program”
    service = Service(ChromeDriverManager().install())

    # And this tells it “run with these options”
    driver = webdriver.Chrome(service=service, options=opts)

    if load_cookies and os.path.exists(COOKIE_FILE):
        # Navigate to LinkedIn to set the right domain for cookies
        driver.get("https://www.linkedin.com")
        # Load and add each cookie into the browser session
        cookies = pickle.load(open(COOKIE_FILE, "rb"))
        for c in cookies:
            driver.add_cookie(c)
    return driver


def login():
    """
    Automate LinkedIn login using credentials from environment variables.
    Saves cookies to COOKIE_FILE for future sessions.
    """
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        print("Error: Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables.")
        sys.exit(1)

    # Launch browser without loading cookies
    driver = init_driver(load_cookies=False)
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)  # wait for login page to load

    # Enter credentials and submit form
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    time.sleep(5)  # wait for authentication

    # Save session cookies for reuse
    pickle.dump(driver.get_cookies(), open(COOKIE_FILE, "wb"))
    driver.quit()
    print("✅ Logged in and cookies saved.")


def fetch_html(url):
    """
    Fetch the fully rendered HTML of a LinkedIn profile page.
    Uses saved cookies to maintain login session.
    """
    driver = init_driver()
    driver.get(url)
    time.sleep(5)  # allow JavaScript-rendered content to load
    html = driver.page_source  # grab the rendered HTML
    driver.quit()
    return html


def parse_profile(html):
    """
    Parse raw LinkedIn profile HTML to extract:
      - Name
      - Headline
      - About
      - Work experience roles and companies
      - Skills listed on the profile
    Returns a Python dict of structured data.
    """
    soup = BeautifulSoup(html, "html.parser")
    data = {
        "name":     soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else None,
        "headline": soup.select_one(".text-body-medium").get_text(strip=True) if soup.select_one(".text-body-medium") else None,
        "about":    soup.select_one("section.pv-about-section .pv-about__summary-text").get_text(strip=True) if soup.select_one("section.pv-about-section .pv-about__summary-text") else None,
        "experience": [],
        "skills":   []
    }

    # Extract each experience entry
    for li in soup.select("#experience-section li"):
        role_el = li.select_one("h3")
        comp_el = li.select_one(".pv-entity__secondary-title")
        if role_el and comp_el:
            data["experience"].append({
                "role":    role_el.get_text(strip=True),
                "company": comp_el.get_text(strip=True)
            })

    # Extract skills
    for s in soup.select(".pv-skill-category-entity__name-text"):
        data["skills"].append(s.get_text(strip=True))

    return data


def format_bio(profile_data):
    """
    Send the structured profile data to OpenAI and generate a 3-sentence LinkedIn-style bio.
    Requires OPENAI_API_KEY in environment variables.
    """

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.responses.create(
        model="gpt-4o",
        instructions=(
            "You’re a friendly user‐profile writer. Given this JSON of someone’s LinkedIn data, "
            "write one casual paragraph (2–3 sentences, ~50 words) that: "
            "1) names their current role and organization, "
            "2) highlights a standout project or experience, "
            "3) calls out their top technical skills, "
            "and 4) sounds natural and upbeat—just like this example:\n\n"
            "Ethan Lee is a Bachelor of Commerce student at the University of Melbourne blending his love of AI and voice tech to build real-time conversational agents, including an AI phone-screening system using Next.js, FastAPI, Twilio and 11Labs. He’s led hackathon teams like Urbanteria, fine-tuned image-generation models for property apps and helped SaaS founders with marketing, sharpening his skills in Python, React, Supabase and prompt engineering.\n\n"
            "Now write a matching paragraph for the JSON below:"
        ),
        input=json.dumps(profile_data),
    )

    return response.output_text


def main():
    """
    Entry point: handles --login flag or profile URL argument.
    """
    args = sys.argv[1:]
    if not args:
        print("Usage: python scrape.py [--login] [profile_url]")
        sys.exit(0)

    if args[0] == "--login":
        # Perform login and cookie save
        login()
        sys.exit(0)

    # Otherwise, treat first argument as the profile URL
    url = args[0]
    print(f"🔍 Fetching {url}")

    # 1) Fetch raw HTML
    html = fetch_html(url)
    print("🧩 Parsing profile data...")

    # 2) Parse into structured dict
    profile = parse_profile(html)
    print("✍️  Formatting bio with ChatGPT...")

    # 3) Generate bio and save to file
    bio = format_bio(profile)
    with open("bio.txt", "w") as f:
        f.write(bio)
    print("✅ Done! Bio saved to bio.txt")


if __name__ == "__main__":
    main()
