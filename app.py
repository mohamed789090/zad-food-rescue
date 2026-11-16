import sqlite3
import random
import string
import os
import io
import csv
import math
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, Response
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "zad_food_rescue_high_end_secret_2026"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. جدول المستخدمين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL, -- 'customer', 'restaurant', 'charity', 'admin'
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. جدول الوجبات / فوائض الطعام
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL, -- 'مخبوزات', 'وجبات رئيسية', 'حلويات', 'خضار وفواكه', 'أخرى'
            original_price REAL NOT NULL,
            discounted_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            pickup_time TEXT NOT NULL,
            is_charity INTEGER DEFAULT 0, -- 0: بيع مخفض, 1: تبرع مجاني للجمعيات
            status TEXT DEFAULT 'available', -- 'available', 'sold_out'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (restaurant_id) REFERENCES users (id)
        )
    """)

    # 3. جدول الحجوزات والطلبات (مع دعم التوصيل والكميات المتعددة)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE NOT NULL,
            meal_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
            delivery_type TEXT DEFAULT 'pickup', -- 'pickup' or 'delivery'
            delivery_address TEXT,
            delivery_fee REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meal_id) REFERENCES meals (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()

    # تحديث أعمدة التوصيل تلقائياً في حال كانت الداتابيز موجودة مسبقاً
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN delivery_type TEXT DEFAULT 'pickup'")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN delivery_address TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN delivery_fee REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()

    # إنشاء مستخدمين افتراضيين للتجربة الفورية لو الجدول فاضي
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_demo_data(conn)

    conn.close()

def seed_demo_data(conn):
    cursor = conn.cursor()
    admin_pass = generate_password_hash("admin123")
    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, role, phone, address)
        VALUES ('admin', ?, 'إدارة منصة زاد', 'admin', '01000000000', 'المقر الرئيسي - الدقي')
    """, (admin_pass,))

    rest_pass = generate_password_hash("123456")
    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, role, phone, address)
        VALUES 
        ('bakery', ?, 'مخبز البركة الآلي', 'restaurant', '01112223344', 'الدقي - شارع التحرير'),
        ('restaurant1', ?, 'مطعم الواحة للمأكولات الشرقية', 'restaurant', '01223334455', 'مدينة نصر - الحي السابع'),
        ('pastry', ?, 'حلواني السعادة الملكي', 'restaurant', '01099887766', 'المعادي - شارع 9'),
        ('fresh_grill', ?, 'شواية الريف والمأكولات الطازجة', 'restaurant', '01011223344', 'مصر القديمة - الفسطاط')
    """, (rest_pass, rest_pass, rest_pass, rest_pass))

    user_pass = generate_password_hash("123456")
    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, role, phone, address)
        VALUES 
        ('charity1', ?, 'جمعية صناع الخير للإغاثة', 'charity', '01556677889', 'مصر القديمة'),
        ('charity2', ?, 'مؤسسة إطعام وتكافل', 'charity', '01511223344', 'المعادي'),
        ('customer1', ?, 'أحمد محمود', 'customer', '01012345678', 'الدقي'),
        ('customer2', ?, 'سارة إبراهيم', 'customer', '01087654321', 'مدينة نصر')
    """, (user_pass, user_pass, user_pass, user_pass))
    conn.commit()

    cursor.execute("SELECT id, username FROM users WHERE role = 'restaurant'")
    restaurants = {row["username"]: row["id"] for row in cursor.fetchall()}

    meals_data = [
        (restaurants['bakery'], 'صندوق مخبوزات وكرواسون فرنسي طازج', 'تشكيلة فينو وكرواسون وباتيه مورق من إنتاج اليوم متبقية لموعد الإغلاق، مغلفة بحرص', 'مخبوزات', 90.0, 35.0, 8, 'اليوم من 9:00م إلى 11:30م', 0),
        (restaurants['restaurant1'], 'صينية أرز بسمتي ودجاج مشوي مع خضار سوتيه', 'وجبات كاملة ومغلفة حرارياً من بوفيه العشاء اليومي، صالحة وشهية 100%', 'وجبات رئيسية', 140.0, 55.0, 5, 'اليوم من 10:00م إلى 12:00 منتصف الليل', 0),
        (restaurants['pastry'], 'صندوق تشكيلة شرقية وساليزون فاخر', 'قطع بسبوسة وكنافة وساليزون متبقية من واجهة العرض صالحة وطازجة في بوكس أنيق', 'حلويات', 160.0, 65.0, 6, 'اليوم من 8:30م إلى 10:30م', 0),
        (restaurants['fresh_grill'], '15 وجبة إطعام عائلية للأسر الأكثر احتياجاً', 'صواني مأكولات مطبوخة بالكامل ومغلفة خصيصاً للتبرع للجمعيات الخيرية والمبادرات الإغاثية', 'وجبات رئيسية', 450.0, 0.0, 15, 'التسليم الفوري من 9:00م إلى 11:00م', 1),
    ]

    cursor.executemany("""
        INSERT INTO meals (restaurant_id, title, description, category, original_price, discounted_price, quantity, pickup_time, is_charity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, meals_data)
    conn.commit()

def generate_order_code():
    chars = string.ascii_uppercase + string.digits
    rand = ''.join(random.choices(chars, k=5))
    return f"ZAD-{rand}"

def calculate_environmental_impact(rescued_meals_count):
    co2_kg = round(rescued_meals_count * 2.5, 1)
    water_liters = int(rescued_meals_count * 1000)
    return co2_kg, water_liters

# حاقن الإشعارات العامة لجميع الصفحات (Context Processor)
@app.context_processor
def inject_notifications():
    if session.get("user_id") and session.get("role") == "restaurant":
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM orders o
                JOIN meals m ON o.meal_id = m.id
                WHERE m.restaurant_id = ? AND o.status = 'pending'
            """, (session["user_id"],))
            pending_count = cursor.fetchone()[0] or 0
            conn.close()
            return {"restaurant_pending_count": pending_count}
        except Exception:
            return {"restaurant_pending_count": 0}
    return {"restaurant_pending_count": 0}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("من فضلك سجل دخولك أولاً للمتابعة", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session or session.get("role") not in allowed_roles:
                flash("غير مصرح لك بالدخول لهذه الصفحة", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.errorhandler(404)
def page_not_found(e):
    flash("الصفحة المطلوبة غير موجودة", "warning")
    return redirect(url_for("home"))

@app.errorhandler(500)
def internal_server_error(e):
    flash("حدث خطأ غير متوقع في الخادم، يرجى المحاولة لاحقاً", "danger")
    return redirect(url_for("home"))

# ----------------- الصفحات الرئيسية -----------------

@app.route("/")
def home():
    category = request.args.get("category", "").strip()
    feed_type = request.args.get("type", "").strip()
    area = request.args.get("area", "").strip()
    
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(quantity) FROM orders WHERE status = 'completed'")
    rescued_meals_count = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM((m.original_price - m.discounted_price) * o.quantity) 
        FROM orders o 
        JOIN meals m ON o.meal_id = m.id 
        WHERE o.status = 'completed' AND m.is_charity = 0
    """)
    money_saved = round(cursor.fetchone()[0] or 0, 1)

    cursor.execute("""
        SELECT SUM(o.quantity) FROM orders o 
        JOIN meals m ON o.meal_id = m.id 
        WHERE m.is_charity = 1 AND o.status = 'completed'
    """)
    charity_meals_count = cursor.fetchone()[0] or 0

    co2_saved, water_saved = calculate_environmental_impact(rescued_meals_count)

    cursor.execute("""
        SELECT DISTINCT address FROM users WHERE role = 'restaurant' AND address IS NOT NULL AND address != ''
    """)
    raw_addresses = [row["address"] for row in cursor.fetchall()]
    areas = []
    for addr in raw_addresses:
        main_part = addr.split("-")[0].strip()
        if main_part and main_part not in areas:
            areas.append(main_part)

    query = """
        SELECT m.*, u.full_name as restaurant_name, u.username as restaurant_username, u.address as restaurant_address, u.phone as restaurant_phone
        FROM meals m
        JOIN users u ON m.restaurant_id = u.id
        WHERE m.status = 'available' AND m.quantity > 0
    """
    params = []

    if category:
        query += " AND m.category = ?"
        params.append(category)

    user_role = session.get("role")

    # حصر عروض التبرع الخيري المجاني (is_charity = 1) على حسابات الجمعيات الخيرية المعتمدة والأدمن فقط
    if user_role not in ["charity", "admin"]:
        # المستخدم العادي أو الزائر يرى فقط عروض التوفير المخفضة للشراء
        query += " AND m.is_charity = 0"
    else:
        # حسابات الجمعيات الخيرية والأدمن يمكنهم تصفح التبرعات أو عروض التوفير
        if feed_type == "charity":
            query += " AND m.is_charity = 1"
        elif feed_type == "discount":
            query += " AND m.is_charity = 0"

    if area:
        query += " AND u.address LIKE ?"
        params.append(f"%{area}%")

    query += " ORDER BY m.id DESC"
    cursor.execute(query, params)
    meals = cursor.fetchall()
    conn.close()

    stats = {
        "rescued_meals": rescued_meals_count,
        "money_saved": money_saved,
        "charity_meals": charity_meals_count,
        "co2_saved": co2_saved,
        "water_saved": water_saved
    }

    return render_template(
        "index.html",
        meals=meals,
        stats=stats,
        selected_category=category,
        selected_type=feed_type,
        selected_area=area,
        areas=areas
    )

# ----------------- تسجيل الدخول وإنشاء حساب -----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("يرجى ملء اسم المستخدم وكلمة المرور", "warning")
            return redirect(url_for("login"))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            session["address"] = user["address"] or ""
            session["phone"] = user["phone"] or ""
            flash(f"أهلاً بك يا {user['full_name']}! تم تسجيل الدخول بنجاح", "success")

            if user["role"] == "restaurant":
                return redirect(url_for("restaurant_dashboard"))
            elif user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("home"))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "customer").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if role not in ["customer", "restaurant", "charity"]:
            role = "customer"

        if not username or not password or not full_name:
            flash("من فضلك املأ جميع الحقول الأساسية المطلوبة", "warning")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("كلمة المرور يجب ألا تقل عن 8 خانات لضمان أمان حسابك", "warning")
            return redirect(url_for("register"))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("اسم المستخدم مسجل مسبقاً، يرجى اختيار اسم دخول آخر", "danger")
            conn.close()
            return redirect(url_for("register"))

        pass_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, pass_hash, full_name, role, phone, address))
        conn.commit()
        conn.close()

        flash("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول مباشرة", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.. نتمنى لك يوماً سعيداً", "info")
    return redirect(url_for("home"))

# ----------------- لوحة تحكم المطعم والميزات -----------------

@app.route("/restaurant/dashboard")
@login_required
@role_required("restaurant")
def restaurant_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    rest_id = session["user_id"]

    cursor.execute("""
        SELECT * FROM meals WHERE restaurant_id = ? ORDER BY id DESC
    """, (rest_id,))
    meals = cursor.fetchall()

    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN is_charity = 0 THEN 1 END) as sales_count,
            COUNT(CASE WHEN is_charity = 1 THEN 1 END) as charity_count,
            SUM(quantity) as current_stock
        FROM meals WHERE restaurant_id = ?
    """, (rest_id,))
    stats = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) FROM orders o
        JOIN meals m ON o.meal_id = m.id
        WHERE m.restaurant_id = ? AND o.status = 'completed'
    """, (rest_id,))
    completed_orders_count = cursor.fetchone()[0]

    # جلب الطلبات المعلقة الجديدة تحديداً لعرضها في بانر التنبيه العاجل
    cursor.execute("""
        SELECT o.*, m.title as meal_title, u.full_name as customer_name, u.phone as customer_phone
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON o.user_id = u.id
        WHERE m.restaurant_id = ? AND o.status = 'pending'
        ORDER BY o.id DESC
    """, (rest_id,))
    pending_orders = cursor.fetchall()

    # جلب كافة طلبات زبائن المطعم (مع تفاصيل التوصيل والكميات)
    cursor.execute("""
        SELECT o.*, m.title as meal_title, u.full_name as customer_name, u.phone as customer_phone
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON o.user_id = u.id
        WHERE m.restaurant_id = ?
        ORDER BY o.id DESC
        LIMIT 35
    """, (rest_id,))
    orders = cursor.fetchall()

    conn.close()
    return render_template(
        "restaurant_dashboard.html",
        meals=meals,
        stats=stats,
        orders=orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders_count
    )

@app.route("/meal/add", methods=["POST"])
@login_required
@role_required("restaurant")
def add_meal():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "أخرى").strip()
    
    try:
        original_price = float(request.form.get("original_price", 0))
    except (ValueError, TypeError):
        original_price = 0.0

    is_charity = 1 if request.form.get("is_charity") == "1" else 0
    
    try:
        discounted_price = 0.0 if is_charity else float(request.form.get("discounted_price", 0))
    except (ValueError, TypeError):
        discounted_price = 0.0

    try:
        quantity = int(request.form.get("quantity", 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    pickup_time = request.form.get("pickup_time", "").strip()

    if not title or not pickup_time:
        flash("يرجى ملء اسم الوجبة وميعاد الاستلام بدقة", "warning")
        return redirect(url_for("restaurant_dashboard"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meals (restaurant_id, title, description, category, original_price, discounted_price, quantity, pickup_time, is_charity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session["user_id"], title, description, category, original_price, discounted_price, quantity, pickup_time, is_charity))
    conn.commit()
    conn.close()

    flash("تمت إضافة الفائض بنجاح وأصبح متاحاً الآن للحجز في المنصة! 🎉", "success")
    return redirect(url_for("restaurant_dashboard"))

@app.route("/meal/edit/<int:meal_id>", methods=["POST"])
@login_required
@role_required("restaurant")
def edit_meal(meal_id):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "أخرى").strip()
    
    try:
        original_price = float(request.form.get("original_price", 0))
    except (ValueError, TypeError):
        original_price = 0.0

    is_charity = 1 if request.form.get("is_charity") == "1" else 0
    
    try:
        discounted_price = 0.0 if is_charity else float(request.form.get("discounted_price", 0))
    except (ValueError, TypeError):
        discounted_price = 0.0

    try:
        quantity = int(request.form.get("quantity", 1))
        if quantity < 0:
            quantity = 0
    except (ValueError, TypeError):
        quantity = 0

    pickup_time = request.form.get("pickup_time", "").strip()
    status = 'available' if quantity > 0 else 'sold_out'

    if not title or not pickup_time:
        flash("يرجى التأكد من كتابة اسم الوجبة وتوقيت الاستلام", "warning")
        return redirect(url_for("restaurant_dashboard"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE meals 
        SET title = ?, description = ?, category = ?, original_price = ?, 
            discounted_price = ?, quantity = ?, pickup_time = ?, is_charity = ?, status = ?
        WHERE id = ? AND restaurant_id = ?
    """, (title, description, category, original_price, discounted_price, quantity, pickup_time, is_charity, status, meal_id, session["user_id"]))
    conn.commit()
    conn.close()

    flash(f"✅ تم تحديث بيانات الوجبة ({title}) بنجاح!", "success")
    return redirect(url_for("restaurant_dashboard"))

@app.route("/meal/delete/<int:meal_id>", methods=["POST"])
@login_required
@role_required("restaurant")
def delete_meal(meal_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meals WHERE id = ? AND restaurant_id = ?", (meal_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("تم حذف الوجبة بنجاح من قائمة عروضك", "info")
    return redirect(url_for("restaurant_dashboard"))

@app.route("/restaurant/verify-order", methods=["POST"])
@login_required
@role_required("restaurant")
def verify_order():
    code = request.form.get("order_code", "").strip().upper()
    if not code:
        flash("يرجى إدخال كود الحجز أولاً", "warning")
        return redirect(url_for("restaurant_dashboard"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.*, m.title as meal_title, m.restaurant_id, u.full_name as customer_name
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON o.user_id = u.id
        WHERE o.order_code = ?
    """, (code,))
    order = cursor.fetchone()

    if not order:
        flash(f"❌ كود الحجز ({code}) غير صحيح أو غير مسجل في النظام!", "danger")
    elif order["restaurant_id"] != session["user_id"]:
        flash(f"⚠️ كود الحجز ({code}) يتبع لمطعم آخر وليس لمطعمك!", "warning")
    elif order["status"] == "completed":
        flash(f"ℹ️ تم تسليم هذا الطلب مسبقاً وتأكيد استلامه!", "info")
    elif order["status"] == "cancelled":
        flash(f"⚠️ هذا الطلب تم إلغاؤه من قبل العميل مسبقاً!", "danger")
    else:
        cursor.execute("UPDATE orders SET status = 'completed' WHERE id = ?", (order["id"],))
        conn.commit()
        delivery_msg = "بواسطة المندوب" if order["delivery_type"] == "delivery" else "في المحل"
        flash(f"🎉 ممتاز! تم تأكيد تسليم ({order['meal_title']} × {order['quantity']}) للعميل {order['customer_name']} ({delivery_msg}) بنجاح!", "success")

    conn.close()
    return redirect(url_for("restaurant_dashboard"))

# ----------------- دورة حياة الحجز بالكميات وطريقة الاستلام/التوصيل -----------------

@app.route("/order/create/<int:meal_id>", methods=["POST"])
@login_required
def create_order(meal_id):
    user_id = session["user_id"]
    user_role = session.get("role")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meals WHERE id = ?", (meal_id,))
    meal = cursor.fetchone()

    if not meal:
        flash("الوجبة غير موجودة أو تم حذفها", "danger")
        conn.close()
        return redirect(url_for("home"))

    # 1. منع حسابات المطاعم من حجز أي وجبات نهائياً
    if user_role == "restaurant":
        flash("حسابات المطاعم مخصصة لعرض وإدارة الفوائض فقط، ولا يمكنها حجز الوجبات! يرجى تسجيل الدخول بحساب مشتري (Customer).", "danger")
        conn.close()
        return redirect(url_for("home"))

    # 2. منع أي مستخدم من حجز وجبة لمطعم يملكه
    if meal["restaurant_id"] == user_id:
        flash("خطأ في الصلاحيات: لا يمكن لصاحب المنشأة حجز وجباته الخاصة!", "danger")
        conn.close()
        return redirect(url_for("home"))

    # 3. الصلاحية الحصرية للتبرع الخيري (فقط للجمعيات الخيرية)
    if meal["is_charity"] == 1:
        if user_role != "charity":
            flash("عروض التبرع الخيري المجاني مخصصة حصرياً للجمعيات الخيرية والمبادرات الإغاثية المعتمدة!", "warning")
            conn.close()
            return redirect(url_for("home"))
    else:
        # 4. وجبات التوفير المخفضة مخصصة للمشترين والمستهلكين
        if user_role not in ["customer", "charity"]:
            flash("حجز وجبات التوفير مخصص لحسابات المشترين والمستهلكين فقط!", "warning")
            conn.close()
            return redirect(url_for("home"))

    # استلام الكمية المطلوبة وطريقة الاستلام مع دعم كامل للأرقام العربية والإنجليزية
    raw_qty = str(request.form.get("quantity", "1")).strip()
    arabic_digits = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    raw_qty = raw_qty.translate(arabic_digits)
    try:
        requested_qty = int(raw_qty)
        if requested_qty < 1:
            requested_qty = 1
    except (ValueError, TypeError):
        requested_qty = 1

    delivery_type = request.form.get("delivery_type", "pickup").strip()
    delivery_address = request.form.get("delivery_address", "").strip()

    # إذا اختار توصيل، نتأكد من إدخال العنوان
    if delivery_type == "delivery" and not delivery_address:
        delivery_address = session.get("address", "")
        if not delivery_address:
            flash("يرجى كتابة عنوان التوصيل بالتفصيل", "warning")
            conn.close()
            return redirect(url_for("home"))

    if meal["quantity"] < requested_qty or meal["status"] != "available":
        flash(f"عذراً، الكمية المتاحة حالياً من هذه الوجبة هي {meal['quantity']} فقط!", "warning")
        conn.close()
        return redirect(url_for("home"))

    order_code = generate_order_code()
    
    # حساب الإجمالي مع مصاريف التوصيل
    delivery_fee = 20.0 if (delivery_type == "delivery" and meal["is_charity"] == 0) else 0.0
    meals_price = meal["discounted_price"] * requested_qty
    total_price = meals_price + delivery_fee

    # إنشاء الطلب
    cursor.execute("""
        INSERT INTO orders (order_code, meal_id, user_id, quantity, total_price, status, delivery_type, delivery_address, delivery_fee)
        VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?)
    """, (order_code, meal_id, user_id, requested_qty, total_price, delivery_type, delivery_address, delivery_fee))

    # خصم الكمية المحجوزة بدقة
    new_quantity = meal["quantity"] - requested_qty
    new_status = 'sold_out' if new_quantity == 0 else 'available'
    cursor.execute("UPDATE meals SET quantity = ?, status = ? WHERE id = ?", (new_quantity, new_status, meal_id))

    conn.commit()
    conn.close()

    method_text = "طلب توصيل دليفري" if delivery_type == "delivery" else "استلام ذاتي من المحل"
    flash(f"تم إتمام الحجز بنجاح ({requested_qty} وجبات - {method_text})! كود الاستلام هو: {order_code}", "success")
    return redirect(url_for("my_orders"))

# ميزة إلغاء الحجز وإعادة المخزون الدقيق (Cancellation & Restocking)
@app.route("/order/cancel/<int:order_id>", methods=["POST"])
@login_required
def cancel_order(order_id):
    user_id = session["user_id"]
    user_role = session.get("role")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, m.id as meal_id, m.quantity as meal_qty, m.title as meal_title
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        WHERE o.id = ?
    """, (order_id,))
    order = cursor.fetchone()

    if not order:
        flash("الطلب غير موجود", "danger")
        conn.close()
        return redirect(url_for("my_orders"))

    if order["user_id"] != user_id and user_role != "admin":
        flash("غير مصرح لك بإلغاء هذا الطلب", "danger")
        conn.close()
        return redirect(url_for("my_orders"))

    if order["status"] != "pending":
        flash("لا يمكن إلغاء طلب تم تسليمه بالفعل أو ملغي مسبقاً", "warning")
        conn.close()
        return redirect(url_for("my_orders"))

    # 1. تحديث حالة الطلب إلى ملغي
    cursor.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))

    # 2. إعادة كامل الكمية المحجوزة إلى رصيد المطعم
    restocked_qty = order["meal_qty"] + order["quantity"]
    cursor.execute("UPDATE meals SET quantity = ?, status = 'available' WHERE id = ?", (restocked_qty, order["meal_id"]))

    conn.commit()
    conn.close()

    flash(f"تم إلغاء الحجز للطلب ({order['order_code']}) بنجاح، وتمت إعادة {order['quantity']} وجبات لرصيد المطعم لعدم هدرها! 🔄", "info")
    return redirect(url_for("my_orders"))

@app.route("/my-orders")
@login_required
def my_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, m.title as meal_title, m.pickup_time, m.is_charity, m.discounted_price,
               u.full_name as restaurant_name, u.address as restaurant_address, u.phone as restaurant_phone
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON m.restaurant_id = u.id
        WHERE o.user_id = ?
        ORDER BY o.id DESC
    """, (session["user_id"],))
    orders = cursor.fetchall()
    conn.close()
    return render_template("my_orders.html", orders=orders)

# ----------------- لوحة تحكم الجمعيات الخيرية وشهادة الأثر المجتمعي -----------------

@app.route("/charity/dashboard")
@login_required
def charity_dashboard():
    user_id = session["user_id"]
    user_role = session.get("role")

    if user_role not in ["charity", "admin"]:
        flash("هذه اللوحة مخصصة لحسابات الجمعيات الخيرية والمؤسسات الإغاثية المعتمدة فقط!", "danger")
        return redirect(url_for("home"))

    conn = get_db()
    cursor = conn.cursor()

    # 1. إحصائيات التبرعات والوجبات المستلمة
    cursor.execute("""
        SELECT SUM(o.quantity) 
        FROM orders o 
        JOIN meals m ON o.meal_id = m.id 
        WHERE o.user_id = ? AND o.status = 'completed'
    """, (user_id,))
    total_meals_rescued = cursor.fetchone()[0] or 0

    # تقدير عدد الأسر المستفيدة (بمعدل 3 وجبات لكل أسرة)
    beneficiary_families = math.ceil(total_meals_rescued / 3) if total_meals_rescued > 0 else 0

    # القيمة السوقية للطعام الموزع مجاناً (بالأسعار الأصلية للمطاعم)
    cursor.execute("""
        SELECT SUM(m.original_price * o.quantity)
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        WHERE o.user_id = ? AND o.status = 'completed'
    """, (user_id,))
    market_value_saved = round(cursor.fetchone()[0] or 0.0, 1)

    # الأثر البيئي المنقذ من خلال الجمعية
    co2_saved, water_saved = calculate_environmental_impact(total_meals_rescued)

    # 2. الحجوزات الجارية في انتظار الاستلام للجمعية
    cursor.execute("""
        SELECT o.*, m.title as meal_title, m.pickup_time, u.full_name as restaurant_name, u.address as restaurant_address, u.phone as restaurant_phone
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON m.restaurant_id = u.id
        WHERE o.user_id = ? AND o.status = 'pending'
        ORDER BY o.id DESC
    """, (user_id,))
    pending_donations = cursor.fetchall()

    # 3. سجل التبرعات السابقة المستلمة
    cursor.execute("""
        SELECT o.*, m.title as meal_title, m.original_price, u.full_name as restaurant_name, u.address as restaurant_address
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON m.restaurant_id = u.id
        WHERE o.user_id = ? AND o.status = 'completed'
        ORDER BY o.id DESC
    """, (user_id,))
    completed_donations = cursor.fetchall()

    # 4. عدد عروض التبرع الخيري المجاني المتاحة حالياً على المنصة
    cursor.execute("SELECT COUNT(*) FROM meals WHERE is_charity = 1 AND status = 'available' AND quantity > 0")
    available_charity_offers = cursor.fetchone()[0]

    conn.close()

    charity_stats = {
        "meals_rescued": total_meals_rescued,
        "beneficiary_families": beneficiary_families,
        "market_value_saved": market_value_saved,
        "co2_saved": co2_saved,
        "water_saved": water_saved,
        "available_offers": available_charity_offers,
        "pending_count": len(pending_donations),
        "completed_count": len(completed_donations)
    }

    return render_template(
        "charity_dashboard.html",
        stats=charity_stats,
        pending_donations=pending_donations,
        completed_donations=completed_donations,
        today_date=datetime.now().strftime('%Y-%m-%d')
    )

# ----------------- لوحة تحكم الأدمن والتقارير المتقدمة -----------------

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'restaurant'")
    restaurants_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'charity'")
    charities_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
    customers_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM orders WHERE status = 'completed'")
    completed_meals = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM((m.original_price - m.discounted_price) * o.quantity)
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        WHERE o.status = 'completed' AND m.is_charity = 0
    """)
    total_money_saved = round(cursor.fetchone()[0] or 0, 1)

    co2_saved, water_saved = calculate_environmental_impact(completed_meals)

    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM meals 
        GROUP BY category
    """)
    category_distribution = {row["category"]: row["count"] for row in cursor.fetchall()}

    # توزيع حالات الطلبات وسلاسل الإمداد (Order Fulfillment Statuses)
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM orders
        GROUP BY status
    """)
    status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
    order_status_data = {
        "completed": status_counts.get("completed", 0),
        "pending": status_counts.get("pending", 0),
        "cancelled": status_counts.get("cancelled", 0)
    }

    # مؤشرات نظم دعم القرار (MIS Decision Support System - DSS Metrics)
    fulfillment_rate = round((order_status_data["completed"] / total_orders * 100), 1) if total_orders > 0 else 100.0
    highest_waste_category = max(category_distribution, key=category_distribution.get) if category_distribution else "مخبوزات"

    cursor.execute("""
        SELECT strftime('%Y-%m-%d', created_at) as order_date, COUNT(*) as count
        FROM orders
        GROUP BY order_date
        ORDER BY order_date ASC
        LIMIT 10
    """)
    timeline_rows = cursor.fetchall()
    timeline_labels = [row["order_date"] for row in timeline_rows] or [datetime.now().strftime('%Y-%m-%d')]
    timeline_counts = [row["count"] for row in timeline_rows] or [0]

    cursor.execute("SELECT id, username, full_name, role, phone, address, created_at FROM users ORDER BY id DESC")
    all_users = cursor.fetchall()

    cursor.execute("""
        SELECT o.*, m.title as meal_title, u.full_name as user_name, r.full_name as restaurant_name
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON o.user_id = u.id
        JOIN users r ON m.restaurant_id = r.id
        ORDER BY o.id DESC
        LIMIT 25
    """)
    recent_orders = cursor.fetchall()

    conn.close()

    stats = {
        "restaurants": restaurants_count,
        "charities": charities_count,
        "customers": customers_count,
        "total_orders": total_orders,
        "completed_meals": completed_meals,
        "total_money_saved": total_money_saved,
        "co2_saved": co2_saved,
        "water_saved": water_saved,
        "fulfillment_rate": fulfillment_rate,
        "highest_waste_category": highest_waste_category
    }

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        users=all_users,
        orders=recent_orders,
        cat_dist=category_distribution,
        order_status=order_status_data,
        timeline_labels=timeline_labels,
        timeline_counts=timeline_counts
    )

@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):
    if user_id == session["user_id"]:
        flash("حماية أمنية: لا يمكن حذف حساب الأدمن الأساسي الجاري العمل به!", "danger")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("تم حذف المستخدم وكافة ارتباطاته بنجاح من النظام", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/export-csv")
@login_required
@role_required("admin")
def export_csv():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.order_code, m.title, r.full_name as restaurant, u.full_name as customer,
               o.quantity, o.delivery_type, o.delivery_address, o.total_price, o.status, o.created_at
        FROM orders o
        JOIN meals m ON o.meal_id = m.id
        JOIN users u ON o.user_id = u.id
        JOIN users r ON m.restaurant_id = r.id
        ORDER BY o.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["كود الحجز", "اسم الوجبة/الفائض", "المطعم أو المنشأة", "المستلم/العميل", "الكمية", "طريقة الاستلام", "عنوان التوصيل", "السعر الإجمالي (ج.م)", "حالة الطلب", "تاريخ الحجز"])
    for r in rows:
        del_type = "توصيل منزلي" if r[5] == "delivery" else "استلام ذاتي"
        status_ar = "تم التسليم" if r[8] == "completed" else ("في انتظار الاستلام" if r[8] == "pending" else "ملغي")
        writer.writerow([r[0], r[1], r[2], r[3], r[4], del_type, r[6] or "-", r[7], status_ar, r[9]])

    return Response(
        output.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=zad_food_rescue_full_report.csv"}
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
