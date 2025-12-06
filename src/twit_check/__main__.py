"""Simple CLI entrypoint for the twit_check package.
"""
import argparse
from .fetcher import fetch_from_csv, fetch_from_snscrape
from .sentiment import classify


def main():
    p = argparse.ArgumentParser(description="Basic Twit sentiment CLI")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv", help="Path to tweets CSV file (must have text column)")
    group.add_argument("--text", help="Single text to classify")
    group.add_argument("--scrape", help="snscrape query (requires snscrape)")
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()

    if args.csv:
        texts = fetch_from_csv(args.csv)
    elif args.text:
        texts = [args.text]
    else:
        texts = fetch_from_snscrape(args.scrape, limit=args.limit)

    for t in texts:
        r = classify(t)
        print(f"{r['label']}\t{r['scores']['compound']:.3f}\t{t}")


if __name__ == '__main__':
    main()
