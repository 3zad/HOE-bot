import textstat
import nltk
from nltk.corpus import words

nltk.download("words")  # Download dictionary

# Get a set of real English words
word_set = set(words.words())

def is_gibberish(text):
    words_in_text = text.split()  # Split by spaces
    valid_words = sum(1 for word in words_in_text if word.lower() in word_set)
    
    # If less than 75% of words are real, it's likely gibberish
    return valid_words / max(len(words_in_text), 1) < 0.75

text = "Sounds good although I don’t get the hostages I never do any of that"

if is_gibberish(text):
    print("Likely gibberish, ignoring analysis.")
else:
    print("Reading Level:", textstat.flesch_kincaid_grade(text))
    print("Dale-Chall Score:", textstat.dale_chall_readability_score(text))