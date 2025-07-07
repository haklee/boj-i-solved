import os
import time
from typing import List, Dict
from boj_crawler import BOJCrawler
from collections import defaultdict
from datetime import datetime
import json

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

def batch_crawl(usernames: List[str], target_month: str = None):
    """Crawl BOJ for multiple users"""
    total_users = len(usernames)
    print(f"Starting batch crawl for {total_users} users" + 
          (f" (filtering by month: {target_month})" if target_month else ""))
    
    # Create a combined monthly report
    combined_monthly_stats = defaultdict(lambda: defaultdict(int))
    
    for i, username in enumerate(usernames, 1):
        print(f"\nProcessing user {i}/{total_users}: {username}")
        try:
            crawler = BOJCrawler(username, target_month)
            problems = crawler.get_solved_problems()
            
            if problems:
                print(f"Found {len(problems)} problems for user {username}")
                crawler.save_to_json(problems)
                
                # Generate monthly stats for this user
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
    
    # Save the combined monthly report
    save_monthly_report(combined_monthly_stats, usernames)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch crawl BOJ solved problems for multiple users')
    parser.add_argument('-f', '--file', required=True, help='Text file containing usernames (one per line)')
    parser.add_argument('-d', '--date', help='Filter by submission month in YYYYMM format (e.g., 202401)')
    args = parser.parse_args()
    
    # Validate date format if provided
    if args.date:
        try:
            from datetime import datetime
            datetime.strptime(args.date, "%Y%m")
        except ValueError:
            print("Error: Date must be in YYYYMM format (e.g., 202401)")
            return
    
    # Read usernames from file
    usernames = read_usernames(args.file)
    if not usernames:
        print(f"No valid usernames found in {args.file}")
        return
    
    # Start batch crawling
    batch_crawl(usernames, args.date)

if __name__ == "__main__":
    main() 