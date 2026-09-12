import os
import chromadb
from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
POLICIES_FILE = os.path.join(DATA_DIR, "policies.txt")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# موديل تحويل النص لأرقام (embeddings) - صغير وسريع
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# عميل ChromaDB بيحفظ البيانات على القرص (مش في الذاكرة بس)
# عشان مانعملش embedding من الأول كل مرة نشغل فيها البرنامج
client = chromadb.PersistentClient(path=CHROMA_DIR)


def chunk_text(text: str, chunk_size: int = 60) -> list[str]:
    """بيقسم النص لقطع، كل قطعة تقريبًا chunk_size كلمة."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for paragraph in paragraphs:
        words = paragraph.split()
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])
            if chunk:
                chunks.append(chunk)
    return chunks


def build_index():
    """
    بيقرأ ملف السياسات، يقسمه، يحوله لـ embeddings، ويخزنهم في ChromaDB.
    لو الـ collection موجودة بالفعل، بيمسحها ويعيد بناءها من الأول
    (عشان لو عدّلت في policies.txt، التغيير ينعكس).
    """
    try:
        client.delete_collection("policies")
    except Exception:
        pass  # الـ collection مش موجودة أصلاً، عادي

    collection = client.create_collection("policies")

    with open(POLICIES_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    embeddings = embedding_model.encode(chunks).tolist()
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(documents=chunks, embeddings=embeddings, ids=ids)
    print(f">> تم بناء الفهرس: {len(chunks)} قطعة تم تخزينها")
    return collection


def get_collection():
    """بيرجع الـ collection الموجودة، أو يبنيها لو مش موجودة."""
    try:
        return client.get_collection("policies")
    except Exception:
        return build_index()


def retrieve_policy(question: str, top_k: int = 2) -> str:
    """
    بياخد سؤال العميل، ويرجع أقرب top_k قطع نصية من السياسات
    مدموجة في نص واحد، جاهزة تتحط في الـ prompt.
    """
    collection = get_collection()
    query_embedding = embedding_model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    matched_chunks = results["documents"][0]
    return "\n\n".join(matched_chunks)


# اختبار سريع لوحده
if __name__ == "__main__":
    build_index()
    print("\n=== اختبار: سؤال عن الاسترجاع ===")
    print(retrieve_policy("Can I return a broken product?"))

    print("\n=== اختبار: سؤال عن الضمان ===")
    print(retrieve_policy("How long is the warranty?"))