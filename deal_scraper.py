import requests
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime
import json

# Store configurations with their scraping patterns
STORE_CONFIGS = {
    "sportswear": [
        {
            "name": "Footlocker",
            "base_url": "https://www.footlocker.com/category/sale.html",
            "page_param": "currentPage",
            "selectors": {
                "product_container": ".ProductCard",
                "title": [".ProductName-primary", ".ProductCard-link"],
                "current_price": ".ProductPrice-final",
                "original_price": ".ProductPrice-original",
                "link": ".ProductCard-link",
                "link_prefix": "https://www.footlocker.com"
            }
        },
        {
            "name": "Eastbay",
            "base_url": "https://www.eastbay.com/category/sale.html",
            "page_param": "currentPage",
            "selectors": {
                "product_container": ".ProductCard",
                "title": [".ProductName-primary", ".ProductCard-link"],
                "current_price": ".ProductPrice-final",
                "original_price": ".ProductPrice-original",
                "link": ".ProductCard-link",
                "link_prefix": "https://www.eastbay.com"
            }
        },
        {
            "name": "Finish Line",
            "base_url": "https://www.finishline.com/men/shoes/sale",
            "page_param": "page",
            "page_offset": -1,
            "selectors": {
                "product_container": ["[data-product]", ".product-tile", ".product-card"],
                "title": [".product-name a", ".product-title"],
                "current_price": [".product-price .price-sale", ".product-sales-price", ".product-price"],
                "original_price": [".product-price .price-regular", ".product-list-price"],
                "link": [".product-name a", "a"],
                "link_prefix": "https://www.finishline.com",
                "data_attr": "data-product"
            }
        },
        {
            "name": "Dick's Sporting Goods",
            "base_url": "https://www.dickssportinggoods.com/f/clearance",
            "single_page": True,
            "selectors": {
                "product_container": [".dsg-react-product-card", "[data-testid='product-card']", ".product-card"],
                "title": [".product-title", "[data-testid='product-title']", ".dsg-product-name"],
                "current_price": [".css-q5spkg", '[data-testid="product-price-sale"]', ".product-sale-price"],
                "original_price": [".css-1xqlg0o", '[data-testid="product-price-original"]', ".product-list-price"],
                "link": "a",
                "link_prefix": "https://www.dickssportinggoods.com"
            }
        },
        {
            "name": "Adidas",
            "base_url": "https://www.adidas.com/us/men-sale",
            "single_page": True,
            "selectors": {
                "product_container": ['[data-auto-id="product-card"]', '[data-test-id="product-card"]', ".product-card"],
                "title": [".glass-product-card__title", ".product-card__title", "[data-test-id='product-card-title']"],
                "current_price": [".glass-product-card__sale-price", ".product-card__sale-price", "[data-test-id='sale-price']"],
                "original_price": [".glass-product-card__original-price", ".product-card__original-price", "[data-test-id='original-price']"],
                "link": "a",
                "link_prefix": "https://www.adidas.com"
            }
        },
        {
            "name": "Reebok",
            "base_url": "https://www.reebok.com/us/men-shoes-outlet",
            "single_page": True,
            "selectors": {
                "product_container": ['[data-testid="product-card"]', '.product-card'],
                "title": ['[data-testid="product-title"]', '.product-title'],
                "current_price": ['[data-testid="product-price-sale"]', '.product-price-sale'],
                "original_price": ['[data-testid="product-price-original"]', '.product-price-original'],
                "link": "a",
                "link_prefix": "https://www.reebok.com"
            }
        },
        {
            "name": "Hibbett Sports",
            "base_url": "https://www.hibbett.com/sale/",
            "single_page": True,
            "selectors": {
                "product_container": ".product-tile",
                "title": ".product-name a",
                "current_price": ".product-sales-price",
                "original_price": ".product-list-price",
                "link": ".product-name a",
                "link_prefix": "https://www.hibbett.com"
            }
        }
    ],
    "beauty": [
        {
            "name": "Walmart Beauty",
            "base_url": "https://www.walmart.com/browse/beauty/clearance/1085666_7924299",
            "single_page": True,
            "category": "Beauty",
            "selectors": {
                "product_container": ['[data-testid="item-stack"]', '[data-testid="product-item"]', '.product-card'],
                "title": ['a[href*="/ip/"] span', '[data-testid="product-title"]'],
                "current_price": ['[data-automation-id="product-price"] .price-current', '[data-testid="current-price"]'],
                "original_price": ['.price-was', '[data-testid="list-price"]'],
                "link": 'a[href*="/ip/"]',
                "link_prefix": "https://www.walmart.com"
            },
            "filters": {
                "min_discount": 30,
                "keywords": ['beauty', 'makeup', 'cosmetic', 'mascara', 'lipstick', 'foundation', 'skincare', 'serum', 'moisturizer'],
                "in_title": True
            }
        },
        {
            "name": "Target Beauty",
            "base_url": "https://www.target.com/c/beauty-deals/-/N-bj2fz",
            "page_param": "offset",
            "page_size": 24,
            "category": "Beauty",
            "selectors": {
                "product_container": ['[data-test="product-card"]', '[data-test="@web/ProductCard"]'],
                "title": ['[data-test="product-title"]', 'h3.ProductCard__Title'],
                "current_price": ['[data-test="offer-price"]', '[data-test="current-retail"]'],
                "original_price": ['[data-test="list-price"]', '[data-test="previous-retail"]'],
                "link": 'a[href*="/p/"]',
                "link_prefix": "https://www.target.com"
            }
        },
        {
            "name": "CVS Beauty",
            "base_url": "https://www.cvs.com/shop/beauty",
            "single_page": True,
            "category": "Beauty",
            "custom_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive"
            },
            "selectors": {
                "product_container": '.css-1dbjc4n.r-13awgt0',
                "title": '.css-901oao.css-cens5h.r-a5wbuh',
                "current_price": '.css-901oao.r-a5wbuh.r-1b2b6em',
                "original_price": '.css-901oao.r-13hce6t.r-1b43r93',
                "link": 'a',
                "link_prefix": "https://www.cvs.com"
            }
        },
        {
            "name": "Ulta Beauty",
            "base_url": "https://www.ulta.com/shop/sale",
            "single_page": True,
            "category": "Beauty",
            "selectors": {
                "product_container": ['.ProductCard', 'div[data-testid="product-card"]'],
                "title": ['.ProductCard__Title', '[data-testid="product-card-title"]'],
                "current_price": ['.ProductPricing__hero-price', '[data-testid="product-card-price"]'],
                "original_price": ['.ProductPricing__original-price', '[data-testid="product-card-original-price"]'],
                "link": 'a',
                "link_prefix": "https://www.ulta.com"
            }
        }
    ]
}

class UniversalScraper:
    """Universal scraper that can handle any store configuration"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
    
    def calculate_discount(self, original_price, current_price):
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
    
    def extract_text(self, element, selectors):
        """Extract text using multiple selectors (handles lists of selectors)"""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            elem = element.select_one(selector)
            if elem:
                return elem.text.strip()
        return None
    
    def extract_url(self, element, selector, prefix):
        """Extract URL from element and add prefix if needed"""
        link_elem = element.select_one(selector)
        if link_elem:
            href = link_elem.get("href", "")
            if href and not href.startswith("http"):
                return prefix + href
            return href
        return ""
    
    def scrape_page(self, url, config):
        """Scrape a single page using the provided configuration"""
        deals = []
        
        try:
            # Use custom headers if provided
            headers = self.headers.copy()
            if config.get("custom_headers"):
                headers.update(config["custom_headers"])
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"  Status code {response.status_code} for {url}")
                return deals
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Try different selectors for product containers
            selectors = config["selectors"]["product_container"]
            if isinstance(selectors, str):
                selectors = [selectors]
            
            products = []
            for selector in selectors:
                products = soup.select(selector)
                if products:
                    print(f"  Found {len(products)} products using selector: {selector}")
                    break
            
            if not products:
                print(f"  No products found with any selector")
                return deals
            
            for product in products[:50]:  # Limit to 50 products per page
                try:
                    # Handle special data-product attribute for some stores
                    if config["selectors"].get("data_attr"):
                        product_data = product.get(config["selectors"]["data_attr"], '')
                        if product_data:
                            try:
                                data = json.loads(product_data)
                                product_url = data.get('url', '')
                                if product_url and not product_url.startswith('http'):
                                    product_url = config["selectors"]["link_prefix"] + product_url
                            except:
                                pass
                    
                    # Extract product details
                    title = self.extract_text(product, config["selectors"]["title"])
                    current_price = self.extract_text(product, config["selectors"]["current_price"])
                    original_price = self.extract_text(product, config["selectors"]["original_price"])
                    
                    if not original_price:
                        original_price = current_price
                    
                    # Get product URL
                    if 'product_url' not in locals() or not product_url:
                        product_url = self.extract_url(
                            product, 
                            config["selectors"]["link"], 
                            config["selectors"]["link_prefix"]
                        )
                    
                    if title and current_price and product_url:
                        discount_pct = self.calculate_discount(original_price, current_price)
                        
                        # Apply filters if specified
                        if "filters" in config:
                            filters = config["filters"]
                            
                            # Check minimum discount
                            if filters.get("min_discount", 0) > discount_pct:
                                continue
                            
                            # Check keywords in title
                            if filters.get("keywords") and filters.get("in_title"):
                                title_lower = title.lower()
                                if not any(keyword in title_lower for keyword in filters["keywords"]):
                                    continue
                        
                        deal = {
                            "store": config["name"],
                            "title": title,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_pct": discount_pct,
                            "url": product_url,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        
                        # Add category if specified
                        if config.get("category"):
                            deal["category"] = config["category"]
                        
                        deals.append(deal)
                        
                except Exception as e:
                    continue  # Skip errors on individual products
            
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
        
        return deals
    
    def scrape_store(self, config, pages=1):
        """Scrape a store using its configuration"""
        print(f"\nScraping {config['name']}...")
        all_deals = []
        
        # Handle single page stores
        if config.get("single_page", False):
            deals = self.scrape_page(config["base_url"], config)
            print(f"  Found {len(deals)} deals")
            return deals
        
        # Handle multi-page stores
        for page in range(1, pages + 1):
            print(f"  Page {page}...")
            
            # Build URL based on pagination configuration
            if page == 1:
                url = config["base_url"]
            else:
                page_num = page
                if config.get("page_offset"):
                    page_num = page + config["page_offset"]
                
                if config.get("page_size"):
                    # For offset-based pagination
                    offset = (page - 1) * config["page_size"]
                    url = f"{config['base_url']}?{config['page_param']}={offset}"
                else:
                    # For page-based pagination
                    url = f"{config['base_url']}?{config['page_param']}={page_num}"
            
            deals = self.scrape_page(url, config)
            print(f"    Found {len(deals)} deals on page {page}")
            all_deals.extend(deals)
            
            # Add delay between pages
            if page < pages:
                time.sleep(random.uniform(1, 2))
        
        print(f"  Total: {len(all_deals)} deals from {config['name']}")
        return all_deals

# Main scraping functions
def run_all_scrapers(pages=1, progress_callback=None, category="all"):
    """Run scrapers based on category selection"""
    scraper = UniversalScraper()
    all_deals = []
    
    # Determine which stores to scrape
    stores_to_scrape = []
    
    if category == "all":
        # Include all stores from all categories
        for cat_stores in STORE_CONFIGS.values():
            stores_to_scrape.extend(cat_stores)
    elif category == "beauty":
        stores_to_scrape = STORE_CONFIGS.get("beauty", [])
    elif category == "sportswear":
        stores_to_scrape = STORE_CONFIGS.get("sportswear", [])
    else:
        # Default to all stores
        for cat_stores in STORE_CONFIGS.values():
            stores_to_scrape.extend(cat_stores)
    
    total_stores = len(stores_to_scrape)
    
    # Run each scraper
    for i, store_config in enumerate(stores_to_scrape):
        try:
            store_name = store_config["name"]
            
            # Update progress
            if progress_callback:
                progress_callback(current=i, total=total_stores, current_store=store_name, category=category)
            
            deals = scraper.scrape_store(store_config, pages)
            all_deals.extend(deals)
            print(f"Found {len(deals)} deals from {store_name}")
            
            # Add delay between stores
            if i < total_stores - 1:
                time.sleep(random.uniform(3, 6))
                
        except Exception as e:
            print(f"Error scraping {store_name}: {e}")
    
    # Final progress update
    if progress_callback:
        progress_callback(current=total_stores, total=total_stores, current_store="Complete", category=category)
    
    print(f"\nTotal deals found: {len(all_deals)}")
    
    # Apply additional filtering for high-value items
    if category == "beauty":
        all_deals = filter_high_value_beauty(all_deals)
    
    return all_deals

def filter_high_value_beauty(deals):
    """Filter beauty deals for high-value items"""
    filtered_deals = []
    high_value_keywords = [
        'mascara', 'serum', 'cream', 'foundation', 'palette', 'brush',
        'volumizing', 'anti-aging', 'skincare', 'treatment', 'set',
        'collection', 'kit', 'fragrance', 'perfume', 'device', 'tool'
    ]
    
    for deal in deals:
        try:
            price_match = re.search(r'[\d\.]+', deal['original_price'].replace(',', ''))
            if price_match:
                original_price_num = float(price_match.group())
                
                if (deal['discount_pct'] >= 40 and original_price_num >= 20):
                    title_lower = deal['title'].lower()
                    if any(keyword in title_lower for keyword in high_value_keywords):
                        filtered_deals.append(deal)
                        
        except Exception as e:
            print(f"Error filtering deal: {e}")
    
    print(f"High-value beauty deals: {len(filtered_deals)}")
    return filtered_deals

# Functions to add new stores easily
def add_store(category, store_config):
    """Add a new store to the configuration"""
    if category not in STORE_CONFIGS:
        STORE_CONFIGS[category] = []
    STORE_CONFIGS[category].append(store_config)

def create_store_config(name, base_url, selectors, **kwargs):
    """Helper function to create a store configuration"""
    config = {
        "name": name,
        "base_url": base_url,
        "selectors": selectors
    }
    
    # Add optional parameters
    config.update(kwargs)
    
    return config

# Example of how to add a new store
def add_new_store_example():
    new_store = create_store_config(
        name="New Store",
        base_url="https://newstore.com/sale",
        selectors={
            "product_container": ".product",
            "title": ".product-name",
            "current_price": ".sale-price",
            "original_price": ".regular-price",
            "link": "a.product-link",
            "link_prefix": "https://newstore.com"
        },
        single_page=True,
        category="General"
    )
    add_store("general", new_store)

# Debug function to test individual stores
def test_store_scraper(store_name, pages=1):
    """Test a specific store's scraper"""
    scraper = UniversalScraper()
    
    # Find the store configuration
    store_config = None
    for category_stores in STORE_CONFIGS.values():
        for store in category_stores:
            if store["name"] == store_name:
                store_config = store
                break
    
    if not store_config:
        print(f"Store '{store_name}' not found")
        return []
    
    print(f"Testing {store_name}...")
    deals = scraper.scrape_store(store_config, pages)
    
    if deals:
        print(f"\nSample deal from {store_name}:")
        print(json.dumps(deals[0], indent=2))
    else:
        print(f"\nNo deals found from {store_name}")
        print("Try checking the following:")
        print("1. Website structure may have changed")
        print("2. CSS selectors need updating")
        print("3. Website might be blocking scrapers")
    
    return deals

if __name__ == "__main__":
    # Test the refactored scraper
    print("Testing refactored scraper...")
    
    # Test individual stores first
    test_stores = ["Footlocker", "Dick's Sporting Goods", "Walmart Beauty"]
    
    for store in test_stores:
        print("\n" + "="*50)
        test_store_scraper(store, pages=1)
        time.sleep(2)
    
    print("\n" + "="*50)
    print("\nTesting full category scraping...")
    
    # Test sportswear scrapers
    sportswear_deals = run_all_scrapers(pages=1, category="sportswear")
    print(f"Found {len(sportswear_deals)} sportswear deals")
    
    # Test beauty scrapers  
    beauty_deals = run_all_scrapers(pages=1, category="beauty")
    print(f"Found {len(beauty_deals)} beauty deals")