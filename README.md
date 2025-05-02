# BOJ Solved Problems Crawler

This Python script crawls the Baekjoon Online Judge (BOJ) status page to collect information about solved problems for a specific user.

## Features

- Crawls the BOJ status page for a given user
- Extracts information about solved problems including:
    - Submission ID
    - Problem ID
    - Problem Title
    - Programming Language
    - Submission Time
- Saves the results to a JSON file

## Requirements

- Python 3.6+
- Required packages (install using `pip install -r requirements.txt`):
    - requests
    - beautifulsoup4
    - lxml

## Usage

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the script:

```bash
python boj_crawler.py
```

The script will crawl the status page for the user "hakleealgo" and save the results to `solved_problems.json`.

## Customization

To crawl a different user's solved problems, modify the `user_id` variable in the `main()` function of `boj_crawler.py`.

## Output

The script generates a JSON file (`solved_problems.json`) containing an array of solved problems with the following structure:

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
