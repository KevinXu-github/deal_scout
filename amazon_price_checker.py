import requests
from bs4 import BeautifulSoup
import time
import re
import json
from urllib.parse import quote
import random
import cloudscraper

# Consider using the official Amazon API instead for production use
# This is for educational purposes to demonstrate anti-blocking techniques

class SaferAmazonPriceChecker:
    def __init__(self):
        # Use cloudscraper which helps bypass Cloudflare protection
        self.scraper = cloudscraper.create_scraper()
        
        # Realistic user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        
        # Headers to appear more human-like
        self.base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # Session to maintain cookies
        self.session = requests.Session()
        
    def get_headers(self):
        """Generate random headers for each request"""
        headers = self.base_headers.copy()
        headers["User-Agent"] = random.choice(self.user_agents)
        return headers
    
    def human_delay(self, min_seconds=2, max_seconds=5):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def search_amazon_safely(self, product_name):
        """Search Amazon with anti-blocking measures"""
        print(f"Searching for: {product_name}")
        
        # Clean search query
        search_query = self.clean_search_query(product_name)
        
        # Alternative search methods
        search_urls = [
            f"https://www.amazon.com/s?k={quote(search_query)}",
            f"https://www.amazon.com/s?k={quote(search_query)}&ref=nb_sb_noss"
        ]
        
        for attempt, url in enumerate(search_urls):
            try:
                print(f"Attempt {attempt + 1}: {url}")
                
                # Human-like delay
                self.human_delay()
                
                # Make request
                headers = self.get_headers()
                response = self.session.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"Success! Status: {response.status_code}")
                    return self.parse_search_results(response.text, search_query)
                elif response.status_code == 503:
                    print("Service unavailable - Possible CAPTCHA")
                elif response.status_code == 429:
                    print("Rate limited - Too many requests")
                else:
                    print(f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
        
        return None
    
    def clean_search_query(self, product_name):
        """Clean product name for better search results"""
        # Remove gender specs but keep brand and model
        query = re.sub(r"\b(men's|women's|boys'|girls'|kids')\b", "", product_name, flags=re.IGNORECASE)
        
        # Keep only important words
        words = query.split()
        if len(words) > 4:
            # Keep brand and first 3 model words
            query = ' '.join(words[:4])
        
        return query.strip()
    
    def parse_search_results(self, html, search_query):
        """Parse Amazon search results"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check for CAPTCHA
            if "Enter the characters you see below" in html:
                print("CAPTCHA detected!")
                return None
            
            results = []
            
            # Try multiple selectors
            selectors = [
                "[data-component-type='s-search-result']",
                "div.s-result-item[data-asin]",
                "div[data-index]"
            ]
            
            products = None
            for selector in selectors:
                products = soup.select(selector)
                if products:
                    print(f"Found {len(products)} products with selector: {selector}")
                    break
            
            if not products:
                print("No products found")
                return None
            
            for i, product in enumerate(products[:5]):
                try:
                    # Extract data with multiple fallback selectors
                    title = self.extract_text(product, [
                        "h2 a span",
                        "h2 span",
                        "a.s-link span"
                    ])
                    
                    price = self.extract_price(product)
                    
                    if title and price:
                        results.append({
                            "title": title,
                            "price": price,
                            "position": i + 1
                        })
                        print(f"Product {i+1}: {title[:50]}... - ${price}")
                except Exception as e:
                    print(f"Error parsing product {i+1}: {e}")
            
            return results
            
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return None
    
    def extract_text(self, element, selectors):
        """Extract text using multiple selectors"""
        for selector in selectors:
            elem = element.select_one(selector)
            if elem:
                return elem.text.strip()
        return None
    
    def extract_price(self, product):
        """Extract price with multiple fallback methods"""
        price_selectors = [
            "span.a-price-whole",
            "span.a-price:not(.a-text-price) span",
            "span.a-price-range span.a-price-whole",
            "span.a-price span.a-offscreen"
        ]
        
        for selector in price_selectors:
            price_elem = product.select_one(selector)
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text)
                if price_match:
                    return float(price_match.group().replace(',', ''))
        
        return None

# Alternative approach using a third-party API (recommended for production)
class AmazonAPIAlternative:
    """
    For production use, consider these alternatives:
    1. Amazon Product Advertising API (official)
    2. RapidAPI Amazon endpoints
    3. ScrapingBee, ScraperAPI, or similar services
    4. Bright Data (formerly Luminati) for residential proxies
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.example.com/amazon"  # Replace with actual API
    
    def search_product(self, product_name):
        """Example of using a third-party API"""
        # This is more reliable and legal than direct scraping
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"query": product_name, "marketplace": "US"}
        
        # response = requests.get(f"{self.base_url}/search", headers=headers, params=params)
        # return response.json()
        
        print("For production, use official APIs or scraping services")
        return None

# Example usage with rate limiting and error handling
def safe_batch_check(deals, max_attempts=3):
    """Safely check Amazon prices with retries and delays"""
    checker = SaferAmazonPriceChecker()
    results = []
    
    for i, deal in enumerate(deals[:5]):  # Limit to 5 for safety
        print(f"\n[{i+1}/{len(deals)}] Checking: {deal['title']}")
        
        success = False
        for attempt in range(max_attempts):
            try:
                result = checker.search_amazon_safely(deal['title'])
                if result:
                    results.append({
                        "deal": deal,
                        "amazon_results": result
                    })
                    success = True
                    break
                else:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(random.uniform(10, 20))  # Longer delay between retries
                    
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
        
        if not success:
            print(f"Failed to get results for {deal['title']}")
            results.append({
                "deal": deal,
                "amazon_results": None
            })
        
        # Longer delay between products
        if i < len(deals) - 1:
            delay = random.uniform(10, 30)
            print(f"Waiting {delay:.1f} seconds before next product...")
            time.sleep(delay)
    
    return results

def calculate_profit_potential(footlocker_deal, amazon_prices):
    """Calculate potential profit from reselling"""
    if not amazon_prices:
        print("  No Amazon prices to compare")
        return None
        
    # Extract numeric price from Footlocker deal
    footlocker_price_match = re.search(r'[\d,]+\.?\d*', footlocker_deal['current_price'])
    if not footlocker_price_match:
        return None
        
    footlocker_price = float(footlocker_price_match.group().replace(',', ''))
    print(f"  Footlocker price: ${footlocker_price}")
    
    # Find the lowest Amazon price
    lowest_amazon_price = min(amazon_prices, key=lambda x: x['price'])
    print(f"  Lowest Amazon price: ${lowest_amazon_price['price']}")
    
    # Calculate profit (before fees)
    gross_profit = lowest_amazon_price['price'] - footlocker_price
    profit_margin = (gross_profit / footlocker_price) * 100 if footlocker_price > 0 else 0
    
    # Estimate Amazon fees (roughly 15% for most categories)
    amazon_fees = lowest_amazon_price['price'] * 0.15
    net_profit = gross_profit - amazon_fees
    net_margin = (net_profit / footlocker_price) * 100 if footlocker_price > 0 else 0
    
    result = {
        "footlocker_price": footlocker_price,
        "amazon_price": lowest_amazon_price['price'],
        "amazon_title": lowest_amazon_price['title'],
        "amazon_url": None,  # URL not available in current implementation
        "gross_profit": round(gross_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "estimated_fees": round(amazon_fees, 2),
        "net_profit": round(net_profit, 2),
        "net_margin": round(net_margin, 2),
        "profitable": net_profit > 5  # Consider profitable if net profit > $5
    }
    
    print(f"  Net profit: ${result['net_profit']} ({'Profitable' if result['profitable'] else 'Not profitable'})")
    return result

def batch_check_amazon_prices(deals, delay=3):
    """Check Amazon prices for a batch of deals"""
    checker = SaferAmazonPriceChecker()
    results = []
    
    for i, deal in enumerate(deals[:5]):  # Limit to 5 for safety
        print(f"\n[{i+1}/{len(deals)}] Checking: {deal['title']}")
        
        try:
            amazon_prices = checker.search_amazon_safely(deal['title'])
            profit_analysis = calculate_profit_potential(deal, amazon_prices) if amazon_prices else None
            
            result = {
                "deal": deal,
                "amazon_results": amazon_prices,
                "profit_analysis": profit_analysis
            }
            
            # Debug: print what we're adding
            print(f"  Result keys: {result.keys()}")
            if profit_analysis:
                print(f"  Profit: ${profit_analysis.get('net_profit', 'N/A')}")
                print(f"  Profitable: {'YES' if profit_analysis['profitable'] else 'NO'}")
            
            results.append(result)
            
            # Longer delay between products
            if i < len(deals) - 1:
                delay_time = random.uniform(10, 30)
                print(f"Waiting {delay_time:.1f} seconds before next product...")
                time.sleep(delay_time)
                
        except Exception as e:
            print(f"Error processing deal: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "deal": deal,
                "amazon_results": None,
                "profit_analysis": None
            })
    
    print(f"\nBatch check complete. Processed {len(results)} deals")
    return results

if __name__ == "__main__":
    # Example usage
    test_deals = [
        {"title": "Nike Air Force 1", "current_price": "$79.99"},
        {"title": "Adidas Samba", "current_price": "$89.99"}
    ]
    
    # For development/testing only
    # results = safe_batch_check(test_deals)
    
    # For production, use official APIs
    print("\nIMPORTANT: For production use, consider:")
    print("1. Amazon Product Advertising API (official)")
    print("2. Third-party scraping APIs (ScrapingBee, ScraperAPI)")
    print("3. Residential proxies for large-scale scraping")
    print("4. Always respect robots.txt and terms of service")