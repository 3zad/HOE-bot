import textstat
import nltk
from nltk.corpus import words

class Language:
    def __init__(self):
        nltk.download("words")
        self.word_set = set(words.words())
        
        self.curse_words = []
        with open("bot_utils/resources/curse_words.txt", 'r') as f:
            for line in f:
                line = line.strip("\t").strip("\n")
                self.curse_words.append(line)
    
    def is_gibberish(self, text):
        words_in_text = text.split()
        valid_words = sum(1 for word in words_in_text if word.lower() in self.word_set)
        
        return valid_words / max(len(words_in_text), 1) < 0.75
    
    def num_curses(self, text):
        summa = 0
        for word in self.curse_words:
            summa += text.lower().split().count(word.lower())
        return summa

    def reading_level(self, text):
        return textstat.flesch_kincaid_grade(text)

    def dale_chall(self, text):
        return textstat.dale_chall_readability_score(text)