import argparse
from datetime import datetime
from .crawler import BOJCrawler

def main():
    parser = argparse.ArgumentParser(description='Crawl BOJ solved problems for a user')
    parser.add_argument('-u', '--username', required=True, help='BOJ username to crawl')
    parser.add_argument('-d', '--date', help='Filter by submission month in YYYYMM format (e.g., 202401)')
    args = parser.parse_args()
    
    # Validate date format if provided
    if args.date:
        try:
            datetime.strptime(args.date, "%Y%m")
        except ValueError:
            print("Error: Date must be in YYYYMM format (e.g., 202401)")
            return
    
    user_id = args.username
    crawler = BOJCrawler(user_id, args.date)
    
    crawler.log_info(f"Starting crawler for user: {user_id}" + (f" (filtering by month: {args.date})" if args.date else ""))
    problems = crawler.get_solved_problems()
    
    if problems:
        crawler.log_info(f"Total problems found: {len(problems)}")
        crawler.save_to_json(problems)
    else:
        crawler.log_error("No problems found or an error occurred")

if __name__ == "__main__":
    main() 