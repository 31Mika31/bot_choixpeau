import json

with open("questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(type(data))
    print(data)
