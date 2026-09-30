from backend.app.tools.document_search import document_search

# --------------------------------------------------

# Relevant questions

# --------------------------------------------------

questions = [
"What is a primary key?",
"What does a foreign key do?",
"What are indexes used for?"
]

print("\nDocument Search Tool Test")
print("=" * 60)

for question in questions:


    print("\nQuestion:")
    print(question)

    print("\nTool result:")
    print("-" * 60)

    result = document_search.invoke(
    {
        "query": question
    }
)

print(result)

assert result
assert isinstance(result, str)

assert result != "No relevant information was found."


# --------------------------------------------------

# Test unrelated question

# --------------------------------------------------

print("\nTesting unrelated question")
print("=" * 60)

unrelated_question = "What is the capital of France?"

result = document_search.invoke(
{
"query": unrelated_question
}
)

print("\nQuestion:")
print(unrelated_question)

print("\nResult:")
print(result)

assert result == "No relevant information was found."

print("\nNo-result test PASSED")

print("\nDocument search tool test PASSED")
