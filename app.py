import gradio as gr

# ⚠️ هذه دالة placeholder مؤقتة
# لما زميلك يخلص llm.py، هنستبدل الكود جوه الدالة دي
# بنداء حقيقي على الموديل، زي:
# from llm import get_response
def get_response(user_message, chat_history):
    try:
        # --- كود مؤقت للتجربة فقط ---
        if not user_message or user_message.strip() == "":
            return "من فضلك اكتب رسالة."

        response = f"(رد تجريبي) استلمت رسالتك: {user_message}"
        # --- هنا هيتم استبدال السطرين اللي فوق بالنداء الحقيقي على الموديل ---

        return response

    except Exception as e:
        # أي خطأ غير متوقع (مثلاً الموديل مش شغال) هيتمسك هنا
        return f"⚠️ حصل خطأ أثناء معالجة طلبك: {str(e)}"


def chat_fn(user_message, chat_history):
    bot_response = get_response(user_message, chat_history)
    chat_history.append((user_message, bot_response))
    return "", chat_history


with gr.Blocks(title="AI Customer Support Agent") as demo:
    gr.Markdown("## 🤖 AI Customer Support Agent")
    gr.Markdown("اسأل عن حالة أوردرك، بيانات منتج، المخزون، أو سياسات الاسترجاع والضمان.")

    chatbot = gr.Chatbot(label="المحادثة", height=400)
    msg = gr.Textbox(label="اكتب رسالتك هنا", placeholder="مثال: عايز أعرف حالة الأوردر رقم 123")
    clear = gr.Button("مسح المحادثة")

    msg.submit(chat_fn, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot)

if __name__ == "__main__":
    demo.launch()