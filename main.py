import json

myjsonfile = open('21stcenturywire.json', 'r')
jsondata = myjsonfile.read()
obj = json.loads(jsondata)
print(obj[1]["id"])

