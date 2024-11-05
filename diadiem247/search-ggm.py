import asyncio
import re
import pandas as pd
from playwright.async_api import async_playwright
from difflib import SequenceMatcher

file_path = "check.csv"

def best_match(address, items):
    highest_ratio = 0
    best_item = ""

    for item in items:
        ratio = SequenceMatcher(None, address, item["address"]).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_item = item

    return best_item, highest_ratio

async def get_location_google_maps(location_name, location_addr):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://www.google.com/maps")
        await page.wait_for_timeout(5000)

        await page.fill("input[name='q']", location_name)
        await page.press("input[name='q']", "Enter")
        await page.wait_for_timeout(5000)

        results_selector = await page.query_selector("div[role='feed']")
        results = []
        current_url = page.url
        
        if results_selector:
            link_elements = await results_selector.query_selector_all('a')
            for link_element in link_elements[1:]:
                href = await link_element.get_attribute('href')
                address = await link_element.get_attribute('aria-label')
                results.append({ "href": href, "address": address })

            best_result, match_ratio = best_match(location_addr, results)
            current_url = best_result["href"]
            print(results)
            print(f"Ratio: {match_ratio * 100}; Link: {best_result["href"]}")

        print(current_url)
        match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', current_url)
        await browser.close()
        return match.groups() if match else (0.0, 0.0)
    
def update_location(file_path):
    df = pd.read_csv(file_path)

    for idx, row in df.iterrows():
        lat = row['lat']
        lng = row['lng']

        if lat == 0.0 and lng == 0.0:
            location_name = row['location_name']
            location_address = row['location_address']

            adm_lv = location_address.rsplit(',', 2)
            dist_prov = adm_lv[-2] + ',' + adm_lv[-1]
            location_name = f"{location_name},{dist_prov}"
        
            coordinates = asyncio.run(get_location_google_maps(location_name, location_address))

            df.at[idx, 'lat'] = float(coordinates[0])
            df.at[idx, 'lng'] = float(coordinates[1])

    df.to_csv(file_path, index=False)

update_location(file_path)