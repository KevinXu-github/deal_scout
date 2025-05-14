# tiktok_trend_tracker.py - SIMPLIFIED VERSION TO START
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class TikTokTrendTracker:
    def __init__(self):
        self.trending_hashtags = [
            "tiktokmademebuyit",
            "amazonfinds",
            "targetfinds"
        ]
    
    def get_trending_products(self):
        """For now, return mock data to test the integration"""
        # TODO: Replace with actual TikTok scraping later
        return [
            {
                'name': 'stanley cup tumbler',
                'store': 'target',
                'total_views': 5000000,
                'mention_count': 45,
                'avg_engagement': 12.5,
                'trending_score': 8.7
            },
            {
                'name': 'rare beauty blush',
                'store': 'target',
                'total_views': 3200000,
                'mention_count': 28,
                'avg_engagement': 15.2,
                'trending_score': 7.9
            }
        ]

def find_matching_deals(trending_product, all_deals):
    """Find deals that match a trending product"""
    matches = []
    keywords = trending_product['name'].lower().split()
    
    for deal in all_deals:
        title_lower = deal['title'].lower()
        match_count = sum(1 for keyword in keywords if keyword in title_lower)
        
        # If at least half the keywords match
        if match_count >= len(keywords) / 2:
            deal_copy = deal.copy()
            deal_copy['trending_data'] = {
                'trending_score': trending_product['trending_score'],
                'tiktok_views': trending_product['total_views'],
                'tiktok_mentions': trending_product['mention_count'],
                'engagement_rate': trending_product['avg_engagement']
            }
            matches.append(deal_copy)
    
    return matches