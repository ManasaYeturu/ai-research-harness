from backend.app.agent.graph import build_graph


graph = build_graph()

result = graph.invoke({
    "question": "What is PostgreSQL?",
    "answer": ""
})

print("\nQUESTION:")
print(result["question"])

print("\nANSWER:")
print(result["answer"])