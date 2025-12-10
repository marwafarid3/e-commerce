import streamlit as st
from datetime import datetime

# ==========================
# إعداد الصفحة
# ==========================
st.set_page_config(page_title="متجر المستلزمات الطبية", page_icon="💊", layout="wide")

# ==========================
# بيانات المنتجات (مخزنة في الذاكرة)
# ==========================
# كل صورة موجودة بجانب ملف البايثون
products = [
    {"name": "كمامة طبية", "price": 2.5, "img": "mask.jpg", "desc": "كمامة واقية ثلاثية الطبقات.", "category": "كمامات"},
    {"name": "قفازات طبية", "price": 5.0, "img": "gloves.jpg", "desc": "قفازات لاتكس معقمة للاستعمال الواحد.", "category": "قفازات"},
    {"name": "جهاز قياس ضغط الدم", "price": 350, "img": "blood_pressure.jpg", "desc": "جهاز رقمي لقياس ضغط الدم بدقة.", "category": "أجهزة"},
    {"name": "ميزان حرارة إلكتروني", "price": 75, "img": "thermometer.jpg", "desc": "ميزان حرارة رقمي سريع القراءة.", "category": "أجهزة"},
    {"name": "مطهر يدين", "price": 25, "img": "sanitizer.jpg", "desc": "مطهر كحولي بنسبة 70%.", "category": "مطهرات"},
    {"name": "كرسي متحرك", "price": 1450, "img": "wheelchair.jpg", "desc": "كرسي متين وخفيف الوزن قابل للطي.", "category": "أجهزة"},
]

# ==========================
# حالة الجلسة
# ==========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "orders" not in st.session_state:
    st.session_state.orders = []

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
    admin_user = st.sidebar.text_input("اسم المستخدم", key="admin_user")
    admin_pass = st.sidebar.text_input("كلمة المرور", type="password", key="admin_pass")
    CORRECT_USER = "admin"
    CORRECT_PASS = "1234"
    if st.sidebar.button("تسجيل دخول"):
        if admin_user == CORRECT_USER and admin_pass == CORRECT_PASS:
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

    # فلترة حسب الفئة
    categories = ["الكل"] + sorted(list({p["category"] for p in products}))
    category_filter = st.selectbox("فئة المنتج", categories)
    
    # شريط بحث
    search_text = st.text_input("🔍 ابحث عن منتج")

    filtered_products = []
    for p in products:
        if (category_filter == "الكل" or p["category"] == category_filter) and (search_text.lower() in p["name"].lower()):
            filtered_products.append(p)

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

                qty = st.number_input(f"الكمية - {p['name']}", min_value=1, max_value=20, key=f"qty_{i}")
                if st.button(f"🛒 أضف للسلة ({p['name']})", key=f"add_{i}"):
                    st.session_state.cart.append({"name": p["name"], "price": p["price"], "qty": qty})
                    st.success("تمت الإضافة للسلة ✅")

# ==========================
# صفحة سلة المشتريات
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
        st.subheader("📞 بيانات العميل")
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")

        payment_method = st.selectbox("اختر وسيلة الدفع", ["الدفع عند الاستلام", "محاكاة دفع أونلاين"])
        if payment_method == "محاكاة دفع أونلاين":
            st.info("💳 سيتم تحويلك لصفحة الدفع (محاكاة).")
        else:
            st.info("💵 سيتم الدفع نقدًا عند الاستلام.")

        if st.button("🧾 تأكيد الطلب"):
            if name == "" or phone == "":
                st.error("❌ من فضلك أدخل بيانات العميل كاملة.")
            else:
                order = {
                    "id": len(st.session_state.orders)+1,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "customer": name,
                    "phone": phone,
                    "items": st.session_state.cart.copy(),
                    "total": total,
                    "payment_method": payment_method
                }
                st.session_state.orders.append(order)
                st.success(f"✔ تم إرسال الطلب بنجاح! رقم الطلب: {order['id']}")
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
        
        # إضافة منتج
        with tab1:
            st.write("أدخل بيانات المنتج الجديد")
            n = st.text_input("اسم المنتج الجديد")
            p = st.number_input("السعر", min_value=1.0, step=1.0)
            d = st.text_area("الوصف")
            cat = st.text_input("الفئة")
            uploaded_file = st.file_uploader("اختر صورة", type=["jpg","jpeg","png"])
            if st.button("حفظ المنتج"):
                img_path = uploaded_file.name if uploaded_file else ""
                products.append({"name": n, "price": p, "img": img_path, "desc": d, "category": cat})
                st.success("✔ تم إضافة المنتج بنجاح!")

        # حذف وعرض المنتجات
        with tab2:
            st.write("📋 قائمة المنتجات الحالية")
            for i, prod in enumerate(products):
                st.write(f"{i+1}. {prod['name']} - {prod['category']} - {prod['price']} جنيه")
            index_to_delete = st.number_input("أدخل رقم المنتج للحذف", min_value=1, max_value=len(products), step=1)
            if st.button("🗑 حذف المنتج المحدد"):
                products.pop(index_to_delete-1)
                st.success("🗑 تم حذف المنتج بنجاح!")

# ==========================
# عرض الطلبات (Admin)
# ==========================
elif page == "الطلبات (Admin)":
    if not st.session_state.is_admin:
        st.error("هذه الصفحة متاحة للأدمن فقط ❌")
    else:
        st.subheader("📦 جميع الطلبات")
        if not st.session_state.orders:
            st.info("لا توجد طلبات حتى الآن.")
        else:
            for order in st.session_state.orders:
                st.write(f"🔹 طلب رقم {order['id']} - {order['customer']} - {order['created_at']} - {order['total']} جنيه")
                for item in order["items"]:
                    st.write(f"    - {item['name']} × {item['qty']} — {item['price']*item['qty']} جنيه")
                st.write(f"طريقة الدفع: {order['payment_method']}")
                st.divider()
