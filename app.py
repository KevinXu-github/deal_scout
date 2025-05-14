from flask import Flask, render_template, jsonify, request
import deal_scraper
import amazon_price_checker
import threading
import json
import os
import re
from datetime import datetime
import importlib
import tiktok_trend_tracker



# Force reload of deal_scraper module to ensure latest changes
importlib.reload(deal_scraper)

app = Flask(__name__)
deals_data = []
profit_data = []
last_scrape_time = None
is_scraping = False
is_checking_amazon = False
scrape_progress = {"current": 0, "total": 7, "current_store": "", "category": "all"}  # Track progress

def clean_product_title(title):
    """Clean product title to show only the item name"""
    # Remove any review information
    title = re.sub(r'Average customer rating.*', '', title, flags=re.IGNORECASE).strip()
    title = re.sub(r'\d+ reviews.*', '', title, flags=re.IGNORECASE).strip()
    title = re.sub(r'\[\d+ out of \d+ stars\].*', '', title, flags=re.IGNORECASE).strip()
    
    # Remove gender/color info if it appears after "Men's" or "Women's"
    title = re.sub(r"(Men's|Women's).*", r'\1', title, flags=re.IGNORECASE).strip()
    
    # Remove any "On Sale" text
    title = re.sub(r'This item is on sale.*', '', title, flags=re.IGNORECASE).strip()
    
    # Remove any price information
    title = re.sub(r'\$\d+\.\d+.*', '', title, flags=re.IGNORECASE).strip()
    
    return title

def update_scrape_progress(current, total, current_store, category="all"):
    """Update the scraping progress"""
    global scrape_progress
    scrape_progress = {
        "current": current,
        "total": total,
        "current_store": current_store,
        "category": category
    }

def background_scraper(category="all"):
    """Run the scraper in the background"""
    global deals_data, last_scrape_time, is_scraping, scrape_progress
    is_scraping = True
    try:
        # Check if the function exists
        if not hasattr(deal_scraper, 'run_all_scrapers'):
            print("Error: run_all_scrapers function not found in deal_scraper module")
            print(f"Available functions in deal_scraper: {dir(deal_scraper)}")
            return
            
        # Run scrapers based on category
        raw_deals_data = deal_scraper.run_all_scrapers(pages=1, progress_callback=update_scrape_progress, category=category)
        
        # Clean product titles and validate URLs
        deals_data = []
        for deal in raw_deals_data:
            # Only include deals with valid URLs
            if deal.get('url', '').startswith('http'):
                deal['title'] = clean_product_title(deal['title'])
                deals_data.append(deal)
            else:
                print(f"Skipping deal with invalid URL: {deal.get('title', 'Unknown')}")
            
        last_scrape_time = datetime.now()
        with open('deals_backup.json', 'w') as f:
            json.dump(deals_data, f)
        
        print(f"Successfully saved {len(deals_data)} deals with valid URLs")
        
        # Reset progress
        update_scrape_progress(0, 0, "")
    except Exception as e:
        print(f"Error in background_scraper: {e}")
        import traceback
        traceback.print_exc()
    finally:
        is_scraping = False

def background_amazon_checker():
    """Check Amazon prices in the background"""
    global profit_data, is_checking_amazon
    is_checking_amazon = True
    print("Starting Amazon price check...")
    try:
        # Check top deals (highest discount) for profit potential
        # Prioritize beauty products if available
        beauty_deals = [d for d in deals_data if d.get('category', '').lower() == 'beauty']
        
        if beauty_deals:
            top_deals = sorted(beauty_deals, key=lambda x: x['discount_pct'], reverse=True)[:10]
            print(f"Checking {len(top_deals)} beauty deals...")
        else:
            top_deals = sorted(deals_data, key=lambda x: x['discount_pct'], reverse=True)[:10]
            print(f"Checking {len(top_deals)} deals...")
        
        profit_results = amazon_price_checker.batch_check_amazon_prices(top_deals, delay=3)
        print(f"Got {len(profit_results)} results")
        
        # Filter to only profitable deals - handle missing profit_analysis
        profit_data = []
        for result in profit_results:
            if result and 'profit_analysis' in result and result['profit_analysis'] and result['profit_analysis']['profitable']:
                profit_data.append(result)
        
        print(f"Found {len(profit_data)} profitable deals")
        
        # Save profit data
        with open('profit_analysis.json', 'w') as f:
            json.dump(profit_data, f)
            
    except Exception as e:
        print(f"Error checking Amazon prices: {e}")
        import traceback
        traceback.print_exc()
    finally:
        is_checking_amazon = False
        print("Amazon price check completed")



# Add these global variables
trending_data = []
is_checking_trends = False

# Add this function
def background_trend_checker():
    """Check trending products and match with deals"""
    global trending_data, is_checking_trends
    is_checking_trends = True
    
    try:
        # Get trending products from TikTok
        tracker = tiktok_trend_tracker.TikTokTrendTracker()
        trending_products = tracker.get_trending_products()
        
        # Match with your current deals
        trending_deals = []
        for product in trending_products:
            matches = tiktok_trend_tracker.find_matching_deals(product, deals_data)
            trending_deals.extend(matches)
        
        trending_data = trending_deals
        print(f"Found {len(trending_deals)} trending deals")
        
    except Exception as e:
        print(f"Error checking trends: {e}")
    finally:
        is_checking_trends = False

# Add these routes
@app.route('/trending')
def trending_page():
    """Page showing trending deals"""
    return render_template('trending.html', trending_deals=trending_data)

@app.route('/api/check-trends', methods=['POST'])
def check_trends():
    """Start checking for trending products"""
    global is_checking_trends
    
    if is_checking_trends:
        return jsonify({'status': 'already_running'})
    
    thread = threading.Thread(target=background_trend_checker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})


@app.route('/')
def index():
    """Main page route"""
    global deals_data, last_scrape_time
    
    # Load from backup if exists and we don't have data
    if not deals_data and os.path.exists('deals_backup.json'):
        try:
            with open('deals_backup.json', 'r') as f:
                deals_data = json.load(f)
                last_scrape_time = datetime.fromtimestamp(os.path.getmtime('deals_backup.json'))
        except Exception:
            pass
    
    return render_template('index.html', deals=deals_data, last_scrape=last_scrape_time)

@app.route('/profit')
def profit_analysis():
    """Profit analysis page"""
    global profit_data
    
    # Load profit data if exists
    if not profit_data and os.path.exists('profit_analysis.json'):
        try:
            with open('profit_analysis.json', 'r') as f:
                profit_data = json.load(f)
        except Exception:
            pass
    
    return render_template('profit.html', profit_data=profit_data)

@app.route('/api/deals')
def get_deals():
    """API endpoint to get deals data with filtering"""
    global deals_data
    min_discount = request.args.get('min_discount', 0, type=int)
    store_filter = request.args.get('store', '', type=str)
    category_filter = request.args.get('category', '', type=str)
    
    filtered_deals = deals_data
    
    # Filter by discount
    if min_discount > 0:
        filtered_deals = [d for d in filtered_deals if d['discount_pct'] >= min_discount]
    
    # Filter by store
    if store_filter:
        filtered_deals = [d for d in filtered_deals if d['store'].lower() == store_filter.lower()]
    
    # Filter by category
    if category_filter:
        filtered_deals = [d for d in filtered_deals if d.get('category', '').lower() == category_filter.lower()]
    
    return jsonify(filtered_deals)

@app.route('/api/stores')
def get_stores():
    """API endpoint to get list of available stores"""
    global deals_data
    stores = list(set([deal['store'] for deal in deals_data]))
    return jsonify(stores)

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """API endpoint to start a scraping job"""
    global is_scraping
    if is_scraping:
        return jsonify({'status': 'already_running'})
    
    # Get category from request
    category = request.json.get('category', 'all') if request.is_json else 'all'
    
    thread = threading.Thread(target=background_scraper, args=(category,))
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started', 'category': category})

@app.route('/api/check-amazon', methods=['POST'])
def check_amazon():
    """API endpoint to check Amazon prices"""
    global is_checking_amazon
    if is_checking_amazon:
        return jsonify({'status': 'already_running'})
    
    thread = threading.Thread(target=background_amazon_checker)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/status')
def get_status():
    """API endpoint to get scraping status"""
    global is_scraping, is_checking_amazon, last_scrape_time, deals_data, profit_data, scrape_progress
    return jsonify({
        'is_scraping': is_scraping,
        'is_checking_amazon': is_checking_amazon,
        'last_scrape': last_scrape_time.strftime("%Y-%m-%d %H:%M:%S") if last_scrape_time else None,
        'deals_count': len(deals_data),
        'profitable_deals_count': len(profit_data),
        'scrape_progress': scrape_progress  # Add progress tracking
    })

if __name__ == '__main__':
    # Create templates folder if needed
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)