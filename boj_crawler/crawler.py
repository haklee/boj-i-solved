import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict, Optional
from urllib.parse import urljoin
from datetime import datetime

class BOJCrawler:
    def __init__(self, user_id: str, start_date: str = None, end_date: str = None, target_month: str = None, proxies: Dict[str, str] = None):
        self.user_id = user_id
        self.base_url = "https://www.acmicpc.net"
        self.status_url = f"{self.base_url}/status?user_id={user_id}&result_id=4"  # result_id=4 for accepted solutions
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.delay = 2  # seconds between requests
        self.max_retries = 3  # maximum number of retries for 403 errors
        self.retry_delay = 2  # seconds between retries
        self.proxies = proxies  # Proxy configuration
        
        # Support both new date range filtering and legacy month filtering
        self.start_date = start_date
        self.end_date = end_date
        self.target_month = target_month
        
        # Convert yymmdd dates to datetime objects for comparison
        self.start_datetime = self._parse_yymmdd_date(start_date) if start_date else None
        self.end_datetime = self._parse_yymmdd_date(end_date) if end_date else None
        
    def _parse_yymmdd_date(self, date_str: str) -> Optional[datetime]:
        """Parse yymmdd format date string to datetime object"""
        if not date_str or len(date_str) != 6:
            return None
        try:
            # Convert 2-digit year to 4-digit year (assume 2000s)
            year = 2000 + int(date_str[:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            return datetime(year, month, day)
        except ValueError:
            return None

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

    def log_warning(self, message: str):
        """Log warning messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] WARNING: {message}")

    def _make_request_with_retry(self, url: str) -> requests.Response:
        """Make HTTP request with retry logic for 403 errors"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):  # 0-indexed, so max_retries + 1 total attempts
            try:
                response = requests.get(url, headers=self.headers, proxies=self.proxies)
                
                # Check for 403 Forbidden error
                if response.status_code == 403:
                    if attempt < self.max_retries:
                        self.log_warning(f"403 Forbidden error on attempt {attempt + 1}/{self.max_retries + 1}. Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        # Last attempt failed, raise the exception
                        response.raise_for_status()
                
                # If we get here, the request was successful or had a non-403 error
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                
                # Only retry on 403 errors, not other request exceptions
                if hasattr(e, 'response') and e.response and e.response.status_code == 403:
                    if attempt < self.max_retries:
                        self.log_warning(f"403 Forbidden error on attempt {attempt + 1}/{self.max_retries + 1}. Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        continue
                
                # For non-403 errors, raise immediately
                raise e
        
        # If we get here, all retries failed
        raise last_exception

    def is_in_date_range(self, submission_time: str) -> bool:
        """Check if the submission time is within the specified date range"""
        try:
            # Convert submission_time to datetime
            dt = datetime.strptime(submission_time, "%Y-%m-%d %H:%M:%S")
            submission_date = dt.date()
            
            # Check start date filter
            if self.start_datetime and submission_date < self.start_datetime.date():
                return False
                
            # Check end date filter
            if self.end_datetime and submission_date > self.end_datetime.date():
                return False
                
            return True
        except ValueError:
            return False

    def is_target_month(self, submission_time: str) -> bool:
        """Check if the submission time matches the target month (legacy support)"""
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

    def is_before_date_range(self, submission_time: str) -> bool:
        """Check if the submission time is before the specified date range"""
        try:
            dt = datetime.strptime(submission_time, "%Y-%m-%d %H:%M:%S")
            submission_date = dt.date()
            
            # If start date is specified and submission is before start date, stop crawling
            if self.start_datetime and submission_date < self.start_datetime.date():
                return True
                
            # Legacy support: check if before target month
            if self.target_month:
                submission_month = dt.strftime("%Y%m")
                return submission_month < self.target_month
                
            return False
        except ValueError:
            return False

    def should_include_submission(self, submission_time: str) -> bool:
        """Determine if a submission should be included based on all filters"""
        # If using new date range filtering
        if self.start_date or self.end_date:
            return self.is_in_date_range(submission_time)
        
        # Fall back to legacy month filtering
        return self.is_target_month(submission_time)

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
                response = self._make_request_with_retry(current_url)
                
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
                            
                            # Check if we should stop crawling (found submission before date range)
                            if self.is_before_date_range(submission_time):
                                self.log_info("Found submission before date range, stopping crawl")
                                stop_crawling = True
                                break
                                
                            # Check if submission should be included
                            if not self.should_include_submission(submission_time):
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