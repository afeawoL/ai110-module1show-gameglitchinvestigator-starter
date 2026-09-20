import random
import streamlit as st

# FIX: Refactored the four pure game functions into logic_utils.py using agent
# mode, so app.py is now only the Streamlit UI and the submit handler.
from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

# FIX: Inverted attempt limits. Easy used to get 6 guesses while Normal got 8,
# making "Easy" the stingiest setting. More attempts means an easier game, so
# the limits no longer increase with difficulty.
attempt_limit_map = {
    "Easy": 10,
    "Normal": 8,
    "Hard": 8,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")


# FIX: Round state was reset ad hoc in three different places and never
# completely. One helper now owns it, so every reset is identical.
def start_new_round():
    """Reset every piece of round state, using the current difficulty's range."""
    # FIX: Uses low/high instead of a hardcoded randint(1, 100), which used to
    # put the secret outside the visible range on Easy and Hard.
    st.session_state.secret = random.randint(low, high)
    # FIX: attempts started at 1 before a single guess was made, so the limit
    # check ended the game one guess early.
    st.session_state.attempts = 0
    # FIX: score, status and history were never reset, so a finished game
    # stayed finished and the old score carried over.
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []


# FIX: The secret used to be generated ONCE on first load and never again, so
# switching Normal -> Easy left a secret outside 1-20 and the round could not
# be won. A difficulty change now starts a fresh round.
if "secret" not in st.session_state or st.session_state.get("difficulty") != difficulty:
    st.session_state.difficulty = difficulty
    start_new_round()

st.subheader("Make a guess")

# FIX: The banner used to render ABOVE the submit handler that increments
# attempts, so "Attempts left" was stale by one for the whole session. A
# placeholder lets it keep its position but be filled in after the handler runs.
status_placeholder = st.empty()


def render_status_banner():
    attempts_left = max(attempt_limit - st.session_state.attempts, 0)
    # FIX: Was hardcoded to "between 1 and 100", which lied to the player on
    # Easy and Hard. Uses the actual low/high now.
    status_placeholder.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempts_left}"
    )


with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIX: "New Game" did not start a new game. It reset only attempts and the
# secret, leaving status "won"/"lost" so the st.stop() below still fired and the
# game stayed over. It now resets the full round.
if new_game:
    start_new_round()
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    render_status_banner()
    st.stop()

if submit:
    # FIX: The attempt used to be spent BEFORE the input was validated, so
    # submitting an empty box or "abc" burned a guess. Validation comes first.
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: Rejected input was appended to history, mixing raw strings in
        # with the int guesses. Invalid input now costs nothing at all.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: The unwinnable-game bug. On every even attempt the secret was
        # cast to str before this call: 50 == "50" is False, so a correct guess
        # could not win, and 50 > "50" raised TypeError into check_guess's
        # broken string fallback. The secret is now always passed as an int.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if outcome != "Win":
            # FIX: Unchecking "Show hint" suppressed ALL feedback, so a wrong
            # guess produced no response at all. It now only hides the
            # directional part -- the player is always told the guess was wrong.
            if show_hint:
                st.warning(message)
            else:
                st.warning("Not quite. Try again.")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

render_status_banner()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
