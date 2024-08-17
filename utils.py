'''More generic functions'''
from bs4 import BeautifulSoup

async def fetch_page(session, url, params):
    '''Generic fetch page function'''
    async with session.get(url, headers=params) as response:
        page = await response.text()
        soup = BeautifulSoup(page, 'html.parser')
        return soup
    
# consumer function to save each entry with requisite info
# remember to parse everything as a set and then add to csv


