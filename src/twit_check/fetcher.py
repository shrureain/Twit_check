from typing import List
import pandas as pd


def fetch_from_csv(path: str, text_col: str = "text") -> List[str]:
    """Read tweets from a CSV file and return a list of texts.

    CSV must contain a column named `text` by default.
    """
    df = pd.read_csv(path)
    if text_col not in df.columns:
        raise ValueError(f"CSV must contain a '{text_col}' column")
    return df[text_col].astype(str).tolist()


def fetch_from_snscrape(query: str, limit: int = 100) -> List[str]:
    """Fetch tweets using snscrape. Raises RuntimeError if snscrape isn't installed.

    This is an optional helper — the CSV loader is the supported fallback.
    """
    try:
        import snscrape.modules.twitter as sntwitter
    except Exception as e:
        raise RuntimeError("snscrape is not installed or not importable") from e

    tweets: List[str] = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit:
            break
        tweets.append(tweet.content)
    return tweets
