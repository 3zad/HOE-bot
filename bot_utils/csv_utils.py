from db.MainDatabase import MainDatabase
import pandas as pd
import re
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from nltk.corpus import stopwords
import nltk
from collections import Counter

class CSVUtils:
    def __init__(self):
        self.db = MainDatabase()

        try:
            stopwords.words('english')
        except LookupError:
            nltk.download('stopwords')
            
        self.ENGLISH_STOP_WORDS = set(stopwords.words('english'))

    @staticmethod
    async def load_csv(filename) -> pd.DataFrame:
        df = pd.read_csv(filename)
        
        df['itemsets'] = df['itemsets'].apply(lambda x: eval(x, {"frozenset": frozenset, "__builtins__": {}}) 
                                              if isinstance(x, str) and x.startswith("frozenset(") 
                                              else x)
        return df

    async def to_csv(self) -> None:
        data = await self.db.to_CSV()

        with open("data.csv", 'w', encoding="UTF-8") as f:
            f.write(f"user_id,channel_id,message_content\n")
            for row in data:
                content: str = row[2].replace('\n', ' ').replace('\t', ' ').replace('’', '').replace(',', ' ').replace("'", '').lower()
                f.write(f"{row[0]},{row[1]},{content}\n")

    async def process_data(self, min_support=0.003) -> None:
        df = pd.read_csv("data.csv")

        df['message_content'] = df['message_content'].apply(self.__preprocess_message__)

        transactions = (
            df
            .apply(
                lambda row: row['message_content'] + [str(row['user_id'])], 
                axis=1
            )
            .tolist()
        )

        transactions = self.__preprocess_transactions__([t for t in transactions if t], min_support)

        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df_ohe = pd.DataFrame(te_ary, columns=te.columns_)

        freq_itemsets = fpgrowth(df_ohe, min_support=min_support, use_colnames=True)
        freq_itemsets = freq_itemsets.sort_values(by='support', ascending=False).reset_index(drop=True)

        freq_itemsets.to_csv("frequent_itemsets.csv", index=False)

    async def process_data_no_id(self, min_support=0.003) -> None:
        df = pd.read_csv("data.csv")

        df['message_content'] = df['message_content'].apply(self.__preprocess_message__)

        transactions = (
            df
            .apply(
                lambda row: row['message_content'],
                axis=1
            )
            .tolist()
        )

        transactions = self.__preprocess_transactions__([t for t in transactions if t], min_support)

        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df_ohe = pd.DataFrame(te_ary, columns=te.columns_)

        freq_itemsets = fpgrowth(df_ohe, min_support=min_support, use_colnames=True)
        freq_itemsets = freq_itemsets.sort_values(by='support', ascending=False).reset_index(drop=True)

        freq_itemsets.to_csv("pure_frequent_itemsets.csv", index=False)


    def __preprocess_transactions__(self, transactions, min_support):
        min_count = int(min_support * len(transactions))
        if min_count < 2:
            min_count = 2
        item_counts = Counter(item for transaction in transactions for item in transaction)
        frequent_items = {item for item, count in item_counts.items() if count >= min_count}
        filtered_transactions = [
            [item for item in t if item in frequent_items] 
            for t in transactions
        ]
        return [t for t in filtered_transactions if t]

    def __preprocess_message__(self, text):
        # Remove Discord custom emojis
        text = re.sub(r'<:[a-zA-Z0-9_]+:\d+>', '', text)
        
        # Remove punctuation and non-word characters
        text = re.sub(r'[^\w\s]', '', text) 
        
        # Tokenization
        tokens = text.split()
        
        # Filtering out single-character tokens and empty strings
        cleaned_tokens = [
            token for token in tokens 
            if token not in self.ENGLISH_STOP_WORDS and len(token) > 1 and "https" not in token
        ]
        return cleaned_tokens
