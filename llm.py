import re
import gradio as gr
import ollama
from tools import (
    get_order_status,
    get_product_info,
    check_stock,
    create_support_ticket,
    check_refund_eligibility,
    

)
from rag import retrieve_policy
MODEL_NAME = "llama3.2:3b"

ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF]")


def contains_arabic(text: str) -> bool:
    return bool(ARABIC_PATTERN.search(text))
    
    available_functions = {
    "get_order_status": get_order_status,
    "get_product_info": get_product_info,
    "check_stock": check_stock,
    "create_support_ticket": create_support_ticket,
    "check_refund_eligibility": check_refund_eligibility,
    "retrieve_policy": retrieve_policy,
}


tools_schema = [    {
        "type": "function",
        "function": {
            "name": "retrieve_policy",
            "description": "Searches company policies (refund, warranty, shipping, exchange) and returns relevant policy text to answer the customer's question",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The customer's policy-related question"}
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Returns the shipping status of an order given its order_id",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order ID"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "Returns product name, price, and description given a product_id",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "The product ID"}
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Checks available stock quantity for a given product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "The product ID"}
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Opens a new support ticket for a customer with an issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "The customer ID"},
                    "issue": {"type": "string", "description": "Description of the issue"},
                },
                "required": ["customer_id", "issue"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund_eligibility",
            "description": "Checks whether an order is eligible for a refund",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order ID"}
                },
                "required": ["order_id"],
            },
        },
    },
]

available_functions = {
    "get_order_status": get_order_status,
    "get_product_info": get_product_info,
    "check_stock": check_stock,
    "create_support_ticket": create_support_ticket,
    "check_refund_eligibility": check_refund_eligibility,
}

SYSTEM_PROMPT = """
You are a customer support assistant for an electronics company.

STRICT RULES:
1. ONLY use a tool when the customer has given you a real, specific ID (an order number, product number, or customer number) that they actually typed themselves.
2. NEVER invent, guess, or make up an order_id, product_id, or customer_id. If the customer didn't give you one, ASK them for it in plain text - do not call any tool.
3. For greetings, thanks, small talk, or vague messages (like "hi", "hello", "thanks"), reply normally and briefly. Do NOT call any tool.
4. Never invent information about orders or products.
5. If a tool returns an error or says something was not found, tell the customer clearly that you could not find it - do not make up a status or details.
6. If the customer has a problem (broken product, complaint), open a support ticket only after you have both a real customer_id and a description of the issue.
7. Always reply in English, in a polite and professional tone.
8. For questions about company policies (refund rules, warranty, shipping, exchange), use the retrieve_policy tool instead of answering from your own knowledge.
"""

ARABIC_FALLBACK_MESSAGE = (
    "شكرًا لتواصلك معنا. سيتم تحويل رسالتك لأحد ممثلي خدمة العملاء "
    "الذين يتحدثون لغتك للرد عليك في أقرب وقت."
)


def chat(user_message: str, history: list) -> tuple[str, list]:
    history.append({"role": "user", "content": user_message})

    if contains_arabic(user_message):
        history.append({"role": "assistant", "content": ARABIC_FALLBACK_MESSAGE})
        return ARABIC_FALLBACK_MESSAGE, history

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    response = ollama.chat(model=MODEL_NAME, messages=messages, tools=tools_schema)
    message = response["message"]

    if message.get("tool_calls"):
        print(">> Tool calls requested:", message.get("tool_calls"))
        history.append(message)
        for call in message["tool_calls"]:
            func_name = call["function"]["name"]
            func_args = call["function"]["arguments"]
            func = available_functions.get(func_name)
            if func:
                result = func(**func_args)
            else:
                result = {"status": "error", "message": "Unknown tool"}
            print(f">> Result of {func_name}:", result)
            history.append(
                {"role": "tool", "content": str(result), "name": func_name}
            )

        final_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        final_response = ollama.chat(model=MODEL_NAME, messages=final_messages)
        final_text = final_response["message"]["content"]
        history.append({"role": "assistant", "content": final_text})
        return final_text, history

    print(">> No tool calls - model answered directly")
    history.append({"role": "assistant", "content": message["content"]})
    return message["content"], history


if __name__ == "__main__":
    print("=== اختبار 1: Multi-tool (استرجاع + تذكرة) ===")
    history_1 = []
    reply1, history_1 = chat(
        "My headphones arrived broken, can I get a refund? My order id is 1002 and my customer id is C02.",
        history_1,
    )
    print("الرد:", reply1)

    print("\n=== اختبار 2: رسالة عادية من غير tool ===")
    history_2 = []
    reply2, history_2 = chat("Hello, thank you!", history_2)
    print("الرد:", reply2)

    print("\n=== اختبار 3: أوردر مش موجود بالإنجليزي ===")
    history_3 = []
    reply3, history_3 = chat("What's the status of order 9999?", history_3)
    print("الرد:", reply3)