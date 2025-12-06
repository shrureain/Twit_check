"""Command-line helpers: scrape to CSV and an interactive chatbot over a CSV dataset.
"""
from typing import List
import argparse
import pandas as pd

from .fetcher import fetch_from_snscrape
from .chatbot import SimpleChatbot


def scrape_to_csv(query: str, limit: int, out: str, preview: bool = False) -> None:
    texts: List[str] = fetch_from_snscrape(query, limit=limit)
    df = pd.DataFrame({"text": texts})
    df["scraped_at"] = pd.Timestamp.utcnow().isoformat()
    df.to_csv(out, index=False)
    if preview:
        print(f"Saved {len(df)} tweets to {out}")
        print(df.head(10).to_string(index=False))


def chat_from_csv(path: str):
    df = pd.read_csv(path)
    if "text" not in df.columns:
        raise ValueError("CSV must contain a 'text' column")
    texts = df["text"].astype(str).tolist()
    bot = SimpleChatbot(texts)
    print("Loaded dataset with", len(texts), "items. Enter queries (empty line to quit).")
    while True:
        q = input("you> ").strip()
        if not q:
            break
        results = bot.respond(q, top_k=5)
        if not results:
            print("bot> No good matches found.")
            continue
        for i, (text, score, sentiment) in enumerate(results, 1):
            print(f"bot[{i}]> score={score:.3f} sentiment={sentiment['label']}\n{text}\n")


def main(argv=None):
    p = argparse.ArgumentParser(description="twit_check helper CLI")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("scrape", help="Scrape tweets using snscrape and save to CSV")
    s.add_argument("--query", "-q", required=True)
    s.add_argument("--limit", "-n", type=int, default=200)
    s.add_argument("--out", "-o", default="scraped_tweets.csv")
    s.add_argument("--preview", action="store_true")

    c = sub.add_parser("chat", help="Start an interactive retrieval chatbot on a CSV file")
    c.add_argument("--csv", required=True)

    args = p.parse_args(argv)
    if args.cmd == "scrape":
        scrape_to_csv(args.query, args.limit, args.out, preview=args.preview)
    elif args.cmd == "chat":
        chat_from_csv(args.csv)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
