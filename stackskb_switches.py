'''
Driver code for StacksKB - switches only
'''
import os
import csv
import asyncio
import aiohttp
from config import variant_listings, urls
from utils import fetch_page

from parse_skb import (
    skb_get_variants,
    skb_get_title_and_link,
    skb_get_qty,
    skb_get_price,
    skb_make_urllist,
    skb_parse_switch_name,
)

async def parse_page_skb_switch(session, url, category, params):
    '''Parse page content for a StacksKB switches page'''
    soup = await fetch_page(session, url, params)
    # print(soup)
    listings = soup.find_all('div', class_='product-details content-bg entry-content-wrap')
    parsed_items = []
    for _, listing in enumerate(listings):

        title, link = skb_get_title_and_link(listing)

        # if in the variant-ed list, check it out
        variants = []
        if title in variant_listings:
            # deal with them by going through each item
            variants = await skb_get_variants(session, link)

        # get and parse product price
        price = skb_get_price(listing)
        switch_count = skb_get_qty(title)
        item_name = skb_parse_switch_name(title)

        if variants:
            for variant in variants:
                variant_name = f"{item_name} ({variant[0]})"
                price = variant[1]
                # print(f"{category}: {variant_name} - {switch_count} - {price} - per-switch = {price // switch_count}")
                this_item = {
                        'name': variant_name,
                        'category': category,
                        'price': price,
                        'count': switch_count,
                        'price-per-switch': (price // switch_count)
                    }
                parsed_items.append(this_item)
        else:
            # print(f"{category}: {item_name} - {switch_count} - {price} - per-switch = {price // switch_count}")
            this_item = {
                    'name': item_name,
                    'category': category,
                    'price': price,
                    'count': switch_count,
                    'price-per-switch': (price // switch_count)
                }
            parsed_items.append(this_item)

    return parsed_items

def save_to_csv(parsed_items, filename='skb-switches.csv'):
    '''Save a list of parsed items to a CSV file, merging categories for duplicate names.'''
    
    # Check if the file exists and load existing data if it does
    if os.path.isfile(filename):
        with open(filename, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_items = {row['name']: row for row in reader}
    else:
        existing_items = {}

    # Update or add items to the existing_items dictionary
    for item in parsed_items:
        name = item['name']
        if name in existing_items:
            # Merge categories if the name already exists
            existing_categories = existing_items[name]['category'].split(', ')
            new_category = item['category']
            if new_category not in existing_categories:
                existing_categories.append(new_category)
            existing_items[name]['category'] = ', '.join(existing_categories)
        else:
            # Add new item
            existing_items[name] = item

        # Write the updated items back to the CSV file
    with open(filename, mode='w', newline='') as csvfile:
        fieldnames = parsed_items[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()
        
        # Write all the items
        writer.writerows(existing_items.values())

    print(f"Saved {len(parsed_items)} items to {filename}.")

async def main():
    '''driver for skb, switches only for now'''
    params = {'avail': 'instock'}

    async with aiohttp.ClientSession() as session:
        url_list = await skb_make_urllist(session, urls, params)
        print(f"Fetching {len(url_list)} pages total")
        tasks = []
        for url, category in url_list.items():
            tasks.append(parse_page_skb_switch(session, url, category, params))
        results = await asyncio.gather(*tasks)
                # Flatten the list of lists (if each parse_page_skb_switch returns a list of items)
        all_parsed_items = [item for sublist in results for item in sublist]

        # Save the parsed items to a CSV file
        save_to_csv(all_parsed_items)
        print(all_parsed_items)

asyncio.run(main())
