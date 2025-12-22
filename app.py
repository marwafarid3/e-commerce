import streamlit as st
import sqlite3
import json
from datetime import datetime

# ==========================
# إعداد الصفحة
# ==========================
st.set_page_config(page_title="متجر المستلزمات الطبية", page_icon="💊", layout="wide")

# ==========================
# الاتصال بقاعدة البيانات
# ==========================
conn = sqlite3.connect("store.db", check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
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
    payment_method TEXT
)
""")
conn.commit()

# ==========================
# إدخال منتجات افتراضية (مرة واحدة فقط)
# ==========================
c.execute("SELECT COUNT(*) FROM products")
if c.fetchone()[0] == 0:
    default_products = [
        ("كمامة طبية", 2.5, "mask.jpg", "كمامة واقية ثلاثية الطبقات.", "كمامات"),
        ("قفازات طبية", 5.0, "gloves.jpg", "قفازات لاتكس معقمة للاستعمال الواحد.", "قفازات"),
        ("جهاز قياس ضغط الدم", 350, "blood_pressure.jpg", "جهاز رقمي لقياس ضغط الدم بدقة.", "أجهزة"),
        ("ميزان حرارة إلكتروني", 75, "thermometer.jpg", "ميزان حرارة رقمي سريع القراءة.", "أجهزة"),
        ("مطهر يدين", 25, "sanitizer.jpg", "مطهر كحولي بنسبة 70%.", "مطهرات"),
        ("كرسي متحرك", 1450, "wheelchair.jpg", "كرسي متين وخفيف الوزن قابل للطي.", "أجهزة"),
    ]
    c.executemany(
        "INSERT INTO products (name, price, img, desc, category) VALUES (?,?,?,?,?)",
        default_products
    )
    conn.commit()

# ==========================
# جلب المنتجات
# ==========================
def get_products():
    c.execute("SELECT name, price, img, desc, category FROM products")
    rows = c.fetchall()
    return [
        {"name": r[0], "price": r[1], "img": r[2], "desc": r[3], "category": r[4]}
        for r in rows
    ]

# ==========================
# حالة الجلسة
# ==========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ==========================
# شريط جانبي
# ==========================
st.sidebar.title("القائمة 👇")
page = st.sidebar.selectbox(
    "انتقل إلى:",
    ["المتجر", "سلة المشتريات", "لوحة التحكم (Admin)", "الطلبات (Admin)"]
)

# ---------------- Admin Login ----------------
st.sidebar.markdown("---")
st.sidebar.subheader("🔐 تسجيل دخول الأدمن")
if not st.session_state.is_admin:
    admin_user = st.sidebar.text_input("اسم المستخدم")
    admin_pass = st.sidebar.text_input("كلمة المرور", type="password")
    if st.sidebar.button("تسجيل دخول"):
        if admin_user == "admin" and admin_pass == "1234":
            st.session_state.is_admin = True
            st.sidebar.success("تم تسجيل الدخول كـ Admin ✅")
        else:
            st.sidebar.error("بيانات غير صحيحة ❌")
else:
    st.sidebar.success("أنت مسجل كـ Admin ✅")
    if st.sidebar.button("تسجيل خروج"):
        st.session_state.is_admin = False

# ==========================
# عنوان المتجر
# ==========================
st.title("💊 متجر المستلزمات الطبية")

# ==========================
# صفحة المتجر
# ==========================
if page == "المتجر":
    st.subheader("🛍️ المنتجات المتاحة")

    products = get_products()

    categories = ["الكل"] + sorted(list({p["category"] for p in products}))
    category_filter = st.selectbox("فئة المنتج", categories)
    search_text = st.text_input("🔍 ابحث عن منتج")

    filtered_products = [
        p for p in products
        if (category_filter == "الكل" or p["category"] == category_filter)
        and search_text.lower() in p["name"].lower()
    ]

    if not filtered_products:
        st.info("لا توجد منتجات مطابقة حالياً.")
    else:
        cols = st.columns(3)
        for i, p in enumerate(filtered_products):
            with cols[i % 3]:
                try:
                    st.image(p["img"], use_container_width=True)
                except:
                    st.write("🚫 لا توجد صورة")
                st.markdown(f"### {p['name']}")
                st.write(p["desc"])
                st.write(f"💰 **السعر:** {p['price']} جنيه")

                qty = st.number_input(
                    f"الكمية - {p['name']}",
                    min_value=1,
                    max_value=20,
                    key=f"qty_{i}"
                )
                if st.button(f"🛒 أضف للسلة ({p['name']})", key=f"add_{i}"):
                    st.session_state.cart.append(
                        {"name": p["name"], "price": p["price"], "qty": qty}
                    )
                    st.success("تمت الإضافة للسلة ✅")

# ==========================
# سلة المشتريات
# ==========================
elif page == "سلة المشتريات":
    st.subheader("🧺 سلة المشتريات")

    if not st.session_state.cart:
        st.info("السلة فارغة 🛍️")
    else:
        total = sum(item["price"] * item["qty"] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"- {item['name']} × {item['qty']} — {item['price']*item['qty']} جنيه")

        st.write(f"### 💰 الإجمالي: {total} جنيه")
        st.divider()

        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")
        payment_method = st.selectbox("اختر وسيلة الدفع", ["الدفع عند الاستلام", "محاكاة دفع أونلاين"])

        if st.button("🧾 تأكيد الطلب"):
            if not name or not phone:
                st.error("❌ من فضلك أدخل بيانات العميل كاملة.")
            else:
                c.execute("""
                INSERT INTO orders (created_at, customer, phone, items, total, payment_method)
                VALUES (?,?,?,?,?,?)
                """, (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    name,
                    phone,
                    json.dumps(st.session_state.cart, ensure_ascii=False),
                    total,
                    payment_method
                ))
                conn.commit()
                st.success("✔ تم إرسال الطلب بنجاح!")
                st.session_state.cart.clear()

# ==========================
# لوحة التحكم (Admin)
# ==========================
elif page == "لوحة التحكم (Admin)":
    if not st.session_state.is_admin:
        st.error("هذه الصفحة متاحة للأدمن فقط ❌")
    else:
        st.subheader("🔧 إدارة المنتجات")
        tab1, tab2 = st.tabs(["➕ إضافة منتج", "🗂️ حذف/عرض المنتجات"])

        with tab1:
            n = st.text_input("اسم المنتج الجديد")
            p = st.number_input("السعر", min_value=1.0)
            d = st.text_area("الوصف")
            cat = st.text_input("الفئة")
            img = st.text_input("اسم الصورة (مثال: mask.jpg)")
            if st.button("حفظ المنتج"):
                c.execute(
                    "INSERT INTO products (name, price, img, desc, category) VALUES (?,?,?,?,?)",
                    (n, p, img, d, cat)
                )
                conn.commit()
                st.success("✔ تم إضافة المنتج بنجاح!")

        with tab2:
            products = get_products()
            for i, prod in enumerate(products):
                st.write(f"{i+1}. {prod['name']} - {prod['category']} - {prod['price']} جنيه")
            index_to_delete = st.number_input(
                "أدخل رقم المنتج للحذف",
                min_value=1,
                max_value=len(products),
                step=1
            )
            if st.button("🗑 حذف المنتج المحدد"):
                c.execute(
                    "DELETE FROM products WHERE rowid = ?",
                    (index_to_delete,)
                )
                conn.commit()
                st.success("🗑 تم حذف المنتج بنجاح!")

# ==========================
# عرض الطلبات (Admin)
# ==========================
elif page == "الطلبات (Admin)":
    if not st.session_state.is_admin:
        st.error("هذه الصفحة متاحة للأدمن فقط ❌")
    else:
        st.subheader("📦 جميع الطلبات")

        c.execute("SELECT * FROM orders ORDER BY id DESC")
        orders = c.fetchall()

        if not orders:
            st.info("لا توجد طلبات حتى الآن.")
        else:
            for o in orders:
                st.write(f"🔹 طلب رقم {o[0]} - {o[2]} - {o[1]} - {o[5]} جنيه")
                items = json.loads(o[4])
                for item in items:
                    st.write(f"    - {item['name']} × {item['qty']} — {item['price']*item['qty']} جنيه")
                st.write(f"طريقة الدفع: {o[6]}")
                st.divider()

