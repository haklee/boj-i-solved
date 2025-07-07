import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict
from urllib.parse import urljoin
from datetime import datetime

class BOJCrawler:
    def __init__(self, user_id: str, target_month: str = None):
        self.user_id = user_id
        self.base_url = "https://www.acmicpc.net"
        self.status_url = f"{self.base_url}/status?user_id={user_id}&result_id=4"  # result_id=4 for accepted solutions
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.delay = 2  # seconds between requests
        self.target_month = target_month

    def log_error(self, message: str, error: Exception = None):
        """Log error messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{timestamp}] ERROR: {message}"
        if error:
            error_message += f"\nError details: {str(error)}"
        print(error_message)

    def log_info(self, message: str):
        """Log info messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] INFO: {message}")

    def is_target_month(self, submission_time: str) -> bool:
        """Check if the submission time matches the target month"""
        if not self.target_month:
            return True
        try:
            # Convert submission_time to datetime
            dt = datetime.strptime(submission_time, "%Y-%m-%d %H:%M:%S")
            # Format as yyyymm
            submission_month = dt.strftime("%Y%m")
            return submission_month == self.target_month
        except ValueError:
            return False

    def is_before_target_month(self, submission_time: str) -> bool:
        """Check if the submission time is before the target month"""
        if not self.target_month:
            return False
        try:
            # Convert submission_time to datetime
            dt = datetime.strptime(submission_time, "%Y-%m-%d %H:%M:%S")
            # Format as yyyymm
            submission_month = dt.strftime("%Y%m")
            return submission_month < self.target_month
        except ValueError:
            return False

    def get_solved_problems(self) -> List[Dict]:
        """
        Crawl the status page and return a list of solved problems
        """
        all_problems = []
        current_url = self.status_url
        stop_crawling = False
        
        while current_url and not stop_crawling:
            try:
                self.log_info(f"Crawling page: {current_url}")
                response = requests.get(current_url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html5lib")
                problems = []
                
                # Find the table containing the submissions
                table = soup.find("table", {"id": "status-table"})
                if not table:
                    self.log_error("Status table not found on the page")
                    break
                
                # Get all rows except the header
                rows = table.find_all("tr")[1:]
                
                for row in rows:
                    try:
                        cols = row.find_all("td")
                        if len(cols) >= 6:
                            submission_time = cols[8].find("a").get("title", "").strip()
                            
                            # If we find a submission before target month, stop crawling
                            if self.is_before_target_month(submission_time):
                                self.log_info("Found submission before target month, stopping crawl")
                                stop_crawling = True
                                break
                                
                            if not self.is_target_month(submission_time):
                                continue
                                
                            problem = {
                                "submission_id": cols[0].text.strip(),
                                "problem_id": cols[2].text.strip(),
                                "problem_title": cols[2].find("a").get("title", "").strip(),
                                "language": cols[6].text.strip(),
                                "submission_time": submission_time,
                            }
                            problems.append(problem)
                    except Exception as e:
                        self.log_error("Error parsing problem row", e)
                
                all_problems.extend(problems)
                self.log_info(f"Found {len(problems)} problems on current page")
                
                if stop_crawling:
                    break
                
                # Find the next page link
                next_page = soup.find("a", {"id": "next_page"})
                if next_page and "href" in next_page.attrs:
                    current_url = urljoin(self.base_url, next_page["href"])
                    self.log_info(f"Found next page: {current_url}")
                    self.log_info(f"Waiting {self.delay} seconds before next request...")
                    time.sleep(self.delay)
                else:
                    self.log_info("No more pages to crawl")
                    current_url = None
                
            except requests.exceptions.RequestException as e:
                self.log_error(f"Request failed for URL: {current_url}", e)
                break
            except Exception as e:
                self.log_error("Unexpected error occurred", e)
                break
        
        return all_problems

    def save_to_json(self, problems: List[Dict], filename: str = "solved_problems.json"):
        """
        Save the solved problems to a JSON file in a folder named after the user
        """
        try:
            import os
            # Create directory if it doesn't exist
            user_dir = os.path.join(os.getcwd(), self.user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            # Save file in the user's directory
            filepath = os.path.join(user_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(problems, f, ensure_ascii=False, indent=2)
            self.log_info(f"Successfully saved {len(problems)} problems to {filepath}")
        except Exception as e:
            self.log_error(f"Failed to save problems to {filename}", e) 