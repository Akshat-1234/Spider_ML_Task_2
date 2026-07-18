import json
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

SAVE_DIR = PROJECT_DIR/"data"/"WHO"
SAVE_DIR.mkdir(parents=True,exist_ok=True)

FACT_SHEET_URL = "https://www.who.int/news-room/fact-sheets"
BASE_URL = "https://www.who.int"

headers = {"User-Agent":"Mozilla/5.0"}


#Retrying a request a few times before giving up

def get_with_retry(url,retries=3):

    for attempt in range(retries):

        try:
            response = requests.get(url,headers=headers,timeout=10)
            response.raise_for_status()
            return response

        except Exception as e:
            print(f"Attempt {attempt+1} failed for {url}: {e}")
            time.sleep(2)

    return None


#Getting all WHO Fact Sheet URLs

response = get_with_retry(FACT_SHEET_URL)

urls = []

if response is not None:

    soup = BeautifulSoup(response.text,"html.parser")

    for link in soup.find_all("a",href=True):
        href = link["href"]
        if href.startswith("/news-room/fact-sheets/detail/"):
            full_url = BASE_URL + href
            if full_url not in urls:
                urls.append(full_url)

else:
    print("Could not load fact sheet list page, stopping.")


#Scraping every Fact Sheet

for url in urls:

    print(f"Scraping {url}")

    response = get_with_retry(url)

    if response is None:
        print("Skipping, could not fetch page")
        continue

    soup = BeautifulSoup(response.text,"html.parser")

    article = soup.find("article")

    if article is None:
        print("Skipping, no article tag found")
        continue

    title_tag = soup.find("h1")

    if title_tag is None:
        print("Skipping, no title found")
        continue

    title = title_tag.get_text(strip=True)

    data = {
        "title":title,
        "source":"WHO",
        "url":url,
        "text":article.get_text("\n",strip=True)
    }

    filename = url.split("/")[-1] + ".json"

    try:
        with open(SAVE_DIR/filename,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4,ensure_ascii=False)
    except Exception as e:
        print(e)

    time.sleep(1)

print("Finished")
