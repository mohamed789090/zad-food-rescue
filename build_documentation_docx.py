import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def create_graduation_doc():
    doc = Document()

    # هوامش قياسية
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # الألوان الرسمية
    C_EMERALD = RGBColor(4, 120, 87)    # #047857
    C_DARK    = RGBColor(30, 41, 59)    # #1e293b
    C_AMBER   = RGBColor(217, 119, 6)   # #d97706
    C_MUTED   = RGBColor(100, 116, 139) # #64748b
    C_WHITE   = RGBColor(255, 255, 255)

    def add_custom_heading(text, level, color=C_EMERALD):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Cairo'
        run.font.color.rgb = color
        if level == 1:
            run.font.size = Pt(20)
        elif level == 2:
            run.font.size = Pt(16)
        else:
            run.font.size = Pt(13)
        return p

    def add_arabic_paragraph(text, bold=False, size=12, color=C_DARK, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=6):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.25
        run = p.add_run(text)
        run.bold = bold
        run.font.name = 'Cairo'
        run.font.size = Pt(size)
        run.font.color.rgb = color
        return p

    def add_callout_box(text, heading_text="ملحوظة أكاديمية هامة:"):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, 'F0FDF4')
        cell.width = Inches(6.5)
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_after = Pt(4)
        r_head = p.add_run(f"📌 {heading_text}\n")
        r_head.bold = True
        r_head.font.name = 'Cairo'
        r_head.font.size = Pt(12)
        r_head.font.color.rgb = C_EMERALD

        r_body = p.add_run(text)
        r_body.font.name = 'Cairo'
        r_body.font.size = Pt(11)
        r_body.font.color.rgb = C_DARK
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==================== صفحة الغلاف الرسمية ====================
    add_arabic_paragraph("جمهورية مصر العربية", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_arabic_paragraph("وزارة التعليم العالي والبحث العلمي", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_arabic_paragraph("المعهد العالي / كلية نظم المعلومات الإدارية (MIS)", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_arabic_paragraph("قسم نظم المعلومات الإدارية والحاسب الآلي", size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    p_cover_title = doc.add_paragraph()
    p_cover_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ct = p_cover_title.add_run("مَنَصَّة زَادْ (ZAD)\nلإنقاذ فوائض الطعام وتعزيز كفاءة سلاسل الإمداد والتكافل المستدام")
    r_ct.bold = True
    r_ct.font.name = 'Cairo'
    r_ct.font.size = Pt(24)
    r_ct.font.color.rgb = C_EMERALD

    p_cover_sub = doc.add_paragraph()
    p_cover_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cs = p_cover_sub.add_run("A Web-Based Decision Support Platform for Food Surplus Rescue & Sustainable Supply Chains")
    r_cs.italic = True
    r_cs.font.name = 'Arial'
    r_cs.font.size = Pt(13)
    r_cs.font.color.rgb = C_MUTED

    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    add_arabic_paragraph("مشروع تخرج مُقدم لنيل درجة البكالوريوس في نظم المعلومات الإدارية (MIS)", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_arabic_paragraph("العام الجامعي: 2025 / 2026", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph().paragraph_format.space_after = Pt(30)

    # جدول الغلاف: إعداد الطلاب والإشراف
    table_team = doc.add_table(rows=2, cols=2)
    table_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    c1 = table_team.cell(0, 0)
    c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = c1.paragraphs[0].add_run("تحت إشراف:")
    r1.bold = True
    r1.font.name = 'Cairo'
    r1.font.size = Pt(12)
    r1.font.color.rgb = C_AMBER
    
    c2 = table_team.cell(0, 1)
    c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = c2.paragraphs[0].add_run("إعداد فريق العمل:")
    r2.bold = True
    r2.font.name = 'Cairo'
    r2.font.size = Pt(12)
    r2.font.color.rgb = C_AMBER

    c3 = table_team.cell(1, 0)
    c3.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c3.paragraphs[0].add_run("لجنة السادة الأساتذة المشرفين والمحكمين\nقسم نظم المعلومات الإدارية")

    c4 = table_team.cell(1, 1)
    c4.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c4.paragraphs[0].add_run("فريق طلاب الفرقة الرابعة\nمشروع التخرج — دور مايو 2026")

    doc.add_page_break()

    # ==================== المستخلص (Abstract) ====================
    add_custom_heading("المستخلص (Abstract)", 1)
    add_arabic_paragraph(
        "تُعد ظاهرة هدر وفقد الأغذية من أبرز التحديات الاقتصادية والبيئية والمجتمعية التي تواجه دول العالم بصفة عامة، وجمهورية مصر العربية بصفة خاصة، "
        "حيث تشير تقارير منظمة الأغذية والزراعة (FAO) إلى هدر ملايين الأطنان من الأطعمة الصالحة للاستهلاك سنوياً، في الوقت الذي تشهد فيه الأسواق ضغوطاً تضخمية وحاجة متزايدة للأسر المتعففة للغذاء. "
        "يهدف هذا المشروع إلى تطوير نظام معلومات إداري سحابي متكامل يحمل اسم 'مَنَصَّة زَادْ (ZAD)' ليعمل كحلقة وصل وتنسيق رقمي تفاعلي بين منشآت الأغذية (المطاعم، المخابز، والحلويات)، "
        "والمستهلكين الباحثين عن وجبات طازجة بأسعار مخفضة، والجمعيات الخيرية والمؤسسات الإغاثية المستفيدة من التبرعات المجانية."
    )
    add_arabic_paragraph(
        "يعتمد النظام على نمط المعمارية البرمجية Model-View-Controller (MVC) باستخدام إطار العمل Python Flask، وقاعدة بيانات علائقية SQLite، وواجهات مستخدم تفاعلية متجاوبة بنظام Bootstrap 5 و GSAP Animations. "
        "كما زُوّدت المنصة بوحدة نظم دعم قرار (MIS Decision Support System - DSS) تقوم باحتساب مؤشرات الأثر البيئي اللحظي (مكافئ غاز الكربون CO2e المحتجز والبصمة المائية الافتراضية الموفرة)، "
        "وتحليل مسار سلاسل الإمداد ومعدلات إنجاز الطلبات لتقديم توصيات استراتيجية للإدارة. "
        "أثبتت مخرجات النظام كفاءة عالية في سرعة إنجاز دورة حياة الطلب والتبرع عبر أكواد الاستلام الموحدة، وتحقيق التوازن الأمثل بين الجدوى الاقتصادية، المسؤولية المجتمعية (CSR)، وأهداف التنمية المستدامة (UN SDGs 2, 12, 13)."
    )

    add_custom_heading("Abstract (English)", 2)
    p_en = doc.add_paragraph()
    p_en.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_en.paragraph_format.line_spacing = 1.25
    r_en = p_en.add_run(
        "Food surplus and waste represent a critical economic, environmental, and humanitarian challenge worldwide and specifically in Egypt. "
        "This graduation project introduces 'ZAD Platform', an end-to-end cloud-based Management Information System (MIS) designed to optimize food supply chains and eliminate food waste. "
        "ZAD acts as a real-time digital bridge connecting food retailers (restaurants, bakeries, confectioneries) with price-conscious consumers and certified NGOs/charities. "
        "Built upon the MVC architecture using Python Flask, SQLite, and responsive front-end frameworks (Bootstrap 5, GSAP, Lenis), "
        "the platform features role-based access control, dynamic multi-unit booking, verified pickup codes, and a Decision Support System (DSS) "
        "that calculates environmental metrics (CO2e avoided and virtual water footprint saved) while providing actionable operational insights. "
        "The project strongly aligns with the United Nations Sustainable Development Goals (SDGs 2, 12, and 13)."
    )
    r_en.font.name = 'Arial'
    r_en.font.size = Pt(11)

    doc.add_page_break()

    # ==================== الفصل الأول ====================
    add_custom_heading("الفصل الأول: الإطار العام والدراسة النظرية للمشروع", 1)
    
    add_custom_heading("1.1 مقدمة عامة", 2)
    add_arabic_paragraph(
        "شهدت العقود الأخيرة تحولات جذرية في مفهوم إدارة سلاسل الإمداد (Supply Chain Management)، حيث لم يعد التركيز مقتصراً على تعظيم الإنتاج فقط، "
        "بل امتد ليشمل إدارة ما بعد البيع والتخلص الآمن والرشيد من الفوائض لمنع الهدر اللوجستي والاقتصادي. "
        "تأتي منصة 'زَادْ' كمبادرة تقنية رائدة تسخر نظم المعلومات الحديثة لتحويل معضلة فائض الطعام المسائي في المنشآت التجارية إلى فرصة استثمارية وتكافلية مستدامة."
    )

    add_custom_heading("1.2 مشكلة البحث والدافع (Problem Statement)", 2)
    add_arabic_paragraph(
        "تتلخص مشكلة الدراسة في النقاط التالية:\n"
        "1. الهدر المالي المباشر: تتكبد المنشآت الغذائية خسائر يومية ناتجة عن التخلص من فوائض الطعام الطازج في نهاية اليوم لعدم وجود قنوات تصريف سريعة.\n"
        "2. الأثر البيئي السلبي: تحلل المخلفات العضوية في مقالب القمامة ينتج غاز الميثان، وهو من أشد غازات الاحتباس الحراري تأثيراً على ظاهرة التغير المناخي، فضلاً عن استنزاف البصمة المائية.\n"
        "3. فجوة التوزيع المجتمعي: صعوبة وصول الجمعيات الخيرية والمستهلكين محدودي الدخل إلى تلك الفوائض بطريقة منظمة وكريمة تحفظ كرامة المستفيد."
    )

    add_custom_heading("1.3 أهداف المشروع", 2)
    add_arabic_paragraph(
        "• الهدف العام: تطوير نظام معلومات إداري متكامل لإدارة وإنقاذ فوائض الأغذية وتحقيق نموذج 'صفر هدر' (Zero Waste Platform).\n"
        "• الأهداف الفرعية:\n"
        "  - أتمتة دورة حياة الفائض الغذائي بدءاً من إدراجه من المطعم وحتى استلامه عبر العميل أو الجمعية.\n"
        "  - ابتكار نظام حجز مرن يتيح اختيار الكميات وتحديد أسلوب الاستلام (استلام ذاتي بالكود أو توصيل منزلي).\n"
        "  - بناء نظام دعم قرار (DSS) للإدارة يرصد مؤشرات الأداء ويوفر رسوماً بيانية تفاعلية لحجم الإنقاذ.\n"
        "  - تقديم مسار مخصص للجمعيات الخيرية يوثق الأثر المجتمعي عبر شهادات رسمية قابلة للطباعة."
    )

    add_custom_heading("1.4 التوافق مع أهداف التنمية المستدامة (UN SDGs)", 2)
    add_callout_box(
        "يحقق مشروع منصة زاد ارتباطاً وثيقاً مع أهداف التنمية المستدامة للأمم المتحدة:\n"
        "• الهدف 2 (القضاء التام على الجوع - Zero Hunger): توجيه وجبات الإطعام المجانية للأسر الأكثر احتياجاً.\n"
        "• الهدف 12 (الاستهلاك والإنتاج المسؤولان): خفض الهدر الغذائي بموجب المستهدف العالمي 12.3.\n"
        "• الهدف 13 (العمل المناخي - Climate Action): تقليص البصمة الكربونية والمائية الناجمة عن تحلل الغذاء.",
        "التوافق مع رؤية مصر 2030 وأهداف الأمم المتحدة"
    )

    doc.add_page_break()

    # ==================== الفصل الثاني ====================
    add_custom_heading("الفصل الثاني: دراسة الجدوى وتحليل متطلبات النظام", 1)

    add_custom_heading("2.1 دراسة الجدوى الثلاثية (Feasibility Study)", 2)
    add_arabic_paragraph(
        "1. الجدوى الفنية (Technical Feasibility): تم الاعتماد على حزمة برمجية قياسية مفتوحة المصدر (Python Flask & SQLite) تتسم بخفة الوزن، سهولة النشر، وانعدام تكاليف التراخيص، مع أداء فائق في معالجة الطلبات المتزامنة.\n"
        "2. الجدوى الاقتصادية (Economic Feasibility): يحقق النظام نموذج عمل رابحاً لكافة الأطراف (Win-Win Model)؛ تسترد المطاعم جزءاً من تكلفة التشغيل، ويوفر المستهلكون 50-70% من النفقات، وتوفر الجمعيات وجبات مجانية بالكامل.\n"
        "3. الجدوى التشغيلية والقانونية (Operational & Legal Feasibility): النظام يحترم خصوصية المستخدمين عبر تشفير كلمات المرور، ويوفر مسار تحقق بالكود يضمن عدم تلاعب أي طرف بالمخزون."
    )

    add_custom_heading("2.2 المتطلبات الوظيفية (Functional Requirements)", 2)
    add_arabic_paragraph(
        "تم تصنيف المتطلبات الوظيفية للنظام وفق أدوار المستخدمين الأربعة (RBAC):\n"
        "• متطلبات إدارة المنصة (Admin):\n"
        "  - إدارة الحسابات، مراجعة الصلاحيات، وحذف أو تجميد أي حساب مخالف.\n"
        "  - استعراض لوحة التحليلات المتقدمة والرسوم البيانية (Chart.js).\n"
        "  - تصدير التقارير التدقيقية الشاملة بصيغة CSV لكافة عمليات المنصة.\n"
        "• متطلبات المنشآت الغذائية (Restaurants & Bakeries):\n"
        "  - إضافة وجبات جديدة (الاسم، التصنيف، السعر الأصلي والمخفض، الكمية المتاحة، ووقت الاستلام).\n"
        "  - تعديل وحذف الوجبات وتحديث الأسعار لحظيّاً عبر حاسبة الخصم الفورية.\n"
        "  - التحقق السريع من كود الحجز (Verify Order) لتسليم الطلب.\n"
        "• متطلبات المستهلكين (Customers):\n"
        "  - تصفح الوجبات وفلترتها حسب التصنيف والحي السكني.\n"
        "  - حجز الوجبات وتحديد الكمية (1، 2، 3...) واختيار الاستلام من المحل أو التوصيل المنزلي.\n"
        "  - استلام كود الحجز الفريد وإمكانية إلغاء الطلب قبل موعد الاستلام.\n"
        "• متطلبات الجمعيات الخيرية (Charities):\n"
        "  - الحجز الحصري لعروض التبرع الإغاثي المجاني (بقيمة صفر جنيه).\n"
        "  - استعراض لوحة الجمعية الخاصة وإحصائيات الأسر المستفيدة.\n"
        "  - طباعة شهادة الأثر المجتمعي الرسمية المعتمدة (CSR Certificate) كـ PDF."
    )

    add_custom_heading("2.3 المتطلبات غير الوظيفية (Non-Functional Requirements)", 2)
    add_arabic_paragraph(
        "• الأمان (Security): تشفير أحادي الاتجاه لكلمات المرور باستخدام خوارزمية Scrypt مع اشتراط ألا تقل كلمة المرور عن 8 خانات.\n"
        "• التجاوبية (Responsiveness): واجهات متوافقة 100% مع الهواتف الذكية وشاشات الحواسيب بنظام Bootstrap 5 RTL.\n"
        "• الأداء والسرعة (Performance): استجابة فورية للصفحات وحركات تمرير انسيابية بفضل مكتبات Lenis و GSAP.\n"
        "• الموثوقية وتكامل البيانات (Data Integrity): فرض قيود المفاتيح الأجنبية (Foreign Keys) لمنع أي تضارب في المخزون أو الطلبات."
    )

    doc.add_page_break()

    # ==================== الفصل الثالث ====================
    add_custom_heading("الفصل الثالث: تحليل وتصميم النظم (System Analysis & Design)", 1)

    add_custom_heading("3.1 معمارية النظام (MVC Pattern)", 2)
    add_arabic_paragraph(
        "تم تبني نمط Model-View-Controller المعياري لضمان فصل الاهتمامات (Separation of Concerns):\n"
        "• Model: طبقة قاعدة البيانات العلائقية SQLite وتتضمن جداول users, meals, orders.\n"
        "• View: قوالب Jinja2 المعيارية التي تفصل منطق العرض عن كود الباك إند وتضمن تجربة استخدام حديثة.\n"
        "• Controller: مسارات Flask (app.py) التي تتحكم في منطق الأعمال والتحقق والصلاحيات وحسابات الأثر."
    )

    add_custom_heading("3.2 قاموس قاعدة البيانات (Data Dictionary)", 2)
    
    # جدول توصيف البيانات
    table_db = doc.add_table(rows=1, cols=4)
    table_db.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table_db.rows[0].cells
    headers = ["الوصف والقيود", "نوع البيان", "اسم الحقل", "اسم الجدول"]
    for i, h in enumerate(headers):
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(hdr[i], '047857')
        r = hdr[i].paragraphs[0].add_run(h)
        r.bold = True
        r.font.name = 'Cairo'
        r.font.color.rgb = C_WHITE

    fields_data = [
        ("users", "id", "INTEGER", "المعرف الفريد للمستخدم (Primary Key, Auto Increment)"),
        ("users", "username", "TEXT", "اسم الدخول الفريد (Unique Constraint)"),
        ("users", "password_hash", "TEXT", "تشفير كلمة المرور بخوارزمية Scrypt"),
        ("users", "role", "TEXT", "دور المستخدم: admin, restaurant, charity, customer"),
        ("meals", "id", "INTEGER", "معرف الوجبة أو العرض (Primary Key)"),
        ("meals", "restaurant_id", "INTEGER", "رقم المطعم المالك (Foreign Key -> users.id)"),
        ("meals", "quantity", "INTEGER", "رصيد الوجبات المتبقية بالمخزون لحظيّاً"),
        ("meals", "is_charity", "INTEGER", "نوع العرض: 0 بيع مخفض، 1 تبرع مجاني للجمعيات"),
        ("orders", "id", "INTEGER", "معرف الحجز (Primary Key)"),
        ("orders", "order_code", "TEXT", "كود الاستلام الفريد بصيغة ZAD-XXXXX (Unique)"),
        ("orders", "quantity", "INTEGER", "عدد الوجبات المطلوبة في الحجز (1، 2، 3...)"),
        ("orders", "status", "TEXT", "حالة الطلب: pending, completed, cancelled"),
        ("orders", "delivery_type", "TEXT", "طريقة الاستلام: pickup (محل) أو delivery (منزل)")
    ]

    for tbl, fld, tp, desc in fields_data:
        row = table_db.add_row().cells
        row[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        row[3].paragraphs[0].add_run(tbl)
        row[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row[2].paragraphs[0].add_run(fld)
        row[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row[1].paragraphs[0].add_run(tp)
        row[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        row[0].paragraphs[0].add_run(desc)

    doc.add_page_break()

    # ==================== الفصل الرابع ====================
    add_custom_heading("الفصل الرابع: التنفيذ البرمجي والبنية التقنية", 1)

    add_custom_heading("4.1 حزمة التطوير البرمجية (Technology Stack)", 2)
    add_arabic_paragraph(
        "• لغة البرمجة: Python 3.13 — خيار مثالي يجمع بين القوة البرمجية، سرعة المعالجة، ودعم خوارزميات الذكاء الاصطناعي وتحليل البيانات.\n"
        "• إطار العمل: Flask 3.1.0 — يتميز بالمرونة العالية والمعمارية الخفيفة لخدمة تطبيقات الويب والـ RESTful APIs.\n"
        "• محرك قواعد البيانات: SQLite 3 — قاعدة بيانات مدمجة توفر استقراراً عالياً ودعماً كاملاً لمعاملات ACID.\n"
        "• الواجهة الأمامية (Frontend): Bootstrap 5 RTL, HTML5, CSS3, JavaScript ES6.\n"
        "• محركات الأنيميشن: GSAP 3.12 (GreenSock) و Lenis Smooth Scroll لتوفير تجربة مستخدم عصرية تنافس التطبيقات العالمية."
    )

    add_custom_heading("4.2 خوارزمية التحكم في المخزون والأكواد الفريدة", 2)
    add_arabic_paragraph(
        "تعتمد المنصة خوارزمية متزامنة لمنع التعارض في حجز الكميات (Concurrency Control & Unique Code Generation):\n"
        "1. استقبال الكمية المدخلة والتحقق من تطهيرها ضد أي رموز غير رقمية، مع دعم كامل لتحويل الأرقام العربية المشرقية (٠١٢٣٤٥٦٧٨٩) إلى أرقام قياسية.\n"
        "2. التأكد من أن الكمية المطلوبة أقل من أو تساوي الكمية المتاحة لدى المطعم.\n"
        "3. توليد كود حجز فريد عشوائي مشفر بنظام الأحرف الكبيرة والأرقام (مثال: ZAD-90BBY) عبر خوارزمية التوليد الآمن.\n"
        "4. خصم الكمية في معاملة قاعدة بيانات فورية، وتحديث حالة الوجبة تلقائياً إلى 'نفدت الكمية' إذا أصبح الرصيد صفراً."
    )

    doc.add_page_break()

    # ==================== الفصل الخامس ====================
    add_custom_heading("الفصل الخامس: نظم دعم القرار الإداري (MIS DSS) والأثر البيئي", 1)

    add_custom_heading("5.1 مفهوم نظام دعم القرار في منصة زاد", 2)
    add_arabic_paragraph(
        "يمثل نظام دعم القرار (Decision Support System - DSS) في منصة زاد جوهر تخصص نظم المعلومات الإدارية، "
        "حيث لا يقتصر دور النظام على تسجيل المعاملات (TPS)، بل يقوم بتحويل تلك البيانات التشغيلية إلى معلومات تحليلية تدعم اتخاذ القرار الاستراتيجي:\n"
        "• تحليل سلاسل الإمداد ومعدل الإنجاز (Fulfillment Rate %): رصد نسبة الطلبات المكتملة مقارنة بالمعلقة والملغاة.\n"
        "• رصد الصنف الأكثر عرضة للهدر (Peak Waste Category): كشف الأصناف الغذائية الأكثر تسجيلاً كفوائض لتوجيه المنشآت بتقديم خصومات مسائية مبكرة.\n"
        "• التحليل التراكمي للنمو الزمني: تتبع حجم الفوائض على مدار الأيام عبر الرسوم البيانية المتصلة."
    )

    add_custom_heading("5.2 النموذج الرياضي لحساب الأثر البيئي والمجتمعي", 2)
    add_callout_box(
        "المعادلات العلمية المعتمدة لحساب الأثر البيئي:\n"
        "• وزن الطعام المنقذ = عدد الوجبات المنقذة × 0.45 كجم\n"
        "• مكافئ الكربون الموفر (CO2e Saved) = وزن الطعام المنقذ × 2.5 كجم كربون متجنب\n"
        "• المياه الافتراضية الموفرة (Virtual Water Saved) = وزن الطعام المنقذ × 1000 لتر ماء\n"
        "• الأسر المستفيدة المقدرة = إجمالي الوجبات الإغاثية ÷ 3 وجبات لكل أسرة",
        "المعادلات المعتمدة دولياً من منظمة FAO وبرنامج UNEP"
    )

    doc.add_page_break()

    # ==================== الفصل السادس ====================
    add_custom_heading("الفصل السادس: الاختبار وضمان الجودة (Testing & QA)", 1)

    add_custom_heading("6.1 منهجية الاختبار المتبعة", 2)
    add_arabic_paragraph(
        "تم إخضاع النظام لاختبارات صارمة على مستويات متعددة لضمان استقرار العمليات البرمجية:\n"
        "1. اختبار الوحدات (Unit Testing): اختبار دوال التشفير، معادلات الأثر البيئي، وتوليد الأكواد الفريدة.\n"
        "2. اختبار التكامل (Integration Testing): التأكد من ربط المسارات بين السيرفر وقاعدة البيانات وقوالب العرض.\n"
        "3. اختبار النظام الشامل (End-to-End Testing): محاكاة سيناريوهات حقيقية لكافة أطراف المنصة (حجز، تحقق، إلغاء، وإعادة مخزون)."
    )

    # جدول حالات الاختبار
    table_test = doc.add_table(rows=1, cols=4)
    table_test.alignment = WD_TABLE_ALIGNMENT.CENTER
    thdr = table_test.rows[0].cells
    theaders = ["النتيجة المحققة", "النتيجة المتوقعة", "الإجراء والمدخلات", "رقم الحالة"]
    for i, th in enumerate(theaders):
        thdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(thdr[i], '047857')
        r = thdr[i].paragraphs[0].add_run(th)
        r.bold = True
        r.font.name = 'Cairo'
        r.font.color.rgb = C_WHITE

    test_cases = [
        ("TC-01", "تسجيل حساب بباسورد أقل من 8 خانات", "رفض التسجيل مع تنبيه بضرورة 8 خانات كحد أدنى", "ناجح ومطابق ✅"),
        ("TC-02", "حجز وجبة بعدد وحدات متعدد (3 وجبات)", "خصم 3 وجبات من رصيد المطعم وحساب السعر × 3", "ناجح ومطابق ✅"),
        ("TC-03", "محاولة مطعم حجز وجبة لنفسه أو لغيره", "رفض العملية وحصر الحجز على حسابات المشترين فقط", "ناجح ومطابق ✅"),
        ("TC-04", "حجز تبرع خيري مجاني بحساب مستهلك عادي", "حظر العملية والتنبيه بأن التبرع حصري للجمعيات", "ناجح ومطابق ✅"),
        ("TC-05", "إلغاء حجز معلق من قبل العميل", "تحويل الطلب لـ 'ملغي' وإعادة الكمية لرصيد المطعم", "ناجح ومطابق ✅")
    ]

    for c_id, act, exp, res in test_cases:
        row = table_test.add_row().cells
        row[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row[3].paragraphs[0].add_run(c_id)
        row[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        row[2].paragraphs[0].add_run(act)
        row[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        row[1].paragraphs[0].add_run(exp)
        row[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row[0].paragraphs[0].add_run(res)

    doc.add_page_break()

    # ==================== الفصل السابع والمراجع ====================
    add_custom_heading("الفصل السابع: الخاتمة والتوصيات المستقبلية", 1)
    add_arabic_paragraph(
        "أثبت مشروع 'منصة زَادْ (ZAD)' التطبيق العملي لمفاهيم نظم المعلومات الإدارية في حل مشكلات واقعية ذات بعد اقتصادي واجتماعي وبيئي معقد. "
        "نجحت المنصة في تحويل ما كان يُعتبر هدراً وخسارة إلى منفعة متبادلة وتكافل إنساني مستدام، مقدمةً دليلاً على أن الحلول الرقمية المبتكرة هي عصب التنمية الشاملة."
    )

    add_custom_heading("7.1 التوصيات والتطلعات المستقبلية", 2)
    add_arabic_paragraph(
        "• إطلاق تطبيق مخصص للهواتف الذكية (Native Mobile App) لتعزيز الإشعارات اللحظية عبر تقنية Push Notifications.\n"
        "• إدماج بوابات الدفع الإلكتروني والمحافظ الذكية (e-Wallets / Fawry / Vodafone Cash) لتوسيع خيارات الدفع إلى جانب الكاش.\n"
        "• تفعيل نماذج التنبؤ بالذكاء الاصطناعي (AI Waste Prediction) لمساعدة المطاعم في تقدير كميات الفوائض المتوقعة مسبقاً قبل حدوثها."
    )

    add_custom_heading("قائمة المراجع والمصادر (References)", 1)
    add_arabic_paragraph(
        "1. منظمة الأغذية والزراعة للأمم المتحدة (FAO) — تقرير حالة انعدام الأمن الغذائي والفاقد والمهدر من الأغذية، 2023.\n"
        "2. برنامج الأمم المتحدة للبيئة (UNEP) — مؤشر هدر الأغذية العالمي ودليل مكافحة الانبعاثات، 2024.\n"
        "3. د. أحمد فؤاد سلامة — نظم المعلومات الإدارية: المفهوم والتطبيق ونظم دعم القرار، دار الفكر العربي، القاهرة.\n"
        "4. Kenneth C. Laudon & Jane P. Laudon — Management Information Systems: Managing the Digital Firm, 17th Edition, Pearson, 2022.\n"
        "5. Miguel Grinberg — Flask Web Development: Developing Web Applications with Python, 2nd Edition, O'Reilly Media, 2018."
    )

    # حفظ الملف في مجلد المشروع وعلى سطح المكتب
    path1 = r"C:\Users\Administrator\Desktop\zad_food_rescue\توثيق_مشروع_التخرج_منصة_زاد.docx"
    path2 = r"C:\Users\Administrator\Desktop\توثيق_مشروع_التخرج_منصة_زاد.docx"
    doc.save(path1)
    doc.save(path2)
    print("Documentation docx successfully generated at:")
    print(" -", path1)
    print(" -", path2)

if __name__ == "__main__":
    create_graduation_doc()
