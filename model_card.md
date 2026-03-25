# Model Card: Mood Machine

This model card is for the Mood Machine project, which includes **two** versions of a mood classifier:

1. A **rule based model** implemented in `mood_analyzer.py`
2. A **machine learning model** implemented in `ml_experiments.py` using scikit learn

You may complete this model card for whichever version you used, or compare both if you explored them.

## 1. Model Overview

**Model type:**
I used the rule based model implemented in `mood_analyzer.py`.

**Intended purpose:**
Classify short social media style text messages into one of four mood labels: positive, negative, neutral, or mixed.

**How it works (brief):**
The model preprocesses text by lowercasing, removing punctuation, normalizing repeated characters (e.g., “soooo” to “soo”), and extracting emojis as separate tokens. It then scores the text by looping through tokens: positive words add +1, negative words subtract -1, and emojis are scored similarly. Negation words like “not” and “never” flip the score of the next sentiment word. Finally, if both positive and negative signals are detected, the label is “mixed”; otherwise it maps score > 0 to “positive”, score < 0 to “negative”, and score == 0 to “neutral”.



## 2. Data

**Dataset description:**
The dataset contains 13 short posts in `SAMPLE_POSTS`. It started with 6 posts and was expanded with 7 new ones designed to test realistic language patterns including slang, emojis, sarcasm, and mixed emotions.

**Labeling process:**
Labels were chosen by reading each post and deciding the overall emotional intent. Some posts were deliberately hard to label:
- "I absolutely love getting zero sleep before an exam" is sarcastic, so labeled "negative" even though the words sound positive.
- "Idk how to feel about today honestly" is genuinely ambiguous and could be "neutral" or "mixed" depending on interpretation.
- "Everything is falling apart but at least I have coffee :)" has both clear negativity and a positive coping tone, labeled "mixed".

**Important characteristics of your dataset:**
- Contains slang ("lowkey", "rn", "gonna", "idk")
- Includes unicode emojis (😂, 💀, 🥲, 🎉) and text emoticons (:))
- Includes sarcasm ("I absolutely love getting zero sleep before an exam")
- Some posts express mixed feelings ("Proud of myself but also exhausted 🥲")
- Contains short or ambiguous messages ("This is fine", "Idk how to feel about today honestly")

**Possible issues with the dataset:**
- Very small (only 13 examples), so accuracy numbers may not generalize
- Label distribution is uneven: 4 positive, 3 negative, 3 mixed, 2 neutral, 1 sarcastic negative
- Does not cover many language styles (no code-switching, no all-caps anger, no longer multi-sentence posts)
- Sarcasm is underrepresented with only one clear example

## 3. How the Rule Based Model Works (if used)

**Your scoring rules:**
- Each positive word (e.g., "love", "excited", "proud") adds +1 to the score
- Each negative word (e.g., "terrible", "stressed", "exhausted") subtracts -1 from the score
- Positive emojis (:), 😂, 🎉, 😊, etc.) add +1; negative emojis (:(, 💀, 🥲, 🙃, etc.) subtract -1
- Negation handling: words like "not", "never", "dont", "cant" flip the score of the next sentiment word (e.g., "not happy" scores -1 instead of +1)
- Mixed detection: if both positive and negative signals (words or emojis) are present in a post, the label is "mixed" regardless of the net score
- Threshold: score > 0 = "positive", score < 0 = "negative", score == 0 = "neutral"

**Preprocessing enhancements:**
- Punctuation removal so "great!" matches "great"
- Emojis are extracted as separate tokens before punctuation is stripped
- Repeated characters are normalized (3+ of the same letter collapses to 2, e.g., "soooo" becomes "soo")

**Strengths of this approach:**
- Transparent and explainable: you can trace exactly why any prediction was made
- Works well for straightforward posts with clear sentiment words ("I love this class", "Today was a terrible day")
- Negation handling correctly flips "I am not happy about this" to negative
- Mixed detection catches posts with competing signals like "Proud of myself but also exhausted 🥲"

**Weaknesses of this approach:**
- Cannot detect sarcasm: "I absolutely love getting zero sleep before an exam" is predicted as "positive" because "love" is a positive word and the model doesn't understand ironic context
- Completely dependent on the word lists: any word not in the lists is invisible to the model
- Treats all words equally (no weighting): "hate" counts the same as "boring"
- Cannot understand phrases or context: "falling apart" works only because both "falling" and "apart" happen to be in the negative list individually

## 4. How the ML Model Works (if used)

Not used in this iteration. Only the rule based model was implemented and evaluated.

## 5. Evaluation

**How you evaluated the model:**
The model was evaluated on all 13 posts in `SAMPLE_POSTS` by comparing `predict_label()` output against `TRUE_LABELS`. Overall accuracy: **12/13 (92%)**.

**Examples of correct predictions:**
- "I am not happy about this" -> predicted "negative", true "negative". The negation handler correctly flipped "happy" from positive to negative.
- "Proud of myself but also exhausted 🥲" -> predicted "mixed", true "mixed". The model detected "proud" (positive) and "exhausted" + 🥲 (negative), triggering the mixed label.
- "This is fine" -> predicted "neutral", true "neutral". No sentiment words were found, so the score stayed at 0.

**Examples of incorrect predictions:**
- "I absolutely love getting zero sleep before an exam" -> predicted "positive", true "negative". This is sarcasm. The model sees "love" as positive and has no way to understand that the sentence is ironic. This is the main failure case and a fundamental limitation of rule based approaches.

## 6. Limitations

- **Small dataset**: only 13 labeled examples, so the 92% accuracy may not reflect real-world performance
- **No sarcasm detection**: the model takes words at face value and cannot understand irony or sarcastic tone
- **Word list dependency**: any sentiment word not in `POSITIVE_WORDS` or `NEGATIVE_WORDS` is completely invisible to the model
- **No phrase understanding**: the model processes words individually and cannot understand multi-word expressions (e.g., "not bad at all" would only catch "not" + "bad", missing that "at all" intensifies)
- **Single language only**: only handles English and a fixed set of common emojis
- **Short text only**: designed for single-sentence social media posts, not paragraphs or conversations

## 7. Ethical Considerations

- **Misclassifying distress**: a message like "I can't do this anymore" could be a sign of serious distress but might be labeled "neutral" if the words aren't in the negative list. Using mood detection in mental health contexts without human oversight is dangerous.
- **Cultural and linguistic bias**: the word lists and emoji interpretations reflect one cultural perspective. Slang, emojis, and tone vary across communities, ages, and regions. For example, 💀 can mean "laughing so hard" or genuinely negative depending on context.
- **Sarcasm misreadings**: labeling a sarcastic complaint as "positive" could lead to harmful decisions if used in customer service or content moderation.
- **Privacy concerns**: analyzing personal messages for mood raises consent and surveillance issues, especially if users don't know their messages are being classified.
- **Oversimplification**: reducing human emotion to four labels (positive, negative, neutral, mixed) erases nuance and complexity in how people actually feel.

## 8. Ideas for Improvement

- **Expand the dataset**: add 50+ labeled posts covering more language styles, longer texts, and edge cases
- **Add word weighting**: give stronger words like "hate" or "amazing" higher scores than mild words like "good" or "bad"
- **Sarcasm heuristics**: detect patterns like positive words followed by clearly negative contexts (e.g., "love" + "zero sleep")
- **Try the ML model**: train the scikit-learn model in `ml_experiments.py` on the same data to see if it can learn patterns the rules miss
- **Use a separate test set**: currently evaluating on the same data used to build the rules, which inflates accuracy
- **Add bigram/phrase detection**: recognize multi-word expressions like "falling apart", "no cap", or "let's go" as single units
- **Expand emoji coverage**: add more emojis and handle skin tone variants and emoji combinations
