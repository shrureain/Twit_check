"""Streaming helpers: snscrape poll fallback and optional Tweepy streaming.

This module provides two public helpers:
- poll_with_snscrape(query, on_tweet, limit=None, interval=5)
- stream_with_tweepy(bearer_token, rule, on_tweet, limit=None, timeout=None)

Both call `on_tweet(text: str)` for each new tweet.
"""
from typing import Callable, Optional
import time


def poll_with_snscrape(query: str, on_tweet: Callable[[str], None], limit: Optional[int] = None, interval: int = 5):
    """Poll snscrape for query and call on_tweet for each new item.

    This is a polling fallback when the Twitter API isn't available.
    """
    try:
        import snscrape.modules.twitter as sntwitter
    except Exception as e:
        raise RuntimeError("snscrape is not installed") from e

    seen = set()
    count = 0
    while True:
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            # try a stable id
            tid = getattr(tweet, "id", None) or getattr(tweet, "url", None) or getattr(tweet, "date", None)
            if tid in seen:
                continue
            seen.add(tid)
            on_tweet(tweet.content)
            count += 1
            if limit and count >= limit:
                return
        time.sleep(interval)


def stream_with_tweepy(bearer_token: str, rule: str, on_tweet: Callable[[str], None], limit: Optional[int] = None, timeout: Optional[int] = None):
    """Stream tweets using Tweepy StreamingClient and call on_tweet for each tweet.

    Requires `tweepy` and a valid bearer token.
    """
    try:
        import tweepy
    except Exception as e:
        raise RuntimeError("tweepy is not installed") from e

    class _Streamer(tweepy.StreamingClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.count = 0

        def on_tweet(self, tweet):
            text = getattr(tweet, "text", None) or (tweet.data and tweet.data.get("text"))
            if text is None:
                return
            on_tweet(str(text))
            self.count += 1
            if limit and self.count >= limit:
                try:
                    self.disconnect()
                except Exception:
                    pass

        def on_connection_error(self):
            # simple surface of connection issues
            print("Connection error in tweepy stream")

    client = _Streamer(bearer_token)

    # Remove existing rules if present, then add our rule
    try:
        existing = client.get_rules().data or []
        if existing:
            ids = [r.id for r in existing]
            client.delete_rules(ids)
    except Exception:
        pass

    client.add_rules(tweepy.StreamRule(rule))
    # blocks until timeout or disconnect
    client.filter(timeout=timeout)
