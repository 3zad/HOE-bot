import textstat
import nltk
from nltk.corpus import words
import re

class Language:
    def __init__(self):
        nltk.download("words")
        self.word_set = set(words.words())
        
        self.curse_words = []
        with open("bot_utils/resources/curse_words.txt", 'r') as f:
            for line in f:
                line = line.strip("\t").strip("\n")
                self.curse_words.append(line)

        self.emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess symbols and other
            "\U0001FA70-\U0001FAFF"  # Symbols for culture & education
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # Enclosed characters
            "]+", flags=re.UNICODE)
    
    def is_gibberish(self, text):
        words_in_text = text.split()
        valid_words = sum(1 for word in words_in_text if word.lower() in self.word_set)
        
        return valid_words / max(len(words_in_text), 1) < 0.5
    
    def num_curses(self, text):
        summa = 0
        for word in self.curse_words:
            summa += text.lower().split().count(word.lower())
        return summa
    
    def num_emojis(self, text):
        summa = 0
        for char in text:
            summa += len(self.emoji_pattern.findall(char))
        return summa

    def reading_level(self, text):
        return textstat.flesch_kincaid_grade(text)

    def dale_chall(self, text):
        return textstat.dale_chall_readability_score(text)