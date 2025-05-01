# LinkedIn Profile Scraper & Formatter

A simple Python script to:

1. Automate LinkedIn login via Selenium and save session cookies.  
2. Fetch a profile’s fully rendered HTML (including JS-loaded sections).  
3. Parse out name, headline, experience, and skills using BeautifulSoup.  
4. Send the structured JSON to OpenAI and generate a concise 3-sentence LinkedIn bio.  

---

## Prerequisites

- Python 3.8+  
- A LinkedIn account (for full-profile scraping)  
- An OpenAI API key  
- Environment variables set:
  - `LINKEDIN_EMAIL`  
  - `LINKEDIN_PASSWORD`  
  - `OPENAI_API_KEY`

---

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/Spagum9113/LinkedinWebScrapperV1.git
   cd LinkedinWebScrapperV1
   ```

2. **Create & activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Log in & save cookies** (run once, or when LinkedIn forces re-login):
   ```bash
   python main.py --login
   ```
   - Launches a headless browser, logs into LinkedIn, and saves your session cookies to `cookies.pkl`.

2. **Fetch a profile & generate the bio**:
   ```bash
   python main.py https://www.linkedin.com/in/someone/
   ```
   - Uses your saved cookies to fetch the full profile page.
   - Parses name, headline, experience, and skills.
   - Sends the structured data to OpenAI and writes the resulting 3-sentence bio to `bio.txt`.

---
