'''All functions for StacksKB item parsing'''
from bs4 import BeautifulSoup
import json
from utils import fetch_page
import re
from config import filter_words

def skb_get_title_and_link(listing):
    '''Get title and link from listing segment'''

    tl = listing.find('a', class_=
            'woocommerce-LoopProduct-link-title woocommerce-loop-product__title_ink')
    title = tl.get_text()

    link = tl['href']

    return (title, link)

def skb_get_qty(title):
    '''Get switch quantity from product title'''

    qty = re.findall(r'\((.*?)\)', title)
    if not qty: # SPECIFICALLY for Akko Matcha Green that do []
        qty = re.findall(r'\[(.*?)\]', title)
    if qty: # retain only the Pack of X/Singles strings
        qty = qty[-1]
    if qty != 'Singles': 
        switch_count = int(''.join(re.findall('[0-9]', qty)))
    else:
        switch_count = 1

    return switch_count

def skb_get_price(listing):
    '''Get price from listing segment'''

    price = listing.find_all('bdi')
    price = price[-1].text[1:] # get text, remove rupee symbol
    price = price.replace(",", '') # remove comma
    price = int(float(price)) # remove decimals and convert to int
    return price

async def skb_get_variants(session, url):
    '''Get variants for products with variants (loading extra page)'''

    soup = await fetch_page(session, url, {}) # no params needed here
    variants = soup.find('form')
    variants = json.loads(variants.get('data-product_variations'))
    variant_and_price = []
    for variant in variants:
        variant_and_price.append([variant['attributes']['attribute_variant'], variant['display_price']])
    return variant_and_price

async def skb_make_urllist(session, urls, params):
    '''
    Runs one call per category page to get the number of items present
    One concern might be the pagecount calculation, but we'll ignore it for now
    As SKB does not display any out of stock items, those are not a concern
    '''
    target_urls = {}
    for category, url in urls.items():
        soup = await fetch_page(session, url, params)
        # soup = BeautifulSoup(page, 'html.parser')

        item_count = int(soup.find('span', class_='wpc-filters-found-posts').get_text())
        per_page_count = 12 # every stackskb page has 12 items each
        pagecount = -((item_count) // (-per_page_count))
        for i in range(1, pagecount+1):
            target_urls[f"{url}page/{i}"] = category
    return target_urls

def skb_parse_switch_name(title):
    truncated_title = title.split('(')[0].strip()
    truncated_title = truncated_title.split()
    filtered_words = [word for word in truncated_title if word.lower() not in filter_words]
    title = ' '.join(filtered_words)
    return title