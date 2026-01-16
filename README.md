## Daily News Email Digest
## Project Overview

Daily News Email Digest is a Python-based automation project that collects the latest news articles from trusted online sources and delivers them directly to the user’s email inbox in a clean, readable format.

The project scrapes news from sources such as Firstpost and Brut Media, stores the articles in a local SQLite database, and sends a daily email digest containing headlines and summaries. This eliminates the need to visit multiple websites manually.

## Features

 Web scraping from reliable news sources

 SQLite database storage for fetched articles

 Automated daily email delivery

 Duplicate article detection to avoid repeated news

 Supports scheduled execution using Cron or Task Scheduler

 Technology Stack

Programming Language: Python

Web Scraping: Requests, BeautifulSoup

Database: SQLite

Email Service: SMTP (smtplib, email libraries)


## Automation

The script can be scheduled to run daily using:

Cron jobs (Linux/macOS)

Task Scheduler (Windows)

## Learning Outcomes

Practical experience with web scraping

Database handling using SQLite

Email automation using Python

Building end-to-end automation workflows

## Future Enhancements

Add more news sources

Category-based news filtering

Improved HTML email formatting

Cloud deployment support
