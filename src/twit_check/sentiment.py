from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


_analyzer = SentimentIntensityAnalyzer()


def classify(text: str) -> dict:
    """Return label and scores for given text.

    Output shape: { 'label': 'positive'|'negative'|'neutral', 'scores': {..} }
    """
    scores = _analyzer.polarity_scores(text)
    comp = scores.get("compound", 0.0)
    if comp >= 0.05:
        label = "positive"
    elif comp <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return {"label": label, "scores": scores}
