import sqlite3
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def scrap_page(page_url):
    conn = sqlite3.connect('iranjib.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS news (
                        url TEXT,
                        title TEXT, 
                        summary TEXT, 
                        content TEXT, 
                        date TEXT, 
                        views TEXT
                    )''')

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto(page_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded")

            # گرفتن title
            title_element = page.query_selector("h1")
            title = title_element.inner_text().strip() if title_element else ""

            # گرفتن summary
            summary_element = page.query_selector("div.newssummary")
            summary = summary_element.inner_text().strip() if summary_element else ""

            # گرفتن متن خبر
            news_text = ""
            matn = page.query_selector("div.matn")

            if matn:
                paragraphs = matn.query_selector_all("p")
                for p_tag in paragraphs:
                    news_text += p_tag.inner_text().strip() + "\n"

            # گرفتن جدول اطلاعات
            date = ""
            views = ""

            tables = page.query_selector_all("table")
            if len(tables) > 1:
                rows = tables[1].query_selector_all("tr")
                if len(rows) > 1:
                    cols = rows[1].query_selector_all("td")
                    if len(cols) > 2:
                        date = cols[1].inner_text().strip()
                        views = cols[2].inner_text().strip()

            # ذخیره در دیتابیس
            cur.execute("INSERT INTO news VALUES (?,?,?,?,?,?)",
                        (page_url, title, summary, news_text, date, views))

            conn.commit()
            browser.close()

    except PlaywrightTimeoutError:
        print("صفحه لود نشد:", page_url)

    except Exception as e:
        print("خطا:", e)

    finally:
        conn.close()


def main():
    scrap_page("https://www.iranjib.ir/shownews/123456/")  # لینک تست خودت رو بذار اینجا


if __name__ == '__main__':
    main()