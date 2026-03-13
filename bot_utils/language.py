import re

class Language:
    # Character map for leetspeak or common substitutions
    LEETSPEAK_MAP = {
        'a': '[a@4]',
        'b': '[b8]',
        'c': '[c(<{]',
        'e': '[e3]',
        'g': '[g69]',
        'i': '[i1!|l]',
        'l': '[l1|]',
        'o': '[o0]',
        's': '[s5$]',
        't': '[t7+]',
        'z': '[z2]'
    }

    # Whitelist to prevent Scunthorpe problem (false positives)
    WHITELIST = {
        'snigger', 'raccoon', 'tycoon', 'cocoon', 'buffoon', 'analytics', 'bass', 'class', 'pass'
    }

    def __init__(self):
        self.curse_patterns = []
        with open("bot_utils/resources/curse_words.txt", "r", encoding="utf-8") as f:
            raw_words = [line.strip() for line in f.readlines()]
            for word in raw_words:
                if not word: continue
                # Generate regex for each word
                pattern_str = self.get_regex_for_word(word)
                self.curse_patterns.append(re.compile(pattern_str, re.IGNORECASE))

        self.really_bad_patterns = []
        with open("bot_utils/resources/really_bad_curse_words.txt", "r", encoding="utf-8") as f:
            raw_words = [line.strip() for line in f.readlines()]
            for word in raw_words:
                if not word: continue
                # Generate regex for each word
                pattern_str = self.get_regex_for_word(word)
                self.really_bad_patterns.append(re.compile(pattern_str, re.IGNORECASE))

    @staticmethod
    def is_english(text):
        pattern = r'^[a-zA-Z0-9\s\.,!@#$%^&*()_+-=\[\]{};:\'"<>/?\\|`~]*$'
        return bool(re.match(pattern, text))

    def get_regex_for_word(self, word: str) -> str:
        """
        Generates a regex pattern for a given word that allows for:
        - Leetspeak substitutions
        - Separators (dots, spaces, hyphens, etc.) between characters
        """
        pattern = ""
        for i, char in enumerate(word):
            # Get the regex for the character (or the character itself if no map)
            char_pattern = self.LEETSPEAK_MAP.get(char.lower(), re.escape(char))
            pattern += char_pattern
            
            # Allow for separators between characters, but not after the last one
            if i < len(word) - 1:
                # Allow any non-alphanumeric character as a separator, or spaces
                pattern += r'[\W_]*'
        
        return pattern

    def number_of_curse_words(self, text) -> int:
        count = 0
        for pattern in self.curse_patterns:
            matches = pattern.findall(text)
            for match in matches:
                 if not self.is_whitelisted(match, text):
                    count += 1
        return count

    def number_of_really_bad_curse_words(self, text) -> int:
        # This count might be less accurate with regex, but we can try to find all matches
        count = 0
        for pattern in self.really_bad_patterns:
            matches = pattern.findall(text)
            for match in matches:
                 if not self.is_whitelisted(match, text):
                    count += 1
        return count

    def contains_curse_words(self, text) -> bool:
        for pattern in self.curse_patterns:
            if pattern.search(text):
                return True
        return False

    def contains_really_bad_language(self, text) -> bool:
        for pattern in self.really_bad_patterns:
            # Search for the pattern in the text
            for match in pattern.finditer(text):
                matched_text = match.group()
                if not self.is_whitelisted(matched_text, text):
                    return True
        return False
        
    def is_whitelisted(self, match_text: str, full_text: str) -> bool:
        
        lower_text = full_text.lower()
        
        for safe_word in self.WHITELIST:
            if safe_word in lower_text:
                pass
        
        is_clean_match = match_text.isalpha()
        if is_clean_match:
             pass
        
        return False

    def contains_really_bad_language(self, text) -> bool:
        for pattern in self.really_bad_patterns:
            for match in pattern.finditer(text):
                if not self._is_false_positive(match, text):
                    return True
        return False

    def _is_false_positive(self, match, text) -> bool:
        start, end = match.span()
        
        if start > 0 and text[start-1].isalpha():
            full_word = self._get_surrounding_word(text, start, end)
            if full_word.lower() in self.WHITELIST:
                return True
            return False
            
        if end < len(text) and text[end].isalpha():
             full_word = self._get_surrounding_word(text, start, end)
             if full_word.lower() in self.WHITELIST:
                 return True
             return False
        return False

    def _get_surrounding_word(self, text, start, end):
        # Expand left
        while start > 0 and text[start-1].isalpha():
            start -= 1
        # Expand right
        while end < len(text) and text[end].isalpha():
            end += 1
        return text[start:end]