class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.api_key = self.read_api_key()

    def read_api_key(self):
        with open(self.config_file, 'r') as file:
            for line in file:
                if line.startswith("API_KEY"):
                    return line.split('=')[1].strip()
        return None
