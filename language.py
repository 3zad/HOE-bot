from langdetect import detect, detect_langs

# DO THIS ONLY IF THE MESSAGE IS LONGER THAN 5 WORDS

text = "Tere mina olen tõnu ja olen eestis"
print("Detected language:", detect(text))  # Output: 'fr' (French)
print("Probabilities:", detect_langs(text))  # Output: [('fr', 0.99)]
