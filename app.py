import gradio as gr
from llm import chat


def chat_fn(user_message, chat_display, model_history):
    if not user_message or user_message.strip() == "":
        return "", chat_display, model_history

    bot_response, model_history = chat(user_message, model_history)

    chat_display.append({"role": "user", "content": user_message})
    chat_display.append({"role": "assistant", "content": bot_response})

    return "", chat_display, model_history


with gr.Blocks(title="AI Customer Support Agent") as demo:
    gr.Markdown("## 🤖 AI Customer Support Agent")
    gr.Markdown("اسأل عن حالة أوردرك، بيانات منتج، المخزون، أو سياسات الاسترجاع والضمان.")

    chatbot = gr.Chatbot(label="المحادثة", height=400)
    msg = gr.Textbox(label="اكتب رسالتك هنا", placeholder="مثال: عايز أعرف حالة الأوردر رقم 123")
    clear = gr.Button("مسح المحادثة")

    model_history_state = gr.State([])

    msg.submit(chat_fn, [msg, chatbot, model_history_state], [msg, chatbot, model_history_state])
    clear.click(lambda: ([], []), None, [chatbot, model_history_state])


if __name__ == "__main__":
    demo.launch()