import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

async def main(url, filename):
    html_content = await fetch_html(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    save_to_file(soup.prettify(), filename)

if __name__ == "__main__":
    url = 'https://stackskb.com/store/monsgeek-m7-qmk-barebones-keyboard/'  # Replace with the URL you want to scrape
    filename = "m7.html"     # Replace with your desired output filename
    asyncio.run(main(url, filename))
