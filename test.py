import json

a = [1,2,3,4,55,]
b = json.dumps(a, indent=2, ensure_ascii=False)
print(type(b))