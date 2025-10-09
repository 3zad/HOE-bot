from db.MainDatabase import MainDatabase

class CSVUtils:
    def __init__(self):
        self.db = MainDatabase()

    async def toCSV(self):
        data = await self.db.to_CSV()

        with open("data.csv", 'w', encoding="UTF-8") as f:
            f.write(f"user_id,channel_id,message_content\n")
            for row in data:
                content: str = row[2].replace('\n', ' ').replace('\t', ' ').replace('’', '').replace(',', ' ').replace("'", '').lower()
                f.write(f"{row[0]},{row[1]},{content}\n")