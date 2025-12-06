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
    # Prefer importing the library API, but some snscrape releases are
    # incompatible with newer Python import machinery (see AttributeError
    # from importlib). If import fails, try calling the `snscrape` CLI
    # and parsing JSON lines as a robust fallback.
    try:
        import snscrape.modules.twitter as sntwitter  # type: ignore

        tweets: List[str] = []
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break
            tweets.append(tweet.content)
        return tweets
    except Exception as e_import:
        # attempt CLI fallback
        import json
        import shlex
        import subprocess

        try:
            cmd = f"snscrape --jsonl twitter-search {shlex.quote(query)} --max-results {int(limit)}"
            proc = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out = proc.stdout
            results: List[str] = []
            for line in out.splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    # snscrape JSON structure contains 'content' for tweet text
                    txt = obj.get("content") or obj.get("rawContent") or ""
                    if txt:
                        results.append(txt)
                except Exception:
                    # skip lines that fail to parse
                    continue
            return results[:limit]
        except FileNotFoundError:
            raise RuntimeError("snscrape is not installed (no importable module and no `snscrape` CLI)") from e_import
        except subprocess.CalledProcessError as e_sub:
            # Last-resort: if snscrape is broken on this Python version, try using
            # the Twitter API via tweepy if a BEARER_TOKEN is available in env.
            # This covers environments (like Python 3.13) where snscrape's
            # import machinery is incompatible.
            import os

            bearer = os.environ.get("BEARER_TOKEN") or os.environ.get("TWITTER_BEARER_TOKEN")
            if bearer:
                try:
                    import tweepy

                    client = tweepy.Client(bearer)
                    tweets: List[str] = []
                    # Tweepy `search_recent_tweets` returns up to 100 per request.
                    remaining = int(limit)
                    max_page = 100 if remaining > 100 else remaining
                    resp = client.search_recent_tweets(query=query, max_results=max_page)
                    if resp and resp.data:
                        for t in resp.data:
                            tweets.append(t.text)
                    return tweets[:limit]
                except Exception:
                    # fall through to raise the original snscrape CLI error below
                    pass

            raise RuntimeError(f"snscrape CLI failed: {e_sub.stderr.strip()}") from e_sub
