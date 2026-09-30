# AI Research & Knowledge Assistant + AI Agent Harness

A production-oriented AI research assistant and AI agent reliability harness built with Python, LangGraph, Ollama, RAG, Qdrant, PostgreSQL, Vue 3, automated evaluation, tracing, guardrails, regression testing, and CI/CD evaluation gates.

> AI agents need more than an LLM. They need execution control, context control, validation, observability, evaluation, and regression protection.

## Project Overview

This project contains two connected systems.

### AI Research & Knowledge Assistant

A technical research assistant that can:

- Answer questions using a knowledge base
- Retrieve relevant information using RAG
- Perform calculations using a controlled calculator tool
- Ground answers in retrieved information
- Avoid unsupported answers when relevant knowledge is unavailable
- Return retrieved source information

### AI Agent Harness

A reliability layer around the AI agent providing:

- Tool validation
- Tool execution limits
- Graph-level execution control
- Context management
- Input validation
- Output validation
- Guardrails
- Retrieval validation
- Run tracing
- PostgreSQL trace persistence
- Answer evaluation
- Retrieval evaluation
- Regression testing
- Evaluation gates
- CI/CD integration

## Architecture

```text
User
 |
 v
Vue 3 Frontend
 |
 v
FastAPI API
 |
 v
LangGraph Agent
 |
 +-------------------+
 |                   |
 v                   v
Knowledge Search   Calculator
 |
 v
Embedding Generation
 |
 v
Qdrant Vector Database
 |
 v
Retrieved Context
 |
 v
Grounded Answer

        AI AGENT HARNESS
               |
   +-----------+-----------+
   |           |           |
   v           v           v
Execution   Context     Tool
Control     Control     Policies
   |           |           |
   +-----------+-----------+
               |
   +-----------+-----------+
   |           |           |
   v           v           v
Validation Guardrails Observability
               |
   +-----------+-----------+
   |           |           |
   v           v           v
Evaluation Regression CI/CD Gate
                       |
                       v
                  PostgreSQL
