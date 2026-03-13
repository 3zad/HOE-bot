import json

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Python workaround to make a singleton."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        self.config = None
        for _ in range(0,2):
            try:
                with open("config.json", "r") as f:
                    self.config = json.load(f)
                break
            except Exception as e:
                # copy config_example.json to config.json
                self.reset_config()
        if self.config is None:
            raise Exception("Failed to load config.json")
        
    def write_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    def read_config(self):
        with open("config.json", "r") as f:
            self.config = json.load(f)

    def reset_config(self):
        with open("config_example.json", "r") as f:
            example_config = json.load(f)
        with open("config.json", "w") as f:
            json.dump(example_config, f, indent=4)
        self.config = example_config