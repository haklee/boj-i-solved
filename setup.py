from setuptools import setup, find_packages

setup(
    name="boj-crawler",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "html5lib>=1.1",
    ],
    entry_points={
        "console_scripts": [
            "boj-crawler=boj_crawler.cli:main",
            "boj-batch-crawler=boj_crawler.batch:main",
        ],
    },
    author="Hak Lee",
    author_email="haklee@haklee.com",
    description="A package to crawl solved problems from Baekjoon Online Judge",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/haklee/boj-crawler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
