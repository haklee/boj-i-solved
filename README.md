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
- Optional date filtering to get solutions from a specific month
- Batch crawling support for multiple users

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

### Command Line Interface

#### Single User Crawling

```bash
# Get all solved problems
boj-crawler -u username

# Get problems solved in January 2024
boj-crawler -u username -d 202401
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
boj-batch-crawler -f usernames.txt -d 202401
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
- When using the -d option, the date must be in YYYYMM format (e.g., 202401 for January 2024)
- The batch crawler adds a 5-second delay between users to be respectful to the server

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
