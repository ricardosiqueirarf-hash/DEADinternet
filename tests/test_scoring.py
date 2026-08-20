from app.scoring import calculate_score


def test_score_is_bounded():
    assert calculate_score(views=10**12, likes=10**12, comments=10**12, hook_strength=99, recreation_ease=99, monetization_potential=99) == 100


def test_score_accepts_empty_metrics():
    assert calculate_score() == 0


def test_better_reference_scores_higher():
    low = calculate_score(views=100, likes=1, comments=0, hook_strength=2, recreation_ease=2, monetization_potential=2)
    high = calculate_score(views=100000, likes=8000, comments=1000, hook_strength=9, recreation_ease=8, monetization_potential=9)
    assert high > low
