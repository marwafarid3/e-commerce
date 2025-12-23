import streamlit as st
import sqlite3
import json
from datetime import datetime

# ==========================
# إعداد الصفحة
# ==========================
st.set_page_config(page_title="متجر المستلزمات الطبية", page_icon="💊", layout="wide")

# ==========================
# قاعدة البيانات
# ==========================
conn = sqlite3.connect("store.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    img TEXT,
    desc TEXT,
    category TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    customer TEXT,
    phone TEXT,
    items TEXT,
    total REAL,
    payment_method TEXT,
    payment_status TEXT
)
""")
conn.commit()

# ==========================
# منتجات افتراضية
# ==========================
c.execute("SELECT COUNT(*) FROM products")
if c.fetchone()[0] == 0:
    products = [
        ("كمامة طبية", 2.5, "mask.jpg", "كمامة طبية ثلاثية الطبقات", "كمامات"),
        ("قفازات طبية", 5, "gloves.jpg", "قفازات لاتكس معقمة", "قفازات"),
        ("ميزان حرارة", 75, "thermo.jpg", "ميزان حرارة رقمي", "أجهزة"),
    ]
    c.executemany(
        "INSERT INTO products (name, price, img, desc, category) VALUES (?,?,?,?,?)",
        products
    )
    conn.commit()

# ==========================
# جلب المنتجات
# ==========================
def get_products():
    c.execute("SELECT name, price, img, desc, category FROM products")
    return c.fetchall()

# ==========================
# Session State
# ==========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "paid" not in st.session_state:
    st.session_state.paid = False

# ==========================
# العنوان
# ==========================
st.title("💊 متجر المستلزمات الطبية")

# ==========================
# عرض المنتجات
# ==========================
st.subheader("🛍️ المنتجات")

for p in get_products():
    st.markdown(f"### {p[0]}")
    st.write(p[3])
    st.write(f"💰 السعر: {p[1]} جنيه")

    qty = st.number_input(f"الكمية ({p[0]})", min_value=1, max_value=10, key=p[0])
    if st.button(f"🛒 أضف {p[0]}"):
        st.session_state.cart.append(
            {"name": p[0], "price": p[1], "qty": qty}
        )
        st.success("تمت الإضافة للسلة")

st.divider()

# ==========================
# سلة المشتريات
# ==========================
st.subheader("🧺 سلة المشتريات")

if not st.session_state.cart:
    st.info("السلة فارغة")
else:
    total = sum(i["price"] * i["qty"] for i in st.session_state.cart)
    for i in st.session_state.cart:
        st.write(f"{i['name']} × {i['qty']} = {i['price']*i['qty']} جنيه")

    st.write(f"### الإجمالي: {total} جنيه")

    name = st.text_input("اسم العميل")
    phone = st.text_input("رقم الهاتف")

    payment_method = st.selectbox(
        "طريقة الدفع",
        ["الدفع عند الاستلام", "دفع أونلاين (محاكاة)"]
    )

    # ==========================
    # دفع أونلاين وهمي
    # ==========================
    if payment_method == "دفع أونلاين (محاكاة)":
        st.subheader("💳 بوابة دفع وهمية")

        card = st.text_input("رقم البطاقة (16 رقم)")
        exp = st.text_input("تاريخ الانتهاء (MM/YY)")
        cvv = st.text_input("CVV", type="password")

        if st.button("💰 تنفيذ الدفع"):
            if len(card) == 16 and cvv.isdigit():
                st.session_state.paid = True
                st.success("✅ تم الدفع بنجاح (محاكاة)")
            else:
                st.error("❌ بيانات البطاقة غير صحيحة")

    # ==========================
    # تأكيد الطلب
    # ==========================
    if st.button("🧾 تأكيد الطلب"):
        if not name or not phone:
            st.error("أدخل البيانات كاملة")
        elif payment_method == "دفع أونلاين (محاكاة)" and not st.session_state.paid:
            st.error("يجب إتمام الدفع أولاً")
        else:
            c.execute("""
            INSERT INTO orders 
            (created_at, customer, phone, items, total, payment_method, payment_status)
            VALUES (?,?,?,?,?,?,?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name,
                phone,
                json.dumps(st.session_state.cart, ensure_ascii=False),
                total,
                payment_method,
                "مدفوع" if st.session_state.paid else "عند الاستلام"
            ))
            conn.commit()
            st.success("✔ تم تسجيل الطلب")
            st.session_state.cart.clear()
            st.session_state.paid = False

