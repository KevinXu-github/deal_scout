# Deal Scout

A comprehensive web scraping and arbitrage analysis platform that automatically discovers discounted products across major retailers and evaluates their resale potential on Amazon.

## Overview

Deal Scout streamlines the process of finding profitable arbitrage opportunities by scraping deals from multiple retail websites, comparing prices with Amazon listings, and calculating potential profits after fees. The platform features a real-time web dashboard for monitoring scraping progress and analyzing results.

## Features

### Multi-Store Scraping
- **Sportswear**: Footlocker, Eastbay, Finish Line, Dick's Sporting Goods, Adidas, Reebok, Hibbett Sports
- **Beauty**: Walmart Beauty, Target Beauty, CVS Beauty, Ulta Beauty
- **Universal Engine**: Configurable scraper that can be extended to any e-commerce site

### Profit Analysis
- Automated Amazon price checking with anti-detection measures
- Net profit calculations including estimated Amazon seller fees (~15%)
- Margin analysis and profitability scoring
- Batch processing with intelligent rate limiting

### Web Dashboard
- Real-time scraping progress with store-by-store tracking
- Advanced filtering by discount percentage, store, and category
- Responsive Bootstrap interface with mobile support
- Separate views for deals, profit analysis, and trending products

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/deal-scout.git
cd deal-scout

# Install dependencies
pip install flask requests beautifulsoup4 cloudscraper lxml

# Run application
python app.py
```

Access the dashboard at `http://localhost:5000`

## Usage

### Web Interface
1. **Scrape Deals**: Click the scrape button to collect current offers from all configured stores
2. **Filter Results**: Use discount percentage and store filters to find specific deals
3. **Profit Analysis**: Navigate to the profit page and click "Check Amazon Prices" to identify arbitrage opportunities
4. **View Details**: Click through to retailer websites to complete purchases

### Command Line
```python
# Run category-specific scraping
from deal_scraper import run_all_scrapers
deals = run_all_scrapers(pages=1, category="beauty")

# Test individual store configuration
from deal_scraper import test_store_scraper
results = test_store_scraper("Footlocker", pages=1)

# Analyze Amazon pricing
from amazon_price_checker import batch_check_amazon_prices
profit_analysis = batch_check_amazon_prices(deals[:10])
```

## Configuration

### Adding New Stores
Extend the platform by adding store configurations to `deal_scraper.py`:

```python
new_store_config = {
    "name": "Store Name",
    "base_url": "https://store.com/sale",
    "category": "Beauty",
    "selectors": {
        "product_container": ".product-card",
        "title": ".product-name",
        "current_price": ".sale-price",
        "original_price": ".regular-price",
        "link": "a.product-link",
        "link_prefix": "https://store.com"
    },
    "single_page": True,  # or configure pagination
    "filters": {
        "min_discount": 30,
        "keywords": ["skincare", "makeup"]
    }
}
```

### Anti-Detection Features
- Rotating user agents and realistic headers
- Human-like delays (2-30 seconds between requests)
- CloudScraper integration for Cloudflare protection
- Session management and cookie handling
- CAPTCHA detection and graceful error handling

## API Reference

### Core Endpoints
- `GET /api/deals` - Retrieve deals with optional filtering parameters
- `POST /api/scrape` - Initiate scraping job for specified category
- `GET /api/stores` - List all configured retailers
- `GET /api/status` - Check current scraping and analysis status

### Profit Analysis
- `POST /api/check-amazon` - Start Amazon price comparison analysis
- `POST /api/check-trends` - Analyze trending product opportunities

### Parameters
```javascript
// Filter deals by discount and store
GET /api/deals?min_discount=30&store=Footlocker&category=beauty

// Start category-specific scraping
POST /api/scrape
Content-Type: application/json
{"category": "sportswear"}
```

## Architecture

```
deal-scout/
├── app.py                    # Flask web application and API routes
├── deal_scraper.py          # Universal scraping engine with store configs
├── amazon_price_checker.py  # Amazon price comparison with anti-bot measures
├── tiktok_trend_tracker.py  # Social media trend analysis (beta)
├── templates/
│   ├── index.html           # Main deals dashboard
│   ├── profit.html          # Arbitrage analysis interface
│   └── trending.html        # Social trend integration
├── deals_backup.json        # Persistent deal storage
└── profit_analysis.json     # Cached profit calculations
```

## Rate Limiting & Safety

The platform implements several measures to ensure responsible scraping:

- **Request Throttling**: 2-30 second randomized delays between requests
- **Concurrent Limits**: Maximum 5 simultaneous store scrapes
- **Session Management**: Persistent cookies and realistic browsing patterns
- **Error Handling**: Graceful degradation with retry mechanisms
- **Monitoring**: Built-in progress tracking and status reporting

## Important Considerations

### Legal Compliance
- This tool is designed for educational and research purposes
- Users must comply with retailer terms of service
- Respect robots.txt files and rate limiting requirements
- Consider using official APIs for production applications

### Amazon Integration
The Amazon price checker uses web scraping techniques that may trigger anti-bot measures. For production use, consider:
- Amazon Product Advertising API (official)
- Third-party scraping services (ScrapingBee, ScraperAPI)
- Residential proxy networks for scale

### Performance Optimization
- Deals are cached locally to reduce redundant requests
- Background processing prevents UI blocking
- Intelligent filtering reduces Amazon API calls
- Batch processing optimizes request efficiency

## Troubleshooting

**Scraping Issues**
- Verify store website accessibility and structure
- Update CSS selectors if websites change layouts
- Check for IP blocking or CAPTCHA challenges
- Ensure proper rate limiting configuration

**Amazon Analysis Problems**
- Implement longer delays if rate limited
- Consider proxy rotation for higher volumes
- Switch to official Amazon API for production use
- Monitor for CAPTCHA detection

## Contributing

1. Fork the repository and create a feature branch
2. Add new store configurations following existing patterns
3. Test thoroughly with `test_store_scraper()` function
4. Ensure compliance with rate limiting and safety measures
5. Submit pull request with detailed description

## License

This project is provided for educational purposes. Users are responsible for ensuring compliance with applicable terms of service and regulations.
