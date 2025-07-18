# BOJ Solved Problems Crawler

A Python package to crawl solved problems from Baekjoon Online Judge (BOJ) for one or multiple users.

## Features

- Crawls the BOJ status page for a given user
- Extracts information about solved problems including:
    - Submission ID
    - Problem ID
    - Problem Title (from title attribute)
    - Programming Language
    - Submission Time (from title attribute)
- Saves the results to a JSON file in a user-specific folder
- Includes rate limiting (2 seconds between requests) to prevent server overload
- Optional date filtering to get solutions from a specific month or date range
- Batch crawling support for multiple users
- **Proxy server support** for HTTP, HTTPS, and SOCKS proxies
- Retry logic for handling 403 Forbidden errors
- Monthly reporting and statistics generation

## Installation

### From PyPI

```bash
pip install boj-crawler
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/boj-crawler.git
cd boj-crawler
```

2. Install the package:
```bash
pip install -e .
```

### For SOCKS Proxy Support

If you need SOCKS proxy support, install the additional dependency:
```bash
pip install requests[socks]
```

## Usage

### As a Package

You can use the crawler in your Python code:

```python
from boj_crawler import BOJCrawler

# Create a crawler instance
crawler = BOJCrawler("username")

# Get solved problems
problems = crawler.get_solved_problems()

# Save to JSON
crawler.save_to_json(problems)
```

#### Using Proxy in Python Code

```python
from boj_crawler import BOJCrawler

# Using a single proxy for both HTTP and HTTPS
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080'
}

crawler = BOJCrawler("username", proxies=proxies)
problems = crawler.get_solved_problems()
crawler.save_to_json(problems)

# Using different proxies for HTTP and HTTPS
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://secure-proxy.example.com:8443'
}

crawler = BOJCrawler("username", proxies=proxies)

# With date filtering and proxy
crawler = BOJCrawler("username", start_date="240101", end_date="240331", proxies=proxies)
```

### Command Line Interface

#### Single User Crawling

```bash
# Get all solved problems
boj-crawler -u username

# Get problems solved in January 2024
boj-crawler -u username -m 202401

# Get problems in a date range
boj-crawler -u username -s 240315 -e 240415

# Using proxy servers
boj-crawler -u username --proxy-all http://proxy.example.com:8080
boj-crawler -u username --proxy-http http://proxy.example.com:8080 --proxy-https https://secure-proxy.example.com:8443

# Combine proxy with date filtering
boj-crawler -u username --proxy-all http://proxy.example.com:8080 -s 240101 -e 240331
```

#### Batch Crawling

1. Create a text file with usernames (one per line), for example `usernames.txt`:
```
user1
user2
user3
```

2. Run the batch crawler:
```bash
# Get all solved problems for all users
boj-batch-crawler -f usernames.txt

# Get problems solved in January 2024 for all users
boj-batch-crawler -f usernames.txt -m 202401

# Get problems in a date range for all users
boj-batch-crawler -f usernames.txt -s 240315 -e 240415

# Using proxy with batch crawling
boj-batch-crawler -f usernames.txt --proxy-all http://proxy.example.com:8080

# Combine proxy with filtering and disable reports
boj-batch-crawler -f usernames.txt --proxy-all http://proxy.example.com:8080 -m 202401 --no-report
```

### Proxy Configuration

#### Supported Proxy Types

- **HTTP proxies**: `http://proxy.example.com:8080`
- **HTTPS proxies**: `https://proxy.example.com:8080`
- **SOCKS proxies**: `socks5://proxy.example.com:1080` (requires `requests[socks]`)
- **Authenticated proxies**: `http://username:password@proxy.example.com:8080`

#### Command Line Proxy Options

- `--proxy-all URL`: Use the same proxy for both HTTP and HTTPS
- `--proxy-http URL`: Use proxy only for HTTP requests
- `--proxy-https URL`: Use proxy only for HTTPS requests

#### Common Proxy Examples

```bash
# Local debugging proxy (Charles, Fiddler, etc.)
boj-crawler -u username --proxy-all http://localhost:8888

# Corporate proxy with authentication
boj-crawler -u username --proxy-all http://user:pass@proxy.company.com:8080

# SOCKS5 proxy
boj-crawler -u username --proxy-all socks5://proxy.example.com:1080

# Different proxies for HTTP and HTTPS
boj-crawler -u username --proxy-http http://proxy1.example.com:8080 --proxy-https https://proxy2.example.com:8443
```

## Output

The script creates a folder named after each user and generates a JSON file (`solved_problems.json`) inside that folder. The JSON file contains an array of solved problems with the following structure:

```json
[
  {
    "submission_id": "...",
    "problem_id": "...",
    "problem_title": "...",
    "language": "...",
    "submission_time": "..."
  },
  ...
]
```

## Notes

- The script uses a 2-second delay between requests to be respectful to the BOJ servers
- Problem titles and submission times are extracted from the title attributes of the respective elements
- The script handles pagination automatically to collect all solved problems
- Each user's data is stored in a separate folder to keep the data organized
- When using date filtering:
  - `-m/--month`: Date must be in YYYYMM format (e.g., 202401 for January 2024)
  - `-s/--start-date` and `-e/--end-date`: Dates must be in YYMMDD format (e.g., 240315 for March 15, 2024)
- The batch crawler adds a 5-second delay between users to be respectful to the server
- Proxy settings are applied to all HTTP requests made by the crawler
- The crawler includes retry logic for 403 Forbidden errors with configurable delays

## Development

### Project Structure

```
boj-crawler/
├── boj_crawler/
│   ├── __init__.py
│   ├── crawler.py
│   ├── cli.py
│   └── batch.py
├── setup.py
├── README.md
└── requirements.txt
```

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
