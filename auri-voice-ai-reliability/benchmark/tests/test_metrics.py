from benchmark.generate_suite import build_suite
from benchmark.metrics import percentile, word_error_rate


def test_suite_has_240_scenarios_and_three_noise_profiles():
    suite = build_suite()
    assert len(suite) == 240
    assert all(len(row["noise_profiles"]) == 3 for row in suite)
    assert sum(len(row["noise_profiles"]) for row in suite) == 720


def test_word_error_rate_exact_match():
    assert word_error_rate("hello world", "hello world") == 0


def test_word_error_rate_single_substitution():
    assert word_error_rate("hello world", "hello there") == 0.5


def test_percentile():
    assert percentile([10, 20, 30, 40], 0.5) == 25
