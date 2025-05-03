# BOJ Solved Problems Crawler

This Python script crawls the Baekjoon Online Judge (BOJ) status page to collect information about solved problems for a specific user.

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

## Requirements

- Python 3.6+
- Required packages (install using `pip install -r requirements.txt`):
    - requests
    - beautifulsoup4
    - html5lib

## Usage

### Single User Crawling

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the script with a BOJ username using the -u option:

```bash
python boj_crawler.py -u <username> [-d YYYYMM]
```

For example:
```bash
# Get all solved problems
python boj_crawler.py -u hakleealgo

# Get problems solved in January 2024
python boj_crawler.py -u hakleealgo -d 202401
```

### Batch Crawling

1. Create a text file with usernames (one per line), for example `usernames.txt`:
```
hakleealgo
user2
user3
```

2. Run the batch crawler:

```bash
python batch_crawler.py -f usernames.txt [-d YYYYMM]
```

For example:
```bash
# Get all solved problems for all users
python batch_crawler.py -f usernames.txt

# Get problems solved in January 2024 for all users
python batch_crawler.py -f usernames.txt -d 202401
```

The script will crawl the status page for each user and save the results to `<username>/solved_problems.json`.

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
