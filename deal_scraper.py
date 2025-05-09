import requests
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime

def scrape_footlocker(pages=1):
    """Scrape Footlocker sale section"""
    print("\nScraping Footlocker...")
    sportswear_deals = []
    base_url = "https://www.footlocker.com/category/sale.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/135.0.7049.96"}
    
    for page in range(1, pages + 1):
        try:
            url = base_url if page == 1 else f"{base_url}?currentPage={page}"
            print(f"Page {page}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, "html.parser")
            product_cards = soup.select(".ProductCard")
            
            for product in product_cards:
                try:
                    title = product.select_one(".ProductCard-link").text.strip()
                    current_price = product.select_one(".ProductPrice-final").text.strip()
                    original_price_elem = product.select_one(".ProductPrice-original")
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    product_url = "https://www.footlocker.com" + product.select_one("a.ProductCard-link")["href"]
                    
                    # Calculate discount percentage
                    discount_pct = 0
                    if original_price != current_price:
                        orig_match = re.search(r'[\d\.]+', original_price)
                        curr_match = re.search(r'[\d\.]+', current_price)
                        if orig_match and curr_match:
                            orig = float(orig_match.group())
                            curr = float(curr_match.group())
                            discount_pct = round(((orig - curr) / orig) * 100)
                    
                    sportswear_deals.append({
                        "store": "Footlocker",
                        "title": title,
                        "current_price": current_price,
                        "original_price": original_price,
                        "discount_pct": discount_pct,
                        "url": product_url,
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                except Exception as e:
                    pass
            
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"Error: {e}")
    
    return sportswear_deals

def run_all_scrapers(pages=1):
    """Run all scrapers and return combined results"""
    all_deals = []
    all_deals.extend(scrape_footlocker(pages))
    # Can add more scrapers here later
    return all_deals