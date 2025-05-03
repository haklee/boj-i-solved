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

## Requirements

- Python 3.6+
- Required packages (install using `pip install -r requirements.txt`):
    - requests
    - beautifulsoup4
    - html5lib

## Usage

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the script with a BOJ username:

```bash
python boj_crawler.py <username>
```

For example:
```bash
python boj_crawler.py hakleealgo
```

The script will crawl the status page for the specified user and save the results to `<username>/solved_problems.json`.

## Customization

To crawl a different user's solved problems, modify the `user_id` variable in the `main()` function of `boj_crawler.py`.

## Output

The script creates a folder named after the user and generates a JSON file (`solved_problems.json`) inside that folder. The JSON file contains an array of solved problems with the following structure:

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
