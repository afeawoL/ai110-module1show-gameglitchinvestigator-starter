# FIX: Refactored out of app.py into logic_utils.py using agent mode.
def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    # FIX: Inverted difficulty. Hard was 1-50, a SMALLER range than Normal's
    # 1-100, which made "Hard" the easiest setting. Widened to 1-200 so the
    # range now grows with difficulty.
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


# FIX: Refactored out of app.py into logic_utils.py using agent mode.
# FIX: Gained optional low/high parameters so the guess can be range-checked.
def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess.

    If low/high are given, the guess must fall inside that inclusive range.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    # FIX: Strip whitespace so " 42 " is not rejected as a non-number.
    raw = raw.strip()

    if raw == "":
        return False, None, "Enter a guess."

    try:
        # FIX: Silent truncation. "3.9" was run through int(float(raw)) and
        # became 3, so the number evaluated was not the number the player
        # typed. Decimals are now rejected outright.
        value = int(raw)
    # FIX: Was a bare `except Exception`, which would also swallow unrelated
    # errors. Narrowed to the ValueError that int() actually raises.
    except ValueError:
        return False, None, "That is not a whole number."

    # FIX: Missing range check. 999 used to be accepted as a valid guess even
    # on Easy (1-20).
    if low is not None and high is not None:
        if value < low or value > high:
            return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


# FIX: Refactored out of app.py into logic_utils.py using agent mode.
def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: Deleted a TypeError fallback that compared guesses as STRINGS, so
    # "9" > "50" reported guessing 9 against a secret of 50 as "Too High". It
    # only existed to swallow the str() cast in app.py, which is also gone.
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: The flipped hints. Both branches used to tell the player the exact
    # opposite of what to do -- "Too High" said "Go HIGHER!" and "Too Low" said
    # "Go LOWER!". A guess above the secret now correctly says LOWER.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"

    return "Too Low", "📈 Go HIGHER!"


# FIX: Refactored out of app.py into logic_utils.py using agent mode.
def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        # FIX: Off by one. attempt_number is already incremented by the caller,
        # and the old (attempt_number + 1) subtracted a second time, so winning
        # on the very first guess scored 80 instead of 100.
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: Parity reward. "Too High" used to ADD 5 points whenever the attempt
    # number was even, while "Too Low" was always -5. Guessing wrong could
    # raise your score. Both wrong outcomes are now penalised identically.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
