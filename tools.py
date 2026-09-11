import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_order_status(order_id: str) -> dict:
    """يرجع حالة شحن الأوردر بناءً على order_id."""
    orders = _load_json("orders.json")
    for order in orders:
        if order["order_id"] == order_id:
            return {"status": "success", "data": order}
    return {"status": "error", "message": f"الأوردر رقم {order_id} مش موجود"}


def get_product_info(product_id: str) -> dict:
    """يرجع تفاصيل المنتج (الاسم، السعر، الوصف) بناءً على product_id."""
    products = _load_json("products.json")
    for product in products:
        if product["product_id"] == product_id:
            return {"status": "success", "data": product}
    return {"status": "error", "message": f"المنتج رقم {product_id} مش موجود"}


def check_stock(product_id: str) -> dict:
    """يرجع الكمية المتاحة بالمخزن للمنتج."""
    stock = _load_json("stock.json")
    for item in stock:
        if item["product_id"] == product_id:
            available = item["quantity"] > 0
            return {
                "status": "success",
                "data": {
                    "product_id": product_id,
                    "quantity": item["quantity"],
                    "available": available,
                },
            }
    return {"status": "error", "message": f"مفيش بيانات مخزون للمنتج {product_id}"}


def create_support_ticket(customer_id: str, issue: str) -> dict:
    """بيفتح تذكرة دعم فني جديدة للعميل ويحفظها."""
    tickets = _load_json("tickets.json")
    new_ticket = {
        "ticket_id": f"T{len(tickets) + 1001}",
        "customer_id": customer_id,
        "issue": issue,
        "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    tickets.append(new_ticket)
    _save_json("tickets.json", tickets)
    return {"status": "success", "data": new_ticket}


def check_refund_eligibility(order_id: str) -> dict:
    """بيتحقق هل الأوردر مؤهل للاسترجاع (خلال 14 يوم من الاستلام وحالته delivered)."""
    orders = _load_json("orders.json")
    for order in orders:
        if order["order_id"] == order_id:
            if order["status"] != "delivered":
                return {
                    "status": "success",
                    "data": {"eligible": False, "reason": "الأوردر لسه ماوصلش أو ماتسلمش"},
                }
            order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            days_passed = (datetime.now() - order_date).days
            eligible = days_passed <= 14
            return {
                "status": "success",
                "data": {
                    "eligible": eligible,
                    "days_since_delivery": days_passed,
                    "reason": "خلال فترة الاسترجاع" if eligible else "تعدت مدة الـ14 يوم",
                },
            }
    return {"status": "error", "message": f"الأوردر رقم {order_id} مش موجود"}


# اختبار سريع لكل الـ tools لوحدها
if __name__ == "__main__":
    print(get_order_status("1001"))
    print(get_order_status("9999"))
    print(get_product_info("P02"))
    print(check_stock("P02"))
    print(check_refund_eligibility("1002"))
    print(create_support_ticket("C01", "المنتج وصل باظ"))