# Twit_check

A minimal Python project that provides a tiny agent for fetching tweets (CSV or snscrape fallback)
and running a basic sentiment classifier using VADER. This scaffold is intentionally simple so it can
run without Twitter API keys (use a CSV of tweets as fallback).

Quick start
1. Create and activate a Python virtualenv (recommended).
2. Install dependencies:

	pip install -r requirements.txt

3. Run the CLI on a CSV file (expects a `text` column):

	python -m twit_check --csv tweets.csv

4. Run tests:

	pytest -q

What's included
- `src/twit_check/fetcher.py` — tweet fetcher (snscrape optional, CSV fallback)
- `src/twit_check/sentiment.py` — VADER-based sentiment classifier
- `src/twit_check/__main__.py` — small CLI
- `tests/test_sentiment.py` — minimal unit tests

Notes
- If you want live scraping without CSV, install `snscrape` and call the `fetch_from_snscrape` function.
- This is a scaffold to get started; extend it with streaming, batching, or a model server as needed.
