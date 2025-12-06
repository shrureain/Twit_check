from twit_check.sentiment import classify


def test_positive():
    r = classify("I love this product, it's fantastic!")
    assert r['label'] == 'positive'


def test_negative():
    r = classify("This is the worst experience ever. I hate it.")
    assert r['label'] == 'negative'
