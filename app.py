import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================================
# إعداد عام
# ================================
st.set_page_config(page_title="متجر المستلزمات الطبية", page_icon="💊", layout="wide")

PRODUCTS_FILE = "products.csv"
ORDERS_FILE = "orders.csv"
IMAGES_DIR = "product_images"

# إنشاء مجلد الصور لو مش موجود
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# ================================
# إنشاء ملفات البيانات لو مش موجودة
# ================================
if not os.path.exists(PRODUCTS_FILE):
    df = pd.DataFrame([
    {"name": "كمامة طبية", "price": 2.5, "img": "mask.jpg", "desc": "كمامة واقية ثلاثية الطبقات."},
    {"name": "قفازات طبية", "price": 5.0, "img": "gloves.jpg", "desc": "قفازات لاتكس معقمة للاستعمال الواحد."},
    {"name": "جهاز قياس ضغط الدم", "price": 350, "img": "blood_pressure.jpg", "desc": "جهاز رقمي لقياس ضغط الدم بدقة."},
    {"name": "ميزان حرارة إلكتروني", "price": 75, "img": "thermometer.jpg", "desc": "ميزان حرارة رقمي سريع القراءة."},
    {"name": "مطهر يدين", "price": 25, "img": "sanitizer.jpg", "desc": "مطهر كحولي بنسبة 70%."},
    {"name": "كرسي متحرك", "price": 1450, "img": "wheelchair.jpg", "desc": "كرسي متين وخفيف الوزن قابل للطي."},
])
    df.to_csv(PRODUCTS_FILE, index=False)

if not os.path.exists(ORDERS_FILE):
    pd.DataFrame(columns=["id", "created_at", "customer", "phone", "items", "total", "payment_method", "payment_status"]).to_csv(ORDERS_FILE, index=False)

# ================================
# تحميل البيانات
# ================================
products_df = pd.read_csv(PRODUCTS_FILE)

# ================================
# حالة الجلسة
# ================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ================================
# شريط جانبي
# ================================
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
    # تقدر تغيّرهم هنا
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

st.title("💊 متجر المستلزمات الطبية")

# ================================
# 📌 صفحة المتجر
# ================================
if page == "المتجر":
    st.subheader("🛍️ المنتجات المتاحة")

    if products_df.empty:
        st.info("لا توجد منتجات حالياً، أضف منتجات من لوحة التحكم.")
    else:
        cols = st.columns(3)

        for i, row in products_df.iterrows():
            with cols[i % 3]:
                # محاولة عرض الصورة
                if isinstance(row["img"], str) and os.path.exists(row["img"]):
                    st.image(row["img"], use_container_width=True)
                else:
                    st.write("🚫 لا توجد صورة")

                st.markdown(f"### {row['name']}")
                st.write(row["desc"])
                st.write(f"💰 **السعر:** {row['price']} جنيه")

                qty = st.number_input(
                    f"الكمية - {row['name']}",
                    min_value=1,
                    max_value=20,
                    key=f"qty_{i}"
                )

                if st.button(f"🛒 أضف للسلة ({row['name']})", key=f"add_{i}"):
                    st.session_state.cart.append({
                        "name": row["name"],
                        "price": float(row["price"]),
                        "qty": int(qty)
                    })
                    st.success("تمت الإضافة للسلة بنجاح ✅")

# ================================
# 🧺 صفحة السلة
# ================================
elif page == "سلة المشتريات":
    st.subheader("🧺 سلة المشتريات")

    if not st.session_state.cart:
        st.info("السلة فارغة حالياً 🛍️")
    else:
        total = 0

        for item in st.session_state.cart:
            st.write(f"- {item['name']} × {item['qty']} — {item['price'] * item['qty']} جنيه")
            total += item["price"] * item["qty"]

        st.write(f"### 💰 الإجمالي: {total} جنيه")

        st.divider()
        st.subheader("📞 بيانات العميل")

        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")

        st.subheader("💳 الدفع الإلكتروني")

        payment_method = st.selectbox(
            "اختر وسيلة الدفع",
            ["Stripe (Visa/Master)", "Paymob (بطاقات/محافظ)", "الدفع عند الاستلام"]
        )

        # شرح بسيط / Placeholder للـ Payment Gateway
        if payment_method == "Stripe (Visa/Master)":
            st.info("سيتم تحويلك لصفحة دفع Stripe (تحتاج إضافة رابط الـ Checkout بعد إعداد API).")
        elif payment_method == "Paymob (بطاقات/محافظ)":
            st.info("سيتم إنشاء رابط دفع من Paymob (يتطلب إعداد Integration و API Keys).")
        else:
            st.info("سيتم الدفع نقدًا عند الاستلام 💵.")

        if st.button("🧾 تأكيد الطلب"):
            if name == "" or phone == "":
                st.error("❌ من فضلك أدخل بيانات العميل كاملة.")
            else:
                # حالة الدفع
                if payment_method == "الدفع عند الاستلام":
                    payment_status = "COD - Pending"
                else:
                    # في الواقع هنا المفروض تستدعي API وترجع حالة الدفع
                    payment_status = "Online - Pending (محاكاة)"

                orders_df = pd.read_csv(ORDERS_FILE)
                order_id = len(orders_df) + 1

                new_order = {
                    "id": order_id,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "customer": name,
                    "phone": phone,
                    "items": str(st.session_state.cart),
                    "total": total,
                    "payment_method": payment_method,
                    "payment_status": payment_status
                }

                orders_df = pd.concat([orders_df, pd.DataFrame([new_order])], ignore_index=True)
                orders_df.to_csv(ORDERS_FILE, index=False)

                st.success(f"✔ تم إرسال طلبك بنجاح! رقم الطلب: {order_id}")
                st.session_state.cart = []

# ================================
# 🔧 لوحة التحكم — Admin Dashboard
# ================================
elif page == "لوحة التحكم (Admin)":
    if not st.session_state.is_admin:
        st.error("هذه الصفحة متاحة للأدمن فقط ❌")
    else:
        st.subheader("🔧 إدارة المنتجات")

        tab1, tab2 = st.tabs(["➕ إضافة منتج", "🗂️ حذف/عرض المنتجات"])

        # -------- إضافة منتج جديد --------
        with tab1:
            st.write("أدخل بيانات المنتج الجديد")

            n = st.text_input("اسم المنتج الجديد")
            p = st.number_input("السعر", min_value=1.0, step=1.0)
            d = st.text_area("الوصف")

            st.write("📷 رفع صورة المنتج:")
            uploaded_file = st.file_uploader("اختر صورة", type=["jpg", "jpeg", "png"])

            img_path = ""

            if st.button("حفظ المنتج"):
                if n == "" or p <= 0:
                    st.error("من فضلك أدخل اسم المنتج والسعر بشكل صحيح.")
                else:
                    # حفظ الصورة لو موجودة
                    if uploaded_file is not None:
                        img_filename = f"{IMAGES_DIR}/{uploaded_file.name}"
                        with open(img_filename, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        img_path = img_filename
                    else:
                        img_path = ""

                    new_row = pd.DataFrame([{
                        "name": n,
                        "price": p,
                        "desc": d,
                        "img": img_path
                    }])

                    df = pd.read_csv(PRODUCTS_FILE)
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(PRODUCTS_FILE, index=False)

                    st.success("✔ تم إضافة المنتج بنجاح!")

        # -------- حذف وعرض المنتجات --------
        with tab2:
            df = pd.read_csv(PRODUCTS_FILE)

            if df.empty:
                st.info("لا توجد منتجات لعرضها.")
            else:
                st.write("📋 قائمة المنتجات الحالية:")
                st.dataframe(df)

                product_to_delete = st.selectbox("اختر المنتج لحذفه", df["name"])

                if st.button("🗑 حذف المنتج المحدد"):
                    df = df[df["name"] != product_to_delete]
                    df.to_csv(PRODUCTS_FILE, index=False)
                    st.success("🗑 تم حذف المنتج بنجاح!")

# ================================
# 📦 صفحة عرض الطلبات (Admin)
# ================================
elif page == "الطلبات (Admin)":
    if not st.session_state.is_admin:
        st.error("هذه الصفحة متاحة للأدمن فقط ❌")
    else:
        st.subheader("📦 جميع الطلبات")

        if not os.path.exists(ORDERS_FILE):
            st.info("لا توجد طلبات حتى الآن.")
        else:
            orders_df = pd.read_csv(ORDERS_FILE)

            if orders_df.empty:
                st.info("لا توجد طلبات حتى الآن.")
            else:
                # فلترة بسيطة
                status_filter = st.selectbox(
                    "فلتر حسب حالة الدفع",
                    ["الكل", "COD - Pending", "Online - Pending (محاكاة)"]
                )

                if status_filter != "الكل":
                    filtered = orders_df[orders_df["payment_status"] == status_filter]
                else:
                    filtered = orders_df

                st.write("📋 قائمة الطلبات:")
                st.dataframe(filtered)

                st.download_button(
                    label="⬇️ تحميل الطلبات كملف CSV",
                    data=orders_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="orders_export.csv",
                    mime="text/csv"
                )

