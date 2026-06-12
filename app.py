# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import hashlib
import os

# --- 1. الإعدادات العامة والهوية ---
st.set_page_config(
    page_title="كلية الهندسة المدنية | Civil Engineering Hub",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# تنسيق CSS احترافي
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 5em;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        transition: 0.3s;
        margin-bottom: 10px;
    }

    .stButton > button:hover {
        transform: translateY(-5px);
        background-color: #E94560;
        color: white;
    }

    .secret-btn { opacity: 0.1; }
    .secret-btn:hover { opacity: 1; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك قاعدة البيانات ---
def get_db():
    conn = sqlite3.connect("Engineering_Library.db")
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash

# --- 3. إدارة حالة التطبيق (الـ Session State) ---
keys = [
    'step',         # welcome, login, password, dashboard, admin_welcome, admin_panel
    'user_data',    # بيانات الطالب
    'logged_in',    # تم تسجيل الدخول
    'is_admin_login',
    'admin_auth',
    'page',         # news, year_news, calcs, results, lectures
    'search_query',
    'user_year',    # السنة الدراسية للطالب (مختارة)
]
for key in keys:
    if key not in st.session_state:
        if "auth" in key or "admin" in key:
            st.session_state[key] = False
        elif key == "step":
            st.session_state[key] = "welcome"
        elif key == "logged_in":
            st.session_state[key] = False
        elif key == "search_query":
            st.session_state[key] = ""
        elif key == "user_year":
            st.session_state[key] = "السنة الأولى"
        else:
            st.session_state[key] = None

# --- 4. الشريط الجانبي (الدعم الفني + زر لوحة الإدارة) ---
with st.sidebar:
    st.title("📘 كلية الهندسة المدنية")

    # زر الإدارة
    if st.button("🔐 إدارة", help="لوحة تحكم المسؤول"):
        st.session_state.step = "admin_welcome"
        st.session_state.admin_auth = False
        st.session_state.is_admin_login = True
        st.rerun()

    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_column_width=True)

    st.divider()
    st.markdown("### 📞 الدعم الفني")
    st.write("🟢 **واتساب**:")
    st.code("0992325041")
    st.link_button("فتح واتساب", "https://wa.me/963992325041", use_container_width=True)

    st.write("💬 **تليجرام**:")
    st.code("@AMS0012")
    st.link_button("فتح تليجرام", "https://t.me/AMS0012", use_container_width=True)

# --- 5. تحقق المسؤول (admin_welcome) ---
if st.session_state.step == "admin_welcome" and not st.session_state.admin_auth:
    st.title("🔐 تحقق المسؤول")

    a_name = st.text_input("الاسم الثلاثي للمسؤول")
    a_pass = st.text_input("كلمة مرور المسؤول", type="password")

    if st.button("دخول للوحة التحكم"):
        if a_name and a_pass:
            db = get_db()
            admin = db.execute(
                "SELECT * FROM admins WHERE full_name = ? AND admin_password = ?",
                (a_name, hash_password(a_pass))
            ).fetchone()
            db.close()
            if admin:
                st.session_state.admin_auth = True
                st.session_state.step = "admin_panel"
                st.rerun()
            else:
                st.error("❌ بيانات غير مصرح بها.")
        else:
            st.warning("⚠️ يرجى تعبئة الاسم وكلمة المرور.")

    if st.button("رجوع"):
        st.session_state.step = "welcome"
        st.rerun()

# --- 6. لوحة إدارة المسؤول (admin_panel) ---
elif st.session_state.step == "admin_panel" and st.session_state.admin_auth:
    st.title("🛡️ لوحة إدارة كلية الهندسة المدنية")

    if st.button("⬅️ تسجيل خروج المسؤول"):
        st.session_state.admin_auth = False
        st.session_state.step = "welcome"
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["👥 الطلاب", "📚 المحاضرات", "📢 الإعلانات", "📊 النتائج"]
    )

    # 6.1 تبويب: الطلاب
    with tab1:
        st.subheader("👥 إضافة طالب جديد")
        n_name = st.text_input("الاسم الثلاثي")
        n_serial = st.text_input("الرقم الجامعي")
        n_pass = st.text_input("كلمة المرور", type="password")

        if st.button("حفظ الطالب"):
            if n_name.strip() == "" or n_serial.strip() == "" or n_pass.strip() == "":
                st.warning("⚠️ يرجى تعبئة جميع الحقول.")
            else:
                db = get_db()
                res = db.execute(
                    "SELECT COUNT(*) as cnt FROM access_gate WHERE serial_number = ?",
                    (n_serial,)
                ).fetchone()
                if res["cnt"] > 0:
                    st.warning("⚠️ الرقم الجامعي موجود مسبقًا.")
                else:
                    hashed = hash_password(n_pass)
                    db.execute(
                        "INSERT INTO access_gate (full_name, serial_number, password) VALUES (?, ?, ?)",
                        (n_name, n_serial, hashed)
                    )
                    db.commit()
                    db.close()
                    st.success("✅ تم حفظ الطالب بنجاح.")

    # 6.2 تبويب: المحاضرات
    with tab2:
        st.subheader("📚 إضافة محاضرة جديدة")
        years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
        sel_y = st.selectbox("اختر السنة", years)
        subjects = db.execute("SELECT DISTINCT subject_name FROM subjects WHERE academic_year = ?", (sel_y,)).fetchall()
        sel_sub = st.selectbox("اختر المادة", [s["subject_name"] for s in subjects])
        lec_title = st.text_input("عنوان المحاضرة")
        lec_url = st.text_input("رابط ملف المحاضرة (Google Drive)")

        if st.button("إضافة المحاضرة"):
            if sel_y and sel_sub and lec_title and lec_url:
                db = get_db()
                db.execute(
                    "INSERT INTO university_archive (academic_year, subject_name, lecture_title, file_url) VALUES (?, ?, ?, ?)",
                    (sel_y, sel_sub, lec_title, lec_url)
                )
                db.commit()
                db.close()
                st.success("✅ تم إضافة المحاضرة.")
            else:
                st.error("❌ يرجى تعبئة جميع الحقول.")

    # 6.3 تبويب: الإعلانات
    with tab3:
        st.subheader("📢 إضافة إعلان جديد")
        n_title = st.text_input("عنوان الإعلان")
        n_text = st.text_area("نص الإعلان")
        n_media = st.text_input("رابط الوسائط (صورة/فيديو/PDF)")
        n_type = st.selectbox("نوع الوسائط", ["image", "video", "pdf", "other"])
        n_target = st.selectbox("السنة المستهدفة", [
            "السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة", "الجميع"
        ])

        if st.button("حفظ الإعلان"):
            if n_title and n_text:
                db = get_db()
                db.execute(
                    "INSERT INTO college_news (news_title, news_text, media_url, media_type, target_year) VALUES (?, ?, ?, ?, ?)",
                    (n_title, n_text, n_media, n_type, None if n_target == "الجميع" else n_target)
                )
                db.commit()
                db.close()
                st.success("✅ تم حفظ الإعلان.")
            else:
                st.error("❌ يرجى تعبئة العنوان ونص الإعلان.")

    # 6.4 تبويب: النتائج الامتحانية
    with tab4:
        st.subheader("📊 إضافة نتيجة امتحانية")
        r_years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
        r_year = st.selectbox("اختر السنة الدراسية", r_years)
        r_title = st.text_input("عنوان النتيجة")
        r_pdf = st.text_input("رابط PDF النتيجة")

        if st.button("حفظ النتيجة"):
            if r_year and r_title and r_pdf:
                db = get_db()
                db.execute(
                    "INSERT INTO exam_results (academic_year, result_title, pdf_url) VALUES (?, ?, ?)",
                    (r_year, r_title, r_pdf)
                )
                db.commit()
                db.close()
                st.success("✅ تم حفظ النتيجة.")
            else:
                st.error("❌ يرجى تعبئة جميع الحقول.")

# --- 7. صفحة الترحيب (welcome) ---
if st.session_state.step == "welcome" and not st.session_state.logged_in:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_column_width=True)
    st.title("🏛️ كلية الهندسة المدنية")
    st.subheader("منصة المكتبة الرقمية والنتائج الامتحانية")
    st.write("أداة متكاملة لطلاب كلية الهندسة المدنية لتسهيل الوصول إلى المحاضرات، النتائج، والإعلانات.")
    st.divider()
    if st.button("🔑 دخول الطلاب", type="primary", use_container_width=True):
        st.session_state.step = "login"
        st.rerun()

# --- 8. صفحة تسجيل الدخول (login) ---
elif st.session_state.step == "login" and not st.session_state.logged_in:
    st.title("🔑 تسجيل الدخول للطلاب")

    if st.button("← الرجوع"):
        st.session_state.step = "welcome"
        st.session_state.user_data = None
        st.rerun()

    st.write("أدخل معلوماتك للوصول إلى حسابك:")

    u_name = st.text_input("الاسم الثلاثي")
    u_serial = st.text_input("الرقم الجامعي")

    if st.button("التحقق من البيانات"):
        if u_name.strip() == "" or u_serial.strip() == "":
            st.warning("⚠️ يرجى تعبئة الاسم والرقم الجامعي.")
        else:
            db = get_db()
            user = db.execute(
                "SELECT * FROM access_gate WHERE full_name = ? AND serial_number = ?",
                (u_name, u_serial)
            ).fetchone()
            db.close()
            if user:
                st.session_state.user_data = user
                st.session_state.step = "password"
                st.rerun()
            else:
                st.error("البيانات غير مسجلة في النظام.")

# --- 9. صفحة إدخال كلمة المرور (password) ---
elif st.session_state.step == "password" and not st.session_state.logged_in:
    user = st.session_state.user_data
    f_name = user["full_name"].split()[0]

    st.title(f"🔐 مهندس {f_name}")
    st.write("أدخل كلمة مرور حسابك للوصول إلى لوحة التحكم الخاصة بك:")

    u_pass = st.text_input("كلمة المرور", type="password")

    if st.button("تأكيد دخول آمن"):
        if user and verify_password(u_pass, user["password"]):
            st.session_state.logged_in = True
            st.session_state.step = "dashboard"
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة. حاول مرة أخرى.")

    if st.button("← العودة"):
        st.session_state.step = "login"
        st.session_state.user_data = None
        st.rerun()

# --- 10. لوحة تحكم الطالب (dashboard) ---
elif st.session_state.logged_in and st.session_state.step == "dashboard":
    user = st.session_state.user_data
    f_name = user["full_name"].split()[0]

    st.title(f"مرحباً مهندس {f_name} 👌")
    st.subheader("المنصة الأكاديمية لكلية الهندسة المدنية")
    st.divider()

    # شريط البحث
    search_query = st.text_input("🔍 ابحث عن محاضرة أو مادة...", value=st.session_state.search_query)
    st.session_state.search_query = search_query

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📢 الإعلانات العامة"):
            st.session_state.page = "news"
            st.rerun()
        if st.button("📅 إعلانات السنوات"):
            st.session_state.page = "year_news"
            st.rerun()
        if st.button("🧮 الحاسبات الهندسية"):
            st.session_state.page = "calcs"
            st.rerun()

    with col2:
        if st.button("📊 النتائج الامتحانية"):
            st.session_state.page = "results"
            st.rerun()
        if st.button("📚 المحاضرات"):
            st.session_state.page = "lectures"
            st.rerun()
        if st.button("🚪 الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.step = "welcome"
            st.session_state.search_query = ""
            st.session_state.page = None
            st.session_state.user_year = None
            st.rerun()

    # --- صفحة: المحاضرات ---
    if st.session_state.page == "lectures":
        st.subheader("📚 محاضرات السنة الدراسية")

        year = st.selectbox(
            "اختر السنة الدراسية",
            ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"],
            key="lectures_year"
        )
        db = get_db()
        subjects = db.execute(
            "SELECT DISTINCT subject_name FROM subjects WHERE academic_year = ?",
            (year,)
        ).fetchall()
        db.close()

        if not subjects:
            st.info("لا توجد مواد مسجلة لهذه السنة بعد.")
        else:
            sel_sub = st.selectbox(
                "اختر المادة",
                [s["subject_name"] for s in subjects],
                key="lectures_subject"
            )
            query = f"SELECT * FROM university_archive WHERE academic_year = ? AND subject_name = ?"
            params = [year, sel_sub]

            if search_query.strip():
                query += " AND lecture_title LIKE ?"
                params.append(f"%{search_query}%")

            db = get_db()
            lecs = db.execute(query, params).fetchall()
            db.close()

            if lecs:
                for l in lecs:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"📄 {l['lecture_title']}")
                    c2.link_button("فتح الملف", l["file_url"])
            else:
                st.info("لا توجد محاضرات مطابقة للبحث في هذه المادة والسنة.")

    # --- صفحة: النتائج الامتحانية ---
    elif st.session_state.page == "results":
        st.subheader("📊 النتائج الامتحانية")

        db = get_db()
        years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
        sel_year = st.selectbox("اختر السنة الدراسية", years)

        results = db.execute(
            "SELECT * FROM exam_results WHERE academic_year = ? ORDER BY id DESC",
            (sel_year,)
        ).fetchall()
        db.close()

        if results:
            for res in results:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📖 {res['result_title']}")
                c2.link_button("فتح PDF", res["pdf_url"])
        else:
            st.info("لا توجد نتائج مدخلة لهذه السنة بعد.")

    # --- صفحة: الإعلانات العامة ---
elif st.session_state.page == "news":
    st.subheader("📢 الإعلانات العامة")

    db = get_db()
    news = db.execute(
        "SELECT * FROM college_news ORDER BY id DESC LIMIT 10"
    ).fetchall()
    db.close()

    if not news:
        st.info("لا توجد إعلانات حديثة في الوقت الحالي.")
    else:
        for n in news:
            st.divider()
            st.markdown(f"### {n['news_title']}")
            st.write(n['news_text'])
            if n['media_url']:
                st.markdown(f"[وسائط]({n['media_url']})")
            "SELECT"