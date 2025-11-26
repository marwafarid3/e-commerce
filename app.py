import streamlit as st

# إعداد الصفحة
st.set_page_config(page_title="متجر المستلزمات الطبية", page_icon="💊", layout="wide")

st.title("💊 متجر المستلزمات الطبية")
st.write("مرحبًا بك في متجرنا! نوفر جميع الأدوات والمستلزمات الطبية بأفضل الأسعار 💉🩺")

# المنتجات (أمثلة)
products = [
    {"name": "كمامة طبية", "price": 2.5, "img": "mask.jpg", "desc": "كمامة واقية ثلاثية الطبقات."},
    {"name": "قفازات طبية", "price": 5.0, "img": "gloves.jpg", "desc": "قفازات لاتكس معقمة للاستعمال الواحد."},
    {"name": "جهاز قياس ضغط الدم", "price": 350, "img": "blood_pressure.jpg", "desc": "جهاز رقمي لقياس ضغط الدم بدقة."},
    {"name": "ميزان حرارة إلكتروني", "price": 75, "img": "thermometer.jpg", "desc": "ميزان حرارة رقمي سريع القراءة."},
    {"name": "مطهر يدين", "price": 25, "img": "sanitizer.jpg", "desc": "مطهر كحولي بنسبة 70% للقضاء على الجراثيم."},
    {"name": "كرسي متحرك", "price": 1450, "img": "wheelchair.jpg", "desc": "كرسي متين وخفيف الوزن قابل للطي."},
]

# حالة السلة
if "cart" not in st.session_state:
    st.session_state.cart = []

# عرض المنتجات في شبكة
cols = st.columns(3)

for i, product in enumerate(products):
    with cols[i % 3]:
        st.image(product["img"], use_container_width=True)
        st.markdown(f"### {product['name']}")
        st.write(product["desc"])
        st.write(f"💰 **السعر:** {product['price']} جنيه")
        if st.button(f"🛒 أضف {product['name']}", key=product["name"]):
            st.session_state.cart.append(product)
            st.success(f"تمت إضافة {product['name']} إلى السلة ✅")

st.divider()
st.subheader("🧺 سلة المشتريات")

if st.session_state.cart:
    total = 0
    for item in st.session_state.cart:
        st.write(f"- {item['name']} ({item['price']} جنيه)")
        total += item["price"]
    st.write(f"### الإجمالي: 💰 {total} جنيه")

    if st.button("🧾 إنهاء الطلب"):
        st.success("تم إرسال طلبك بنجاح! سنتواصل معك قريبًا 📞")
        st.session_state.cart = []  # إفراغ السلة بعد الطلب
else:
    st.info("السلة فارغة حاليًا 🛍️")
