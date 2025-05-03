import os
import time
from typing import List
from boj_crawler import BOJCrawler

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

def batch_crawl(usernames: List[str], target_month: str = None):
    """Crawl BOJ for multiple users"""
    total_users = len(usernames)
    print(f"Starting batch crawl for {total_users} users" + 
          (f" (filtering by month: {target_month})" if target_month else ""))
    
    for i, username in enumerate(usernames, 1):
        print(f"\nProcessing user {i}/{total_users}: {username}")
        try:
            crawler = BOJCrawler(username, target_month)
            problems = crawler.get_solved_problems()
            
            if problems:
                print(f"Found {len(problems)} problems for user {username}")
                crawler.save_to_json(problems)
            else:
                print(f"No problems found for user {username}")
                
            # Add a small delay between users to be respectful to the server
            if i < total_users:
                print("Waiting 5 seconds before next user...")
                time.sleep(5)
                
        except Exception as e:
            print(f"Error processing user {username}: {str(e)}")
            continue

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