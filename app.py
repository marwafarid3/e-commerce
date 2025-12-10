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
DEFAULT_IMG = "default.jpg"  # صورة افتراضية لو الصورة مش موجودة

# ================================
# إنشاء ملفات البيانات لو مش موجودة
# ================================
if not os.path.exists(PRODUCTS_FILE):
    df = pd.DataFrame([
        {"name": "كمامة طبية", "category": "كمامات", "price": 2.5, "img": "mask.jpg", "desc": "كمامة واقية ثلاثية الطبقات."},
        {"name": "قفازات طبية", "category": "معدات", "price": 5.0, "img": "gloves.jpg", "desc": "قفازات لاتكس معقمة للاستعمال الواحد."},
        {"name": "جهاز قياس ضغط الدم", "category": "أجهزة", "price": 350, "img": "blood_pressure.jpg", "desc": "جهاز رقمي لقياس ضغط الدم بدقة."},
        {"name": "ميزان حرارة إلكتروني", "category": "أجهزة", "price": 75, "img": "thermometer.jpg", "desc": "ميزان حرارة رقمي سريع القراءة."},
        {"name": "مطهر يدين", "category": "معدات", "price": 25, "img": "sanitizer.jpg", "desc": "مطهر كحولي بنسبة 70%."},
        {"name": "كرسي متحرك", "category": "معدات", "price": 1450, "img": "wheelchair.jpg", "desc": "كرسي متين وخفيف الوزن قابل للطي."},
    ])
    df.to_csv(PRODUCTS_FILE, index=False)

if not os.path.exists(ORDERS_FILE):
    pd.DataFrame(columns=["id","created_at","customer","phone","items","total","payment_method","payment_status"]).to_csv(ORDERS_FILE, index=False)

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
page = st.sidebar.selectbox("انتقل إلى:", ["المتجر","سلة المشتريات","لوحة التحكم (Admin)","الطلبات (Admin)"])

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

st.title("💊 متجر المستلزمات الطبية")

# ================================
# 📌 صفحة المتجر
# ================================
if page == "المتجر":
    st.subheader("🛍️ المنتجات المتاحة")

    # فلترة وبحث
    search = st.text_input("🔍 ابحث عن منتج بالاسم")
    category_filter = st.selectbox("فئة المنتج", ["الكل"] + products_df["category"].unique().tolist())

    filtered_df = products_df.copy()
    if search:
        filtered_df = filtered_df[filtered_df["name"].str.contains(search, case=False)]
    if category_filter != "الكل":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    if filtered_df.empty:
        st.info("لا توجد منتجات حالياً.")
    else:
        cols = st.columns(3)
        for i, row in filtered_df.iterrows():
            with cols[i % 3]:
                img_path = row["img"] if os.path.exists(row["img"]) else DEFAULT_IMG
                st.image(img_path, use_container_width=True)
                st.markdown(f"### {row['name']}")
                st.write(row["desc"])
                st.write(f"💰 **السعر:** {row['price']} جنيه")

                qty = st.number_input(f"الكمية - {row['name']}", min_value=1, max_value=20, key=f"qty_{i}")
                if st.button(f"🛒 أضف للسلة ({row['name']})", key=f"add_{i}"):
                    st.session_state.cart.append({"name": row["name"],"price": float(row["price"]),"qty": int(qty)})
                    st.success("تمت الإضافة للسلة ✅")

# ================================
# 🧺 صفحة السلة
# ================================
elif page == "سلة المشتريات":
    st.subheader("🧺 سلة المشتريات")
    if not st.session_state.cart:
        st.info("السلة فارغة 🛍️")
    else:
        total = sum(item["price"]*item["qty"] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"- {item['name']} × {item['qty']} — {item['price']*item['qty']} جنيه")
        st.write(f"### 💰 الإجمالي: {total} جنيه")

        st.subheader("📞 بيانات العميل")
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")

        st.subheader("💳 الدفع الإلكتروني")
        payment_method = st.selectbox("اختر وسيلة الدفع", ["الدفع عند الاستلام", "Stripe (محاكاة)", "Paymob (محاكاة)"])
        if payment_method != "الدفع عند الاستلام":
            st.info("⚠ هذه محاكاة للدفع الإلكتروني فقط")

        if st.button("🧾 تأكيد الطلب"):
            if not name or not phone:
                st.error("❌ من فضلك أدخل بيانات العميل كاملة.")
            else:
                orders_df = pd.read_csv(ORDERS_FILE)
                order_id = len(orders_df)+1
                payment_status = "COD - Pending" if payment_method=="الدفع عند الاستلام" else "Online - Pending"
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
                st.success(f"✔ تم إرسال الطلب بنجاح! رقم الطلب: {order_id}")
                st.session_state.cart = []

# ================================
# 🔧 لوحة التحكم - Admin
# ================================
elif page == "لوحة التحكم (Admin)":
    if not st.session_state.is_admin:
        st.error("هذه الصفحة للأدمن فقط ❌")
    else:
        st.subheader("🔧 إدارة المنتجات")
        tab1, tab2 = st.tabs(["➕ إضافة منتج", "🗂️ تعديل/حذف المنتجات"])

        # -------- إضافة منتج جديد --------
        with tab1:
            st.write("أدخل بيانات المنتج الجديد")
            n = st.text_input("اسم المنتج")
            cat = st.text_input("الفئة")
            p = st.number_input("السعر", min_value=1.0, step=1.0)
            d = st.text_area("الوصف")
            uploaded_file = st.file_uploader("اختر صورة", type=["jpg","jpeg","png"])
            img_path = ""
            if st.button("حفظ المنتج"):
                if uploaded_file is not None:
                    img_path = uploaded_file.name
                    with open(img_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                new_row = pd.DataFrame([{"name": n,"category": cat,"price": p,"desc": d,"img": img_path}])
                df = pd.read_csv(PRODUCTS_FILE)
                df = pd.concat([df,new_row], ignore_index=True)
                df.to_csv(PRODUCTS_FILE, index=False)
                st.success("✔ تم إضافة المنتج!")

        # -------- تعديل/حذف المنتجات --------
        with tab2:
            df = pd.read_csv(PRODUCTS_FILE)
            st.write("📋 قائمة المنتجات الحالية")
            st.dataframe(df)
            product_to_delete = st.selectbox("اختر المنتج للحذف", df["name"])
            if st.button("🗑 حذف المنتج"):
                df = df[df["name"] != product_to_delete]
                df.to_csv(PRODUCTS_FILE, index=False)
                st.success("🗑 تم الحذف!")

# ================================
# 📦 صفحة الطلبات - Admin
# ================================
elif page == "الطلبات (Admin)":
    if not st.session_state.is_admin:
        st.error("هذه الصفحة للأدمن فقط ❌")
    else:
        st.subheader("📦 جميع الطلبات")
        if not os.path.exists(ORDERS_FILE):
            st.info("لا توجد طلبات")
        else:
            orders_df = pd.read_csv(ORDERS_FILE)
            if orders_df.empty:
                st.info("لا توجد طلبات")
            else:
                st.dataframe(orders_df)
                st.download_button(
                    label="⬇️ تحميل الطلبات كملف CSV",
                    data=orders_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="orders_export.csv",
                    mime="text/csv"
                )
