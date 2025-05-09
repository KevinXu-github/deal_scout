from flask import Flask, render_template, jsonify, request
import deal_scraper
import threading
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
deals_data = []
last_scrape_time = None
is_scraping = False

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

def background_scraper():
    """Run the scraper in the background"""
    global deals_data, last_scrape_time, is_scraping
    is_scraping = True
    try:
        raw_deals_data = deal_scraper.run_all_scrapers(pages=1)
        
        # Clean product titles
        deals_data = []
        for deal in raw_deals_data:
            deal['title'] = clean_product_title(deal['title'])
            deals_data.append(deal)
            
        last_scrape_time = datetime.now()
        with open('deals_backup.json', 'w') as f:
            json.dump(deals_data, f)
    except Exception as e:
        print(f"Error: {e}")
    is_scraping = False

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

@app.route('/api/deals')
def get_deals():
    """API endpoint to get deals data with filtering"""
    global deals_data
    min_discount = request.args.get('min_discount', 0, type=int)
    filtered_deals = [d for d in deals_data if d['discount_pct'] >= min_discount]
    return jsonify(filtered_deals)

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """API endpoint to start a scraping job"""
    global is_scraping
    if is_scraping:
        return jsonify({'status': 'already_running'})
    
    thread = threading.Thread(target=background_scraper)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/status')
def get_status():
    """API endpoint to get scraping status"""
    global is_scraping, last_scrape_time, deals_data
    return jsonify({
        'is_scraping': is_scraping,
        'last_scrape': last_scrape_time.strftime("%Y-%m-%d %H:%M:%S") if last_scrape_time else None,
        'deals_count': len(deals_data)
    })

if __name__ == '__main__':
    # Create templates folder if needed
    os.makedirs('templates', exist_ok=True)
    
    # Create the template file if it doesn't exist
    if not os.path.exists('templates/index.html'):
        # Index template code here would be similar to what we created earlier
        pass
    
    app.run(debug=True, host='0.0.0.0', port=5000)