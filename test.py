import json

with open("resp.txt", "r") as file:
    content= file.read()
    print(json.loads(content))