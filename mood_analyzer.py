# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

import re
from typing import List, Dict, Tuple, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        TODO: Improve this method.

        Right now, it does the minimum:
          - Strips leading and trailing whitespace
          - Converts everything to lowercase
          - Splits on spaces

        Ideas to improve:
          - Remove punctuation
          - Handle simple emojis separately (":)", ":-(", "🥲", "😂")
          - Normalize repeated characters ("soooo" -> "soo")
        """
        cleaned = text.strip().lower()

        # Extract emojis and text emoticons before removing punctuation
        emoji_pattern = re.compile(
            r"[:;]=?[)(DP/\\|]"   # text emoticons like :) :( ;) :/ :P
            r"|[😂😭🥲😊😍🥺😤😡💀🎉🔥❤️👍👎🙃😎🤔]"  # common unicode emojis
        )
        emojis = emoji_pattern.findall(cleaned)

        # Remove emojis/emoticons from text so they don't interfere with word tokenization
        cleaned = emoji_pattern.sub(" ", cleaned)

        # Remove punctuation
        cleaned = re.sub(r"[^\w\s]", "", cleaned)

        # Normalize repeated characters: 3+ of the same letter becomes 2
        # e.g., "soooo" -> "soo", "happyyy" -> "happyy"
        cleaned = re.sub(r"(.)\1{2,}", r"\1\1", cleaned)

        tokens = cleaned.split()

        # Append emojis as their own tokens
        tokens.extend(emojis)

        return tokens

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> int:
        """
        Compute a numeric "mood score" for the given text.

        Positive words increase the score.
        Negative words decrease the score.

        TODO: You must choose AT LEAST ONE modeling improvement to implement.
        For example:
          - Handle simple negation such as "not happy" or "not bad"
          - Count how many times each word appears instead of just presence
          - Give some words higher weights than others (for example "hate" < "annoyed")
          - Treat emojis or slang (":)", "lol", "💀") as strong signals
        """
        tokens = self.preprocess(text)
        score = 0

        # Words that flip the meaning of the next word
        negation_words = {"not", "no", "never", "dont", "doesnt", "didnt", "cant", "wont"}

        # Emoji scoring
        positive_emojis = {":)", ";)", ":D", "😂", "😊", "😍", "🎉", "🔥", "❤️", "👍", "😎"}
        negative_emojis = {":(", ":/", "😭", "🥺", "😤", "😡", "💀", "👎", "🙃", "🥲"}

        is_negated = False

        for token in tokens:
            # Check if this token is a negation word
            if token in negation_words:
                is_negated = True
                continue

            # Score emojis
            if token in positive_emojis:
                score += 1
                continue
            if token in negative_emojis:
                score -= 1
                continue

            # Score positive/negative words, flipping if negated
            if token in self.positive_words:
                score += -1 if is_negated else 1
                is_negated = False
            elif token in self.negative_words:
                score += 1 if is_negated else -1
                is_negated = False
            else:
                # Reset negation if the next word isn't a sentiment word
                is_negated = False

        return score

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score for a piece of text into a mood label.

        The default mapping is:
          - score > 0  -> "positive"
          - score < 0  -> "negative"
          - score == 0 -> "neutral"

        TODO: You can adjust this mapping if it makes sense for your model.
        For example:
          - Use different thresholds (for example score >= 2 to be "positive")
          - Add a "mixed" label for scores close to zero
        Just remember that whatever labels you return should match the labels
        you use in TRUE_LABELS in dataset.py if you care about accuracy.
        """
        score = self.score_text(text)
        tokens = self.preprocess(text)

        positive_emojis = {":)", ";)", ":D", "😂", "😊", "😍", "🎉", "🔥", "❤️", "👍", "😎"}
        negative_emojis = {":(", ":/", "😭", "🥺", "😤", "😡", "💀", "👎", "🙃", "🥲"}

        has_positive = any(t in self.positive_words or t in positive_emojis for t in tokens)
        has_negative = any(t in self.negative_words or t in negative_emojis for t in tokens)

        if has_positive and has_negative:
            return "mixed"
        elif score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        else:
            return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        TODO:
          - Look at the tokens and identify which ones counted as positive
            and which ones counted as negative.
          - Show the final score.
          - Return a short human readable explanation.

        Example explanation (your exact wording can be different):
          'Score = 2 (positive words: ["love", "great"]; negative words: [])'

        The current implementation is a placeholder so the code runs even
        before you implement it.
        """
        tokens = self.preprocess(text)

        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for token in tokens:
            if token in self.positive_words:
                positive_hits.append(token)
                score += 1
            if token in self.negative_words:
                negative_hits.append(token)
                score -= 1

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
