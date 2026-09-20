# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
  There was a text box to input a guess. The game was in 'Normal' difficulty and had hints set to on.

- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

  The hints said lowe or higher when it should have been the opposite.
  The levels (easy, hard etc.) are switched
  The new game button doesn't start a new game

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| 31    | go higher| go lower | none |
| 50    | go higher| go lower | none |
| 98    | go higher| go lower | none |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

  Claude Code

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

  Claude said the hints in check_guess were reversed: when guess > secret the code returned "Go HIGHER!" when it should say "Go LOWER!", and both branches were backwards. It swapped the two messages. I verified it by calling the function directly and by running the new pytest suite against the old buggy code from git, where the hint-direction tests failed as expected. That confirmed the test actually catches the bug instead of just agreeing with the new code.

- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

  To fix the inverted difficulty levels, Claude widened Hard to a 1–200 range but left its attempt limit at 8. A guaranteed win on 1–200 takes exactly 8 guesses with perfect binary search, so Hard became winnable only with flawless play and no room for a single wasted guess. It also wrote a comment saying the attempt limits "decrease with difficulty" when Normal and Hard were both set to 8, so the comment contradicted the code. I changed it because a difficulty setting should be hard, not effectively unwinnable, and I checked my version by comparing each range against the number of guesses binary search needs.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  I checked that the new behavior was right, and that the old behavior would have been caught. 

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.


- Did AI help you design or understand any tests? How?
  Yes. Claude wrote the initial suite and, more usefully, pointed out that the three starter tests were already broken — they asserted check_guess(50, 50) == "Win", but the function returns a (outcome, message) tuple, so they would have failed even against correct code. It also suggested asserting relationships rather than hardcoded values, like checking that the Easy range is smaller than Normal which is smaller than Hard, so the test still holds if I retune the numbers later. The idea I'll reuse is running new tests against the old buggy code first to prove they actually detect the bug.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  Every time you click a button or type in a box, Streamlit throws away the whole page and runs your script again from line 1 to the bottom — there's no "onClick" handler that fires in isolation. That means ordinary Python variables are wiped on every interaction, which is why the secret number has to live in st.session_state: it's the one dictionary that survives a rerun, so random.randint() isn't called again and hand you a new secret mid-game.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

    I will continue to use the planning, execution, refractoring and reflection skills learnt in this assignment.

- What is one thing you would do differently next time you work with AI on a coding task?

  I will have a focus on planning and refreactoring.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  It made me trust its abilities a bit more, especially coupled with human supervision and planning.