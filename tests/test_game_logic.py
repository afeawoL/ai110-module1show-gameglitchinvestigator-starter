"""
Regression tests for the bugs fixed in logic_utils.py.

Each test names the specific defect it guards against, so a reintroduced bug
points straight at the behaviour that regressed.
"""

import pytest

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


# ---------------------------------------------------------------------------
# check_guess -- the flipped hints, and the lexicographic string fallback
# ---------------------------------------------------------------------------

def test_winning_guess():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


def test_guess_too_high():
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


def test_too_high_tells_player_to_go_lower():
    """BUG: both hint messages were flipped -- "Too High" said "Go HIGHER!"."""
    _, message = check_guess(60, 50)
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_too_low_tells_player_to_go_higher():
    """BUG: the counterpart flip -- "Too Low" said "Go LOWER!"."""
    _, message = check_guess(40, 50)
    assert "HIGHER" in message
    assert "LOWER" not in message


def test_hint_direction_holds_just_below_and_above_the_secret():
    assert check_guess(51, 50)[0] == "Too High"
    assert check_guess(49, 50)[0] == "Too Low"


def test_no_lexicographic_string_fallback():
    """
    BUG: a TypeError fallback compared guesses as STRINGS, so 9 vs a secret of
    50 came back "Too High" because "9" > "50". The fallback is gone, so a
    str secret must now raise rather than silently return a wrong answer.
    """
    with pytest.raises(TypeError):
        check_guess(9, "50")


def test_single_digit_guess_against_two_digit_secret_is_too_low():
    """The numeric comparison the string fallback used to get backwards."""
    assert check_guess(9, 50)[0] == "Too Low"


# ---------------------------------------------------------------------------
# get_range_for_difficulty -- inverted difficulty ranges
# ---------------------------------------------------------------------------

def test_range_grows_with_difficulty():
    """BUG: Hard was 1-100 wide at most and SMALLER than Normal, so "Hard" was
    the easier setting. A harder difficulty must span more numbers."""
    easy_low, easy_high = get_range_for_difficulty("Easy")
    normal_low, normal_high = get_range_for_difficulty("Normal")
    hard_low, hard_high = get_range_for_difficulty("Hard")

    easy_span = easy_high - easy_low
    normal_span = normal_high - normal_low
    hard_span = hard_high - hard_low

    assert easy_span < normal_span < hard_span


def test_unknown_difficulty_falls_back_to_normal():
    assert get_range_for_difficulty("Nightmare") == get_range_for_difficulty("Normal")


# ---------------------------------------------------------------------------
# parse_guess -- silent truncation and the missing range check
# ---------------------------------------------------------------------------

def test_decimal_input_is_rejected_not_truncated():
    """BUG: "3.9" was silently truncated to 3, so the number evaluated was not
    the number the player typed."""
    ok, value, err = parse_guess("3.9", 1, 100)
    assert ok is False
    assert value is None
    assert err


def test_out_of_range_guess_is_rejected():
    """BUG: parse_guess never range-checked, so 999 was accepted on Easy (1-20)."""
    ok, value, err = parse_guess("999", 1, 20)
    assert ok is False
    assert value is None
    assert "between 1 and 20" in err


@pytest.mark.parametrize("raw", ["1", "20"])
def test_range_boundaries_are_inclusive(raw):
    ok, value, err = parse_guess(raw, 1, 20)
    assert ok is True
    assert value == int(raw)
    assert err is None


def test_valid_guess_is_parsed():
    assert parse_guess("42", 1, 100) == (True, 42, None)


def test_surrounding_whitespace_is_tolerated():
    assert parse_guess("  42  ", 1, 100) == (True, 42, None)


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_blank_input_asks_for_a_guess(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_non_numeric_input_is_rejected():
    ok, value, err = parse_guess("abc", 1, 100)
    assert ok is False
    assert value is None
    assert err


def test_bounds_are_optional():
    """Called without low/high, parse_guess still parses but skips the range check."""
    assert parse_guess("999") == (True, 999, None)


# ---------------------------------------------------------------------------
# update_score -- the off-by-one win bonus and the parity reward
# ---------------------------------------------------------------------------

def test_winning_on_the_first_guess_scores_full_points():
    """BUG: attempt_number was already incremented, and (attempt_number + 1)
    subtracted a second time, so a first-guess win scored 80 instead of 100."""
    assert update_score(0, "Win", 1) == 100


def test_win_bonus_decays_by_ten_per_attempt():
    assert update_score(0, "Win", 2) == 90
    assert update_score(0, "Win", 3) == 80


def test_win_bonus_never_drops_below_ten():
    assert update_score(0, "Win", 50) == 10


def test_wrong_guess_is_never_rewarded_on_even_attempts():
    """BUG: a "Too High" guess ADDED 5 points whenever the attempt number was
    even, so guessing wrong could raise the score."""
    assert update_score(0, "Too High", 2) == -5
    assert update_score(0, "Too High", 4) == -5


def test_both_wrong_outcomes_are_penalised_identically():
    """BUG: "Too High" was scored by parity while "Too Low" was always -5."""
    for attempt in range(1, 7):
        assert update_score(0, "Too High", attempt) == update_score(0, "Too Low", attempt)


def test_score_accumulates_from_the_current_score():
    assert update_score(30, "Too Low", 3) == 25


def test_unknown_outcome_leaves_score_untouched():
    assert update_score(42, "Sideways", 3) == 42
