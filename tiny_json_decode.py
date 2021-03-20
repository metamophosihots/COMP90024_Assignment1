import json
with open("tinyTwitter.json", "r") as read_file:
    data = json.load(read_file)
print(json.dumps(data, indent=4, sort_keys=True))