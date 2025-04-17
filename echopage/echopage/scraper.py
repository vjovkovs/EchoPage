import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathlib import Path
from time import sleep

from echopage.echopage.utils import sanitize_filename
from echopage.logger import setup_logger

load_dotenv()
logger = setup_logger()

# Load selectors from .env
TITLE_SELECTOR = os.getenv("CHAPTER_TITLE_SELECTOR", "h1")
CONTENT_SELECTOR = os.getenv("CHAPTER_CONTENT_SELECTOR", "div.chapter-content")
NEXT_SELECTOR = os.getenv("NEXT_CHAPTER_SELECTOR", "a.next")

def fetch_page(url):
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logger.error(f"Failed to fetch page: {e}")
        return None

def parse_chapter(soup):
    try:
        title = soup.select_one(TITLE_SELECTOR).text.strip()
        content_div = soup.select_one(CONTENT_SELECTOR)
        content = content_div.get_text(separator="\n").strip()
        return title, content
    except Exception as e:
        logger.error(f"Error parsing chapter: {e}")
        return None, None

def get_next_chapter_url(soup):
    try:
        next_link = soup.select_one(NEXT_SELECTOR)
        return next_link['href'] if next_link and 'href' in next_link.attrs else None
    except Exception as e:
        logger.warning(f"No next chapter link found: {e}")
        return None

def save_chapter(title, content, chapter_num, novel_dir):
    safe_title = sanitize_filename(f"{chapter_num:03d}_{title.replace(' ', '_').replace('/', '-')}")+".txt"
    filepath = Path(novel_dir) / safe_title
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{title}\n\n{content}")
    return filepath

def scrape_chapters(start_url, count, novel_title):
    current_url = start_url
    novel_dir = Path("output") / novel_title.replace(" ", "_")
    novel_dir.mkdir(parents=True, exist_ok=True)

    chapters = []

    for i in range(count):
        soup = fetch_page(current_url)
        if not soup:
            logger.error(f"Skipping chapter {i + 1} due to fetch error.")
            break

        title, content = parse_chapter(soup)
        if not title or not content:
            logger.error(f"Skipping chapter {i + 1} due to parse error.")
            break

        filepath = save_chapter(title, content, i + 1, novel_dir)
        chapters.append({
            "title": title,
            "filepath": filepath,
            "number": i + 1
        })

        next_url = get_next_chapter_url(soup)
        if not next_url:
            logger.warning("No next chapter found. Ending early.")
            break

        current_url = next_url
        sleep(1)  # be kind to the server

    logger.info(f"Scraped {len(chapters)} chapters.")
    return chapters



# def scrape_chapter(url, selectors):
#     """
#     Scrapes a single chapter from the given URL using the provided selectors.

#     Args:
#         url (str): The URL of the chapter to scrape.
#         selectors (dict): A dictionary containing CSS selectors for 'title', 'content', and 'next'.

#     Returns:
#         dict: A dictionary containing the chapter title, content, and next chapter URL.
#     """
#     response = requests.get(url)
#     response.raise_for_status()

#     soup = BeautifulSoup(response.text, 'html.parser')

#     title = soup.select_one(selectors['title']).get_text(strip=True)
#     content = soup.select_one(selectors['content']).get_text(strip=True)
#     next_url = soup.select_one(selectors['next'])['href'] if soup.select_one(selectors['next']) else None

#     return {
#         'title': title,
#         'content': content,
#         'next_url': next_url
#     }