import os
import time
from typing import List, Dict
from datetime import datetime
from collections import defaultdict
import json
from .crawler import BOJCrawler

def read_usernames(filename: str) -> List[str]:
    """Read usernames from a text file, one username per line"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Read lines, strip whitespace, and filter out empty lines
            usernames = [line.strip() for line in f if line.strip()]
        return usernames
    except Exception as e:
        print(f"Error reading usernames from {filename}: {str(e)}")
        return []

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

def generate_monthly_report(problems: List[Dict], username: str) -> Dict[str, Dict[str, int]]:
    """Generate a report of problems solved per month for a user"""
    monthly_stats = defaultdict(lambda: defaultdict(int))
    for problem in problems:
        try:
            submission_time = datetime.strptime(problem['submission_time'], "%Y-%m-%d %H:%M:%S")
            month_key = submission_time.strftime("%Y-%m")
            monthly_stats[month_key][username] += 1
        except (KeyError, ValueError) as e:
            print(f"Error processing submission time: {str(e)}")
            continue
    return dict(monthly_stats)

def save_monthly_report(monthly_stats: Dict[str, Dict[str, int]], all_usernames: List[str]):
    """Save monthly statistics to a single report file"""
    try:
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # Sort months in descending order
        sorted_months = sorted(monthly_stats.keys(), reverse=True)
        
        # Create a nicely formatted report
        formatted_report = {
            "monthly_stats": {
                month: {
                    "total_solved": sum(monthly_stats[month].values()),
                    "users": dict(sorted(
                        # Include all users, defaulting to 0 if they didn't solve any
                        {username: monthly_stats[month].get(username, 0) for username in all_usernames}.items(),
                        key=lambda x: x[1],  # Sort by number of problems solved
                        reverse=True  # Descending order
                    ))
                }
                for month in sorted_months
            },
            "total_users": len(all_usernames),
            "total_months": len(monthly_stats),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        report_file = os.path.join(report_dir, "monthly_solved_problems.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_report, f, ensure_ascii=False, indent=2)
        print(f"Monthly report saved to {report_file}")
    except Exception as e:
        print(f"Error saving monthly report: {str(e)}")

def batch_crawl(usernames: List[str], start_date: str = None, end_date: str = None, target_month: str = None, generate_report: bool = True, proxies: Dict[str, str] = None):
    """Crawl BOJ for multiple users"""
    total_users = len(usernames)
    
    # Build filter description for logging
    filter_desc = ""
    if start_date or end_date:
        if start_date and end_date:
            filter_desc = f" (filtering from {start_date} to {end_date})"
        elif start_date:
            filter_desc = f" (filtering from {start_date})"
        elif end_date:
            filter_desc = f" (filtering until {end_date})"
    elif target_month:
        filter_desc = f" (filtering by month: {target_month})"
    
    if proxies:
        proxy_desc = f" using proxy: {proxies}"
        filter_desc += proxy_desc
    
    print(f"Starting batch crawl for {total_users} users{filter_desc}")
    
    # Create a combined monthly report if requested
    combined_monthly_stats = defaultdict(lambda: defaultdict(int))
    
    for i, username in enumerate(usernames, 1):
        print(f"\nProcessing user {i}/{total_users}: {username}")
        try:
            crawler = BOJCrawler(username, start_date=start_date, end_date=end_date, target_month=target_month, proxies=proxies)
            problems = crawler.get_solved_problems()
            
            if problems:
                print(f"Found {len(problems)} problems for user {username}")
                crawler.save_to_json(problems)
                
                # Generate monthly stats for this user if report generation is enabled
                if generate_report:
                    user_monthly_stats = generate_monthly_report(problems, username)
                    
                    # Merge into combined stats
                    for month, user_stats in user_monthly_stats.items():
                        for user, count in user_stats.items():
                            combined_monthly_stats[month][user] = count
            else:
                print(f"No problems found for user {username}")
                
            # Add a small delay between users to be respectful to the server
            if i < total_users:
                print("Waiting 5 seconds before next user...")
                time.sleep(5)
                
        except Exception as e:
            print(f"Error processing user {username}: {str(e)}")
            continue
    
    # Save the combined monthly report if requested
    if generate_report:
        save_monthly_report(combined_monthly_stats, usernames)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch crawl BOJ solved problems for multiple users')
    parser.add_argument('-f', '--file', required=True, help='Text file containing usernames (one per line)')
    parser.add_argument('-m', '--month', help='Filter by submission month in YYYYMM format (e.g., 202401)')
    parser.add_argument('-s', '--start-date', help='Start date filter in YYMMDD format (e.g., 240315 for Mar 15, 2024)')
    parser.add_argument('-e', '--end-date', help='End date filter in YYMMDD format (e.g., 240415 for Apr 15, 2024)')
    parser.add_argument('--no-report', action='store_true', help='Skip generating monthly report')
    parser.add_argument('--proxy', nargs=2, metavar=('http', 'https'), help='Use a proxy for requests (e.g., --proxy http 127.0.0.1:8080)')
    args = parser.parse_args()
    
    # Validate month format if provided
    if args.month:
        try:
            datetime.strptime(args.month, "%Y%m")
        except ValueError:
            print("Error: Month must be in YYYYMM format (e.g., 202401)")
            return
    
    # Validate start date format if provided
    if args.start_date and not validate_yymmdd_date(args.start_date):
        print("Error: Start date must be in YYMMDD format (e.g., 240315 for Mar 15, 2024)")
        return
    
    # Validate end date format if provided
    if args.end_date and not validate_yymmdd_date(args.end_date):
        print("Error: End date must be in YYMMDD format (e.g., 240415 for Apr 15, 2024)")
        return
    
    # Check for conflicting arguments
    if (args.start_date or args.end_date) and args.month:
        print("Error: Cannot use both date range filters (--start-date, --end-date) and month filter (--month) at the same time")
        return
    
    # Read usernames from file
    usernames = read_usernames(args.file)
    if not usernames:
        print(f"No valid usernames found in {args.file}")
        return
    
    # Start batch crawling
    proxies = None
    if args.proxy:
        proxies = {
            'http': args.proxy[0],
            'https': args.proxy[1]
        }
    batch_crawl(usernames, start_date=args.start_date, end_date=args.end_date, target_month=args.month, generate_report=not args.no_report, proxies=proxies)

if __name__ == "__main__":
    main() 