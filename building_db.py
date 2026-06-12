# -*- coding: utf-8 -*-
import sqlite3
import os
import hashlib

def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام SHA256"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def rebuild_official_database():
    db_name = "Engineering_Library.db"
    if os.path.exists(db_name):
        os.remove(db_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # --- إنشاء الجداول ---

    # جدول الوصول للطلاب (الاسم + الرقم الجامعي + كلمة مرور مدروسة)
    cursor.execute("""
        CREATE TABLE access_gate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # جدول المسؤولين (الدخول للوحة إدارة)
    cursor.execute("""
        CREATE TABLE admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            admin_password TEXT NOT NULL
        )
    """)

    # جدول المواد الدراسية (السنة + المادة)
    cursor.execute("""
        CREATE TABLE subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            academic_year TEXT NOT NULL,
            subject_name TEXT NOT NULL
        )
    """)

    # أرشيف المحاضرات (السنة + المادة + عنوان + رابط)
    cursor.execute("""
        CREATE TABLE university_archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            academic_year TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            lecture_title TEXT NOT NULL,
            file_url TEXT NOT NULL
        )
    """)

    # جدول الإعلانات العامة للكلية
    cursor.execute("""
        CREATE TABLE college_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_title TEXT NOT NULL,
            news_text TEXT NOT NULL,
            media_url TEXT,
            media_type TEXT,          -- video, pdf, image, etc.
            target_year TEXT          -- "السنة الأولى"، "السنة الثانية"...
        )
    """)

    # جدول النتائج الامتحانية (سنة + عنوان + PDF)
    cursor.execute("""
        CREATE TABLE exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            academic_year TEXT NOT NULL,
            result_title TEXT NOT NULL,
            pdf_url TEXT NOT NULL
        )
    """)

    # --- بيانات أولية لمسؤول وطالب خاص بك (حسب app.py الجديد) ---

    # كلمة مرور المسؤول (تُستخدم في app.py: يعرب ناصيف)
    admin_password = "admin2026"
    hashed_admin = hash_password(admin_password)

    cursor.execute(
        "INSERT INTO admins (full_name, admin_password) VALUES (?, ?)",
        ("يعرب ناصيف", hashed_admin)
    )

    # كلمة مرور الطالب (محمد عادل) – مثال فقط، يمكن تغييرها لاحقاً
    student_password = "0000"
    hashed_student = hash_password(student_password)

    cursor.execute(
        "INSERT INTO access_gate (full_name, serial_number, password) VALUES (?,?,?)",
        ("يعرب ناصيف", "841183", hashed_student)
    )

    # --- بيانات المواد الرسمية لكل سنوات الكلية ---

    data = [
        # السنة الأولى
        ('السنة الأولى', 'ميكانيك هندسي 1'),
        ('السنة الأولى', 'ميكانيك هندسي 2'),
        ('السنة الأولى', 'الرياضيات للمهندسين 1'),
        ('السنة الأولى', 'الرياضيات للمهندسين 2'),
        ('السنة الأولى', 'لغة انكليزية 1'),
        ('السنة الأولى', 'لغة انكليزية 2'),
        ('السنة الأولى', 'لغة عربية'),
        ('السنة الأولى', 'فيزياء للمهندسين'),
        ('السنة الأولى', 'كيمياء للمهندسين'),
        ('السنة الأولى', 'اسس معلوماتية'),
        ('السنة الأولى', 'برمجة وخوارزميات'),
        ('السنة الأولى', 'الهندسة الوصفية والرسم الهندسي'),
        ('السنة الأولى', 'تمثيل المنشأت المدنية'),

        # السنة الثانية
        ('السنة الثانية', 'مقاومة مواد 1'),
        ('السنة الثانية', 'مقاومة مواد 2'),
        ('السنة الثانية', 'ميكانيك سوائل'),
        ('السنة الثانية', 'هيدروليك'),
        ('السنة الثانية', 'انشاء مباني 1'),
        ('السنة الثانية', 'انشاء مباني 2'),
        ('السنة الثانية', 'لغة انكليزية 3'),
        ('السنة الثانية', 'لغة انكليزية 4'),
        ('السنة الثانية', 'مساحة 1'),
        ('السنة الثانية', 'مساحة 2'),
        ('السنة الثانية', 'الاحصاء والاحتمالات'),
        ('السنة الثانية', 'الجبر الخطي والمعادلات التفاضلية'),
        ('السنة الثانية', 'جيولوجيا هندسية'),
        ('السنة الثانية', 'مواد بناء واختباراتها'),

        # السنة الثالثة
        ('السنة الثالثة', 'ميكانيك انشاءات 1'),
        ('السنة الثالثة', 'ميكانيك انشاءات 2'),
        ('السنة الثالثة', 'خرسانة مسلحة 1'),
        ('السنة الثالثة', 'خرسانة مسلحة 2'),
        ('السنة الثالثة', 'ميكانيك تربة 1'),
        ('السنة الثالثة', 'ميكانيك تربة 2'),
        ('السنة الثالثة', 'تكنولوجيا مواد البناء'),
        ('السنة الثالثة', 'الهيدرولوجيا الهندسية'),
        ('السنة الثالثة', 'هندسة الري والصرف'),
        ('السنة الثالثة', 'هندسة الطرق'),
        ('السنة الثالثة', 'هندسة النقل والمرور'),
        ('السنة الثالثة', 'التجهيزات الفنية للمباني'),
        ('السنة الثالثة', 'المخلفات الصلبة ومعالجتها'),
        ('السنة الثالثة', 'الجيوديزيا 1'),

        # السنة الرابعة
        ('السنة الرابعة', 'ميكانيك انشاءات 3'),
        ('السنة الرابعة', 'هندسة اساسات 1'),
        ('السنة الرابعة', 'هندسة اساسات 2'),
        ('السنة الرابعة', 'شبكات مياه الشرب'),
        ('السنة الرابعة', 'هندسة السكك الحديدية'),
        ('السنة الرابعة', 'الخرسانة المسلحة 3'),
        ('السنة الرابعة', 'ديناميك الانشاءات والهندسة الزلزالية'),
        ('السنة الرابعة', 'شبكات مياه الصرف الصحي'),
        ('السنة الرابعة', 'المنشأت المعدنية 1'),
        ('السنة الرابعة', 'هندسة السدود'),
        ('السنة الرابعة', 'الجيوديزيا 2'),
        ('السنة الرابعة', 'تكنولوجيا التشييد 1'),
        ('السنة الرابعة', 'المنشأت المعدنية 2'),
        ('السنة الرابعة', 'المنشأت المائية'),

        # السنة الخامسة
        ('السنة الخامسة', 'الانفاق والمنشأت المطمورة'),
        ('السنة الخامسة', 'هندسة المرافئ'),
        ('السنة الخامسة', 'معالجة مياه الصرف الصحي'),
        ('السنة الخامسة', 'المنشأت الخرسانية الخاصة'),
        ('السنة الخامسة', 'هندسة المطارات'),
        ('السنة الخامسة', 'تنقية مياه الشرب'),
        ('السنة الخامسة', 'اقتصاد هندسي'),
        ('السنة الخامسة', 'تكنولوجيا التشييد 2'),
        ('السنة الخامسة', 'ادارة المشاريع الهندسية'),
        ('السنة الخامسة', 'تصميم بمعونة الحاسب'),
        ('السنة الخامسة', 'المنشأت المختلطة'),
    ]

    cursor.executemany("INSERT INTO subjects (academic_year, subject_name) VALUES (?, ?)", data)

    conn.commit()
    conn.close()
    print("✅ تم بناء القاعدة وتعبئة 66 مادة بنجاح!")
    print("🔑 كلمات المرور مُشفّرة (SHA256) للمسؤول والطلاب.")


if __name__ == "__main__":
    rebuild_official_database()