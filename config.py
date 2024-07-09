import json

with open(".env", "r", encoding="utf-8") as f:
    environment = dict()

    for line in f.readlines():
        if line.strip() != "":
            key = line.split("=")[0].strip()
            value = line.split("=")[1].strip()

            environment[key] = value


class Lexicon:
    def __init__(self):
        with open("lexicon.json", "r", encoding="utf-8") as f:
            self.lexicon = json.load(f)

    def get(self, key, lang):
        return self.lexicon[key].get(lang) or self.lexicon[key].get("en")
