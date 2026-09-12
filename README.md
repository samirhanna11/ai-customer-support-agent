# AI Customer Support Agent

## Team
- **Project:** Team 2 – Project 2 (DEPI Team Project)
- **Members:** Zyad Waled Talaat, Samir Hanna

## Problem Statement
Companies receive repetitive customer support requests (order status, product
info, stock availability, refund eligibility, policy questions) that consume
support staff time. This project builds an AI-powered support agent that
answers these requests automatically using a local LLM connected to real
company data, and escalates anything it cannot confidently handle.

## Features
- Conversational chat interface built with Gradio
- Maintains conversation history within a session
- 5 callable tools that the LLM decides to use on its own:
  - `get_order_status` – order shipping status
  - `get_product_info` – product name, price, and description
  - `check_stock` – stock availability for a product
  - `create_support_ticket` – opens a support ticket for a customer issue
  - `check_refund_eligibility` – checks whether an order qualifies for a refund
- RAG (Retrieval-Augmented Generation) over company policy documents
  (refund, warranty, shipping, exchange) using ChromaDB + sentence-transformers
- Language handling: messages containing Arabic are detected and routed to a
  fixed "a representative will contact you in your language" response instead
  of being sent to the LLM, since the small model is unreliable in Arabic
- Reliability: strict system prompt rules prevent the model from inventing
  order/product/customer IDs or policy details; tools always return a
  structured `status: success/error` so the model reports "not found" instead
  of guessing

## Model Used
**Ollama – `llama3.2:3b`**

We initially planned to use `phi3:mini`, but discovered it does not support
Ollama's native tool-calling API. We switched to `llama3.2:3b`, which supports
tool calling reliably and still stays under our 3GB size constraint.

## How to Run

1. Install [Ollama](https://ollama.com) and pull the model:
2. Clone this repository and create a virtual environment:
3. Install dependencies:
4. Run the app:
5. Open the local URL shown in the terminal (e.g. `http://127.0.0.1:7860`).

## Architecture
User → Gradio UI (app.py)
│
▼
llm.py (chat function)
│
┌──────┴──────┐
│ │
Arabic? English
│ │
Fixed reply Ollama (llama3.2:3b) + tools_schema
│
┌─────────┼─────────────┐
▼ ▼ ▼
tools.py tools.py rag.py
(order/product/stock/ticket/refund) (policy retrieval via ChromaDB)
│ │
└──────────┬──────────────┘
▼
Final response to user


## Tools Explained

| Tool | Input | What it does |
|---|---|---|
| `get_order_status` | `order_id` | Reads `data/orders.json`, returns shipping status |
| `get_product_info` | `product_id` | Reads `data/products.json`, returns name/price/description |
| `check_stock` | `product_id` | Reads `data/stock.json`, returns quantity + availability |
| `create_support_ticket` | `customer_id`, `issue` | Appends a new ticket to `data/tickets.json` |
| `check_refund_eligibility` | `order_id` | Checks delivery status + 14-day window from `data/orders.json` |
| `retrieve_policy` | `question` | Embeds the question, retrieves the closest matching policy chunk from ChromaDB |

## Multi-Tool Example 1 (Refund + Ticket)
**Customer:** "My headphones arrived broken, can I get a refund? My order id
is 1002 and my customer id is C02."

The model calls `check_refund_eligibility(order_id="1002")`, confirms the
order is within the 14-day window, then calls
`create_support_ticket(customer_id="C02", issue="broken headphones")` and
replies with a summary and the ticket ID.

## Multi-Tool Example 2 (Policy + Product)
**Customer:** "What's your warranty policy, and can you tell me about
product P02?"

The model calls `retrieve_policy(question="warranty policy")` to fetch the
warranty terms, then calls `get_product_info(product_id="P02")` to get the
product details, and combines both into a single reply.

## RAG (Retrieval-Augmented Generation)
Company policy documents (`data/policies.txt`) are split into chunks, embedded
using `sentence-transformers` (`all-MiniLM-L6-v2`), and stored in a persistent
ChromaDB collection. When a customer asks a policy-related question, the
`retrieve_policy` tool embeds the question and retrieves the most relevant
chunks, which are fed back to the LLM so it answers from real company policy
instead of its own (potentially incorrect) knowledge.

## Limitations
- `llama3.2:3b` is a small model; it can occasionally call a tool
  unnecessarily on vague messages, though the system prompt mitigates this
- Arabic support is limited to a fixed handoff message, not full bilingual
  conversation
- Demo data is small and static (a handful of orders/products)
- No authentication or real customer verification

## Future Improvements
- Add proper Arabic support with a multilingual model or translation layer
- Expand demo data and connect to a real database
- Add streaming responses in the Gradio UI
- Add automated tests for each tool and the RAG pipeline