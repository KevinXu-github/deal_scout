from flask import Flask, render_template, jsonify, request
import deal_scraper
import threading
import json
import os
from datetime import datetime

app = Flask(__name__)
deals_data = []
last_scrape_time = None
is_scraping = False

def background_scraper():
    """Run the scraper in the background"""
    global deals_data, last_scrape_time, is_scraping
    is_scraping = True
    try:
        deals_data = deal_scraper.run_all_scrapers(pages=1)
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
    
    # Create a simple template file
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Deal Scout</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .deal-card { height: 100%; }
        .discount-badge {
            position: absolute;
            top: 10px;
            right: 10px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">Deal Scout</a>
            <button class="btn btn-light" id="scrape-btn">Scrape Deals</button>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row mb-3">
            <div class="col">
                <div class="input-group">
                    <span class="input-group-text">Min Discount</span>
                    <select class="form-select" id="discount-filter">
                        <option value="0">All Deals</option>
                        <option value="20">20% or more</option>
                        <option value="30">30% or more</option>
                        <option value="50">50% or more</option>
                    </select>
                    <button class="btn btn-primary" id="filter-btn">Filter</button>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12 mb-4">
                <div class="alert alert-info" id="status-alert">
                    <span id="status-text">
                        {% if last_scrape %}
                            Last scraped: {{ last_scrape.strftime('%Y-%m-%d %H:%M') }}
                        {% else %}
                            No data available. Click "Scrape Deals" to find deals.
                        {% endif %}
                    </span>
                    <div class="spinner-border spinner-border-sm text-primary float-end" id="loading-spinner" style="display: none;"></div>
                </div>
            </div>
        </div>
        
        <div class="row row-cols-1 row-cols-md-3 g-4" id="deals-container"></div>
    </div>

    <script>
        // Elements
        const dealsContainer = document.getElementById('deals-container');
        const scrapeBtn = document.getElementById('scrape-btn');
        const filterBtn = document.getElementById('filter-btn');
        const discountFilter = document.getElementById('discount-filter');
        const statusText = document.getElementById('status-text');
        const loadingSpinner = document.getElementById('loading-spinner');
        
        // Load initial deals
        loadDeals();
        
        // Check status every 5 seconds
        setInterval(checkStatus, 5000);
        
        // Event listeners
        scrapeBtn.addEventListener('click', startScraping);
        filterBtn.addEventListener('click', applyFilters);
        
        function loadDeals() {
            const minDiscount = discountFilter.value;
            fetch(`/api/deals?min_discount=${minDiscount}`)
                .then(response => response.json())
                .then(deals => {
                    dealsContainer.innerHTML = '';
                    
                    if (deals.length === 0) {
                        dealsContainer.innerHTML = '<div class="col-12 text-center"><h3>No deals found</h3></div>';
                        return;
                    }
                    
                    // Sort by discount (highest first)
                    deals.sort((a, b) => b.discount_pct - a.discount_pct);
                    
                    deals.forEach(deal => {
                        const discountClass = deal.discount_pct >= 50 ? 'bg-danger' : 
                                             deal.discount_pct >= 30 ? 'bg-warning' : 'bg-info';
                        
                        dealsContainer.innerHTML += `
                            <div class="col">
                                <div class="card deal-card">
                                    <div class="badge ${discountClass} discount-badge">${deal.discount_pct}% OFF</div>
                                    <div class="card-body">
                                        <h5 class="card-title">${deal.title}</h5>
                                        <p class="card-text">
                                            <del>${deal.original_price}</del><br>
                                            <strong class="text-success">${deal.current_price}</strong>
                                        </p>
                                        <a href="${deal.url}" target="_blank" class="btn btn-primary">View Deal</a>
                                    </div>
                                    <div class="card-footer text-muted">
                                        ${deal.store} | ${new Date(deal.date_found).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                });
        }
        
        function startScraping() {
            loadingSpinner.style.display = 'inline-block';
            statusText.textContent = 'Scraping in progress...';
            
            fetch('/api/scrape', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'already_running') {
                        alert('A scraping job is already running');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    loadingSpinner.style.display = 'none';
                    statusText.textContent = 'Error starting scrape job';
                });
        }
        
        function checkStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.is_scraping) {
                        loadingSpinner.style.display = 'inline-block';
                        statusText.textContent = 'Scraping in progress...';
                    } else {
                        loadingSpinner.style.display = 'none';
                        if (data.last_scrape) {
                            statusText.textContent = `Last scraped: ${data.last_scrape}`;
                            loadDeals();
                        }
                    }
                });
        }
        
        function applyFilters() {
            loadDeals();
        }
    </script>
</body>
</html>
            ''')
    
    app.run(debug=True, host='0.0.0.0', port=5000)