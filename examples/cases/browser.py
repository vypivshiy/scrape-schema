import pprint

from playwright.sync_api import sync_playwright
from schema import MainPage

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://books.toscrape.com/catalogue/page-50.html")
        pprint.pprint(MainPage(page.content()).dict(), compact=True)
        browser.close()
