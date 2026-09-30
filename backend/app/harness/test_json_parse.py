import json

content = '{"type":"function","function":{"name":"document_search","parameters":{"query":"foreign key relationship"}}}'

payload = json.loads(content)

print("PAYLOAD:", payload)
print("TYPE:", payload.get("type"))
print("TOOL:", payload.get("function", {}).get("name"))
print(
    "PARAMETERS:",
    payload.get("function", {}).get("parameters")
)