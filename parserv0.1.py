import requests
from bs4 import BeautifulSoup
import csv
import time
import re

BASE_URL = "https://kaz.tengrinews.kz/news/page/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def get_article_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")

        content_div = soup.find("div", class_="tn-article-body") or soup.find("div", class_="content_main_text")
        if not content_div:
            print(f"ниче нот файндед братуль {url}")
            return ""

        paragraphs = content_div.find_all("p")
        text = "\n".join(p.get_text(" ", strip=True) for p in paragraphs)

        text = re.sub(r"(ПОДЕЛИТЬСЯ|Telegram[^\.]+|Tengrinews\.kz[^\.]*)", "", text)
        text = re.sub(r'Сілтемесіз жаңалық оқисыз ба\?.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Қосымшада оқыңыз.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Толығырақ оқу үшін қосымшаға өтіңіз.*', '', text, flags=re.DOTALL)
        text = text.strip()

        return text
    except Exception as e:
        print(f"брат парсить ете алмайм бұндайды, впадлу {url}: {e}")
        return ""


def scrape_page(page_num):
    url = f"{BASE_URL}{page_num}/"
    print(f"парсинг пейдж: {page_num} → {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print("мазерфакинеррор:", e)
        return []

    articles = []

    for item in soup.find_all("div", class_="content_main_item"):
        a_tag = item.find("a", href=True)
        if not a_tag:
            continue

        href = a_tag["href"]
        if not href.startswith("http"):
            href = "https://kaz.tengrinews.kz" + href

        title_tag = item.find("span", class_="content_main_item_title")
        title = title_tag.get_text(strip=True) if title_tag else a_tag.get("title", "").strip()
        if not title:
            continue

        date_tag = item.find("div", class_="content_main_item_meta")
        date = "—"
        if date_tag:
            span = date_tag.find("span")
            if span:
                date = span.get_text(strip=True)

        text = get_article_text(href)
        if not text:
            continue

        print(f"  [+] {title[:80]}...")
        articles.append([title, date, href, text])
        time.sleep(0.5)

    print(f"  файндед жаңалық саны: {len(articles)}")
    return articles


start_page = 1
end_page = 200

with open("kaz_tengri_dataset.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["title", "date", "url", "text"])

    for page in range(start_page, end_page + 1):
        data = scrape_page(page)
        for row in data:
            writer.writerow(row)
        time.sleep(1)

print("саксесфулл радной, чекни kaz_tengri_dataset.csv")
