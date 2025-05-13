import requests
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime

def calculate_discount(original_price, current_price):
    """Calculate discount percentage between prices"""
    try:
        orig_match = re.search(r'[\d\.]+', original_price.replace(',', ''))
        curr_match = re.search(r'[\d\.]+', current_price.replace(',', ''))
        if orig_match and curr_match:
            orig = float(orig_match.group())
            curr = float(curr_match.group())
            if orig > curr:
                return round(((orig - curr) / orig) * 100)
    except:
        pass
    return 0

def scrape_footlocker(pages=1):
    """Scrape Footlocker sale section"""
    print("\nScraping Footlocker...")
    sportswear_deals = []
    base_url = "https://www.footlocker.com/category/sale.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
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
                    # Extract just the product name instead of all text
                    product_link = product.select_one(".ProductCard-link")
                    product_name_elem = product_link.select_one(".ProductName-primary")
                    
                    # If there's a specific product name element, use it
                    if product_name_elem:
                        title = product_name_elem.text.strip()
                    else:
                        # Fallback: try to extract just the product name from the link text
                        title = product_link.text.strip()
                        # Clean up the title (remove ratings, etc.)
                        title = re.sub(r'Average customer rating.*', '', title).strip()
                        title = re.sub(r'\d+ reviews.*', '', title).strip()
                        # Keep only the first line which is usually the product name
                        title = title.split('\n')[0].strip()
                    
                    current_price = product.select_one(".ProductPrice-final").text.strip()
                    original_price_elem = product.select_one(".ProductPrice-original")
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    # Get the href attribute correctly
                    href = product_link.get("href", "")
                    if href:
                        product_url = "https://www.footlocker.com" + href
                    else:
                        continue
                    
                    discount_pct = calculate_discount(original_price, current_price)
                    
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
                    print(f"Product extraction error: {e}")
            
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"Error: {e}")
    
    return sportswear_deals

def scrape_finishline(pages=1):
    """Scrape Finish Line sale section"""
    print("\nScraping Finish Line...")
    sportswear_deals = []
    base_url = "https://www.finishline.com/men/shoes/sale"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
    for page in range(1, pages + 1):
        try:
            url = f"{base_url}?page={page-1}"
            print(f"Page {page}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, "html.parser")
            # Finish Line structure
            products = soup.select("[data-product]")
            
            for product in products:
                try:
                    # Finish Line uses data-product attribute with JSON
                    product_data = product.get('data-product', '')
                    if product_data:
                        try:
                            import json
                            data = json.loads(product_data)
                            product_url = data.get('url', '')
                            if product_url and not product_url.startswith('http'):
                                product_url = "https://www.finishline.com" + product_url
                        except:
                            pass
                    
                    # Fallback to traditional extraction
                    title_elem = product.select_one(".product-name a")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one(".product-price .price-sale")
                    if not current_price_elem:
                        current_price_elem = product.select_one(".product-price span.price")
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one(".product-price .price-regular")
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    # Get URL from the link element if not already found
                    if not product_url and title_elem:
                        product_url = title_elem.get("href", "")
                        if product_url and not product_url.startswith('http'):
                            product_url = "https://www.finishline.com" + product_url
                    
                    if title and current_price and product_url:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        sportswear_deals.append({
                            "store": "Finish Line",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"Error: {e}")
    
    return sportswear_deals

def scrape_dicks_sporting_goods(pages=1):
    """Scrape Dick's Sporting Goods clearance section"""
    print("\nScraping Dick's Sporting Goods...")
    sportswear_deals = []
    base_url = "https://www.dickssportinggoods.com/f/clearance"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Dick's product structure
            products = soup.select(".dsg-react-product-card")
            
            for product in products:
                try:
                    title_elem = product.select_one(".product-title")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one(".css-q5spkg") # sale price
                    if not current_price_elem:
                        current_price_elem = product.select_one('[data-testid="product-price-sale"]')
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one(".css-1xqlg0o") # original price
                    if not original_price_elem:
                        original_price_elem = product.select_one('[data-testid="product-price-original"]')
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    link_elem = product.select_one("a")
                    product_url = "https://www.dickssportinggoods.com" + link_elem["href"] if link_elem else ""
                    
                    if title and current_price:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        sportswear_deals.append({
                            "store": "Dick's Sporting Goods",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return sportswear_deals

def scrape_adidas(pages=1):
    """Scrape Adidas sale section"""
    print("\nScraping Adidas...")
    sportswear_deals = []
    base_url = "https://www.adidas.com/us/sale"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Adidas product structure
            products = soup.select('[data-auto-id="product-card"]')
            
            for product in products:
                try:
                    title_elem = product.select_one(".product-card__title")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one(".product-card__sale-price")
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one(".product-card__original-price")
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    link_elem = product.select_one("a")
                    product_url = "https://www.adidas.com" + link_elem["href"] if link_elem else ""
                    
                    if title and current_price:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        sportswear_deals.append({
                            "store": "Adidas",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return sportswear_deals

def scrape_reebok(pages=1):
    """Scrape Reebok sale section"""
    print("\nScraping Reebok...")
    sportswear_deals = []
    base_url = "https://www.reebok.com/us/outlet"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Reebok uses similar structure to Adidas
            products = soup.select('[data-testid="product-card"]')
            
            for product in products:
                try:
                    title_elem = product.select_one('[data-testid="product-title"]')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one('[data-testid="product-price-sale"]')
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one('[data-testid="product-price-original"]')
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    link_elem = product.select_one("a")
                    product_url = "https://www.reebok.com" + link_elem["href"] if link_elem else ""
                    
                    if title and current_price:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        sportswear_deals.append({
                            "store": "Reebok",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return sportswear_deals

def scrape_eastbay(pages=1):
    """Scrape Eastbay sale section"""
    print("\nScraping Eastbay...")
    sportswear_deals = []
    base_url = "https://www.eastbay.com/category/sale.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
    for page in range(1, pages + 1):
        try:
            url = base_url if page == 1 else f"{base_url}?currentPage={page}"
            print(f"Page {page}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, "html.parser")
            # Eastbay uses similar structure to Footlocker
            product_cards = soup.select(".ProductCard")
            
            for product in product_cards:
                try:
                    product_link = product.select_one(".ProductCard-link")
                    product_name_elem = product_link.select_one(".ProductName-primary")
                    
                    if product_name_elem:
                        title = product_name_elem.text.strip()
                    else:
                        title = product_link.text.strip()
                        title = title.split('\n')[0].strip()
                    
                    current_price = product.select_one(".ProductPrice-final").text.strip()
                    original_price_elem = product.select_one(".ProductPrice-original")
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    # Get the href attribute correctly
                    href = product_link.get("href", "")
                    if href:
                        product_url = "https://www.eastbay.com" + href
                    else:
                        continue
                    
                    discount_pct = calculate_discount(original_price, current_price)
                    
                    sportswear_deals.append({
                        "store": "Eastbay",
                        "title": title,
                        "current_price": current_price,
                        "original_price": original_price,
                        "discount_pct": discount_pct,
                        "url": product_url,
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"Error: {e}")
    
    return sportswear_deals

def scrape_hibbett(pages=1):
    """Scrape Hibbett Sports sale section"""
    print("\nScraping Hibbett Sports...")
    sportswear_deals = []
    base_url = "https://www.hibbett.com/clearance/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Hibbett product structure
            products = soup.select(".product-tile")
            
            for product in products:
                try:
                    title_elem = product.select_one(".product-name a")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one(".product-sales-price")
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one(".product-list-price")
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    link_elem = product.select_one(".product-name a")
                    product_url = link_elem["href"] if link_elem else ""
                    if product_url and not product_url.startswith("http"):
                        product_url = "https://www.hibbett.com" + product_url
                    
                    if title and current_price:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        sportswear_deals.append({
                            "store": "Hibbett Sports",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return sportswear_deals

def scrape_walmart_beauty(pages=1):
    """Scrape Walmart beauty clearance section"""
    print("\nScraping Walmart Beauty Clearance...")
    beauty_deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Try multiple Walmart beauty clearance URLs
    urls = [
        "https://www.walmart.com/browse/beauty/clearance/1085666_7924299",
        "https://www.walmart.com/browse/beauty/1085666?facet=special_offers%3AClearance",
        "https://www.walmart.com/browse/beauty/makeup/1085666_1007040?facet=special_offers%3AClearance"
    ]
    
    for url in urls:
        try:
            print(f"Trying URL: {url}")
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Try multiple selectors for Walmart
            products = soup.select('[data-testid="item-stack"]') or soup.select('.search-result-gridview-item')
            
            for product in products[:10]:  # Limit to 10 products per URL
                try:
                    # Extract title
                    title_elem = product.select_one('a[href*="/ip/"] span')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # Extract current price
                    price_elem = product.select_one('[data-automation-id="product-price"] .price-current')
                    current_price = price_elem.text.strip() if price_elem else ""
                    
                    # Extract original price
                    orig_elem = product.select_one('.price-was')
                    original_price = orig_elem.text.strip() if orig_elem else current_price
                    
                    # Extract URL
                    link_elem = product.select_one('a[href*="/ip/"]')
                    if link_elem:
                        href = link_elem.get("href", "")
                        product_url = "https://www.walmart.com" + href if href.startswith('/') else href
                    else:
                        continue
                    
                    if title and current_price and product_url:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        # Filter for beauty products with good discounts
                        beauty_keywords = ['beauty', 'makeup', 'cosmetic', 'mascara', 'lipstick', 'foundation', 'skincare', 'serum', 'moisturizer']
                        if discount_pct > 30 and any(keyword in title.lower() for keyword in beauty_keywords):
                            beauty_deals.append({
                                "store": "Walmart",
                                "category": "Beauty",
                                "title": title,
                                "current_price": current_price,
                                "original_price": original_price,
                                "discount_pct": discount_pct,
                                "url": product_url,
                                "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                            
                except Exception as e:
                    continue
            
            if beauty_deals:
                break  # Stop if we found products
                
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Error with URL {url}: {e}")
    
    return beauty_deals

def scrape_target_beauty(pages=1):
    """Scrape Target beauty clearance section"""
    print("\nScraping Target Beauty Clearance...")
    beauty_deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Target beauty clearance URL
    base_url = "https://www.target.com/c/beauty-deals/-/N-bj2fz"
    
    for page in range(1, pages + 1):
        try:
            offset = (page - 1) * 24
            url = f"{base_url}?offset={offset}"
            print(f"Page {page}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.select('[data-test="product-card"]')
            
            for product in products:
                try:
                    title_elem = product.select_one('[data-test="product-title"]')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one('[data-test="offer-price"]')
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one('[data-test="list-price"]')
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    link_elem = product.select_one('a[href*="/p/"]')
                    if link_elem:
                        href = link_elem.get("href", "")
                        product_url = "https://www.target.com" + href if href.startswith('/') else href
                    else:
                        continue
                    
                    if title and current_price and product_url:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        beauty_deals.append({
                            "store": "Target",
                            "category": "Beauty",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
    
    return beauty_deals

def scrape_cvs_beauty(pages=1):
    """Scrape CVS beauty clearance section"""
    print("\nScraping CVS Beauty Clearance...")
    beauty_deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # CVS beauty sale URL
    base_url = "https://www.cvs.com/shop/beauty/sale"
    
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.select('.product-item')
            
            for product in products:
                try:
                    title_elem = product.select_one('.product-title a')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one('.price-now')
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one('.price-was')
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    if title_elem:
                        href = title_elem.get("href", "")
                        product_url = "https://www.cvs.com" + href if href.startswith('/') else href
                    else:
                        continue
                    
                    if title and current_price and product_url:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        beauty_deals.append({
                            "store": "CVS",
                            "category": "Beauty",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return beauty_deals

def scrape_ulta_clearance(pages=1):
    """Scrape Ulta beauty clearance section"""
    print("\nScraping Ulta Beauty Clearance...")
    beauty_deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Ulta clearance URL
    base_url = "https://www.ulta.com/shop/sale"
    
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.select('.ProductCard')
            
            for product in products:
                try:
                    title_elem = product.select_one('.ProductCard__Title')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    current_price_elem = product.select_one('.ProductHero__PriceNow')
                    current_price = current_price_elem.text.strip() if current_price_elem else ""
                    
                    original_price_elem = product.select_one('.ProductHero__PriceWas')
                    original_price = original_price_elem.text.strip() if original_price_elem else current_price
                    
                    link_elem = product.select_one('a')
                    if link_elem:
                        href = link_elem.get("href", "")
                        product_url = "https://www.ulta.com" + href if href.startswith('/') else href
                    else:
                        continue
                    
                    if title and current_price and product_url:
                        discount_pct = calculate_discount(original_price, current_price)
                        
                        beauty_deals.append({
                            "store": "Ulta",
                            "category": "Beauty",
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        
                except Exception as e:
                    print(f"Product extraction error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return beauty_deals

def run_beauty_scrapers(pages=1, progress_callback=None):
    """Run all beauty-focused scrapers"""
    all_beauty_deals = []
    
    # List of beauty scrapers
    scrapers = [
        ("Walmart Beauty", scrape_walmart_beauty),
        ("Target Beauty", scrape_target_beauty),
        ("CVS Beauty", scrape_cvs_beauty),
        ("Ulta Beauty", scrape_ulta_clearance)
    ]
    
    # Run each scraper
    for i, (store_name, scraper) in enumerate(scrapers):
        try:
            print(f"\nRunning {scraper.__name__}...")
            
            # Update progress
            if progress_callback:
                progress_callback(current=i, total=len(scrapers), current_store=store_name)
            
            deals = scraper(pages)
            all_beauty_deals.extend(deals)
            print(f"Found {len(deals)} deals from {store_name}")
            
            # Add delay between scrapers
            time.sleep(random.uniform(3, 6))
            
        except Exception as e:
            print(f"Error in {scraper.__name__}: {e}")
    
    # Final progress update
    if progress_callback:
        progress_callback(current=len(scrapers), total=len(scrapers), current_store="Complete")
    
    # Filter for high-value items (40%+ discount, $20+ original price)
    filtered_deals = []
    high_value_keywords = [
        'mascara', 'serum', 'cream', 'foundation', 'palette', 'brush',
        'volumizing', 'anti-aging', 'skincare', 'treatment', 'set',
        'collection', 'kit', 'fragrance', 'perfume', 'device', 'tool'
    ]
    
    for deal in all_beauty_deals:
        try:
            price_match = re.search(r'[\d\.]+', deal['original_price'].replace(',', ''))
            if price_match:
                original_price_num = float(price_match.group())
                
                if (deal['discount_pct'] >= 40 and 
                    original_price_num >= 20):
                    
                    title_lower = deal['title'].lower()
                    if any(keyword in title_lower for keyword in high_value_keywords):
                        filtered_deals.append(deal)
                        
        except Exception as e:
            print(f"Error filtering deal: {e}")
    
    print(f"\nTotal beauty deals found: {len(all_beauty_deals)}")
    print(f"High-value beauty deals: {len(filtered_deals)}")
    
    return filtered_deals
    """Run all scrapers and return combined results"""
    all_deals = []
    
    # List of all scraper functions
    scrapers = [
        ("Footlocker", scrape_footlocker),
        ("Finish Line", scrape_finishline),
        ("Dick's Sporting Goods", scrape_dicks_sporting_goods),
        ("Adidas", scrape_adidas),
        ("Reebok", scrape_reebok),
        ("Eastbay", scrape_eastbay),
        ("Hibbett Sports", scrape_hibbett)
    ]
    
    # Run each scraper
    for i, (store_name, scraper) in enumerate(scrapers):
        try:
            print(f"\nRunning {scraper.__name__}...")
            
            # Update progress
            if progress_callback:
                progress_callback(current=i, total=len(scrapers), current_store=store_name)
            
            deals = scraper(pages)
            all_deals.extend(deals)
            print(f"Found {len(deals)} deals from {store_name}")
            
            # Debug: Check if URLs are valid
            invalid_urls = [d for d in deals if not d.get('url', '').startswith('http')]
            if invalid_urls:
                print(f"WARNING: {len(invalid_urls)} deals from {store_name} have invalid URLs")
                for deal in invalid_urls[:3]:  # Show first 3 invalid URLs
                    print(f"  - {deal.get('title', 'Unknown')}: {deal.get('url', 'No URL')}")
            
            # Add delay between scrapers to avoid rate limiting
            time.sleep(random.uniform(2, 5))
        except Exception as e:
            print(f"Error in {scraper.__name__}: {e}")
    
    # Final progress update
    if progress_callback:
        progress_callback(current=len(scrapers), total=len(scrapers), current_store="Complete")
    
    print(f"\nTotal deals found: {len(all_deals)}")
    
    # Debug: Show URL statistics
    valid_urls = [d for d in all_deals if d.get('url', '').startswith('http')]
    print(f"Valid URLs: {len(valid_urls)}/{len(all_deals)}")
    
    return all_deals
    return all_deals

if __name__ == "__main__":
    # Test scraping with different options
    print("=== Testing Beauty Scrapers ===")
    beauty_deals = run_all_scrapers(pages=1, category="beauty")
    
    print("\n=== Beauty Deals Summary ===")
    print(f"Total beauty deals: {len(beauty_deals)}")
    
    # Show top 5 beauty deals by discount
    if beauty_deals:
        sorted_beauty = sorted(beauty_deals, key=lambda x: x["discount_pct"], reverse=True)[:5]
        print("\nTop 5 Beauty Deals by Discount:")
        for deal in sorted_beauty:
            print(f"{deal['discount_pct']}% off - {deal['title'][:50]}... - {deal['current_price']} (was {deal['original_price']}) - {deal['store']}")
    
    print("\n=== Testing General Scrapers ===")
    general_deals = run_all_scrapers(pages=1, category="all")
    
    # Print summary
    print("\n=== Summary by Store ===")
    store_counts = {}
    for deal in general_deals:
        store = deal["store"]
        store_counts[store] = store_counts.get(store, 0) + 1
    
    for store, count in store_counts.items():
        print(f"{store}: {count} deals")
    
    # Print top 5 deals by discount
    print("\n=== Top 5 Deals by Discount ===")
    sorted_deals = sorted(general_deals, key=lambda x: x["discount_pct"], reverse=True)[:5]
    for deal in sorted_deals:
        print(f"{deal['discount_pct']}% off - {deal['title']} - {deal['current_price']} (was {deal['original_price']}) - {deal['store']}")