#!/usr/bin/env python3
"""
Standalone script wrapper for boj-crawler package.
This script provides the same functionality as the package's CLI but as a standalone script.
"""

import argparse
import sys
from datetime import datetime

try:
    from boj_crawler import BOJCrawler
except ImportError:
    print("Error: boj-crawler package not found. Please install it with:")
    print("  pip install -e .")
    sys.exit(1)

def validate_yymmdd_date(date_str: str) -> bool:
    """Validate yymmdd format date string"""
    if not date_str or len(date_str) != 6:
        return False
    try:
        year = 2000 + int(date_str[:2])
        month = int(date_str[2:4])
        day = int(date_str[4:6])
        datetime(year, month, day)
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Crawl BOJ solved problems for a user')
    parser.add_argument('-u', '--username', required=True, help='BOJ username to crawl')
    parser.add_argument('-m', '--month', help='Filter by submission month in YYYYMM format (e.g., 202401)')
    parser.add_argument('-s', '--start-date', help='Start date filter in YYMMDD format (e.g., 240315 for Mar 15, 2024)')
    parser.add_argument('-e', '--end-date', help='End date filter in YYMMDD format (e.g., 240415 for Apr 15, 2024)')
    parser.add_argument('--proxy-http', help='HTTP proxy server (e.g., http://proxy.example.com:8080)')
    parser.add_argument('--proxy-https', help='HTTPS proxy server (e.g., https://proxy.example.com:8080)')
    parser.add_argument('--proxy-all', help='Proxy server for both HTTP and HTTPS (e.g., http://proxy.example.com:8080)')
    args = parser.parse_args()
    
    # Validate month format if provided
    if args.month:
        try:
            datetime.strptime(args.month, "%Y%m")
        except ValueError:
            print("Error: Month must be in YYYYMM format (e.g., 202401)")
            sys.exit(1)
    
    # Validate start date format if provided
    if args.start_date and not validate_yymmdd_date(args.start_date):
        print("Error: Start date must be in YYMMDD format (e.g., 240315 for Mar 15, 2024)")
        sys.exit(1)
    
    # Validate end date format if provided
    if args.end_date and not validate_yymmdd_date(args.end_date):
        print("Error: End date must be in YYMMDD format (e.g., 240415 for Apr 15, 2024)")
        sys.exit(1)
    
    # Check for conflicting arguments
    if (args.start_date or args.end_date) and args.month:
        print("Error: Cannot use both date range filters (--start-date, --end-date) and month filter (--month) at the same time")
        sys.exit(1)
    
    # Configure proxy settings
    proxies = None
    if args.proxy_all:
        proxies = {
            'http': args.proxy_all,
            'https': args.proxy_all
        }
    elif args.proxy_http or args.proxy_https:
        proxies = {}
        if args.proxy_http:
            proxies['http'] = args.proxy_http
        if args.proxy_https:
            proxies['https'] = args.proxy_https
    
    user_id = args.username
    crawler = BOJCrawler(user_id, start_date=args.start_date, end_date=args.end_date, target_month=args.month, proxies=proxies)
    
    # Build filter description for logging
    filter_desc = ""
    if args.start_date or args.end_date:
        if args.start_date and args.end_date:
            filter_desc = f" (filtering from {args.start_date} to {args.end_date})"
        elif args.start_date:
            filter_desc = f" (filtering from {args.start_date})"
        elif args.end_date:
            filter_desc = f" (filtering until {args.end_date})"
    elif args.month:
        filter_desc = f" (filtering by month: {args.month})"
    
    if proxies:
        proxy_desc = f" using proxy: {proxies}"
        filter_desc += proxy_desc
    
    crawler.log_info(f"Starting crawler for user: {user_id}{filter_desc}")
    problems = crawler.get_solved_problems()
    
    if problems:
        crawler.log_info(f"Total problems found: {len(problems)}")
        crawler.save_to_json(problems)
    else:
        crawler.log_error("No problems found or an error occurred")


if __name__ == "__main__":
    main()
