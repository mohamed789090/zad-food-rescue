import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_zad_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # الألوان الرسمية للمنصة
    C_DARK_GREEN = RGBColor(4, 78, 55)     # #047857
    C_DEEP_BG    = RGBColor(2, 44, 34)     # #022c22
    C_AMBER      = RGBColor(217, 119, 6)   # #d97706
    C_LIGHT_BG   = RGBColor(248, 250, 252) # #f8fafc
    C_WHITE      = RGBColor(255, 255, 255)
    C_DARK_TEXT  = RGBColor(30, 41, 59)
    C_MUTED_TEXT = RGBColor(100, 116, 139)
    C_CARD_BG    = RGBColor(255, 255, 255)
    C_CARD_BORDER= RGBColor(226, 232, 240)
    C_SUCCESS_BG = RGBColor(236, 253, 245)

    blank_layout = prs.slide_layouts[6]

    def set_slide_bg(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text="مشروع تخرج نظم ومعلومات إدارية 2026"):
        # شريط الهيدر العلوي
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.3))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = C_DARK_GREEN
        header_shape.line.fill.background()

        # التصنيف / التخصص
        tx1 = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.35))
        tf1 = tx1.text_frame
        p1 = tf1.paragraphs[0]
        p1.text = category_text
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = C_AMBER
        p1.alignment = PP_ALIGN.RIGHT

        # عنوان الشريحة الرئيسي
        tx2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.7), Inches(0.75))
        tf2 = tx2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(25)
        p2.font.bold = True
        p2.font.color.rgb = C_WHITE
        p2.alignment = PP_ALIGN.RIGHT

    def add_card(slide, left, top, width, height, title, body_lines, accent_color=C_DARK_GREEN):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1.5)

        # شريط جانبي ملون
        side_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + width - Inches(0.15), top, Inches(0.15), height)
        side_bar.fill.solid()
        side_bar.fill.fore_color.rgb = accent_color
        side_bar.line.fill.background()

        # النص داخل الكارت
        tx = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.45), height - Inches(0.4))
        tf = tx.text_frame
        tf.word_wrap = True

        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(18)
        p_title.font.bold = True
        p_title.font.color.rgb = accent_color
        p_title.alignment = PP_ALIGN.RIGHT

        for line in body_lines:
            p_line = tf.add_paragraph()
            p_line.text = line
            p_line.font.size = Pt(13.5)
            p_line.font.color.rgb = C_DARK_TEXT
            p_line.alignment = PP_ALIGN.RIGHT
            p_line.space_before = Pt(6)

    # ==================== SLIDE 1: Cover Slide ====================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, C_DEEP_BG)

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.333), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p1_badge = tf1.paragraphs[0]
    p1_badge.text = "★ مشروع تخرج نظم ومعلومات إدارية (MIS) — العام الجامعي 2026 ★"
    p1_badge.font.size = Pt(17)
    p1_badge.font.bold = True
    p1_badge.font.color.rgb = C_AMBER
    p1_badge.alignment = PP_ALIGN.CENTER

    p1_title = tf1.add_paragraph()
    p1_title.text = "مَنَصَّة زَادْ (ZAD)"
    p1_title.font.size = Pt(56)
    p1_title.font.bold = True
    p1_title.font.color.rgb = C_WHITE
    p1_title.alignment = PP_ALIGN.CENTER
    p1_title.space_before = Pt(14)

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "نظام رقمي متكامل لإدارة سلاسل إنقاذ فوائض الطعام، الاستدامة البيئية، والتكافل المجتمعي"
    p1_sub.font.size = Pt(21)
    p1_sub.font.color.rgb = RGBColor(167, 243, 208)
    p1_sub.alignment = PP_ALIGN.CENTER
    p1_sub.space_before = Pt(10)

    p1_team = tf1.add_paragraph()
    p1_team.text = "إعداد وتطوير: فريق عمل طلاب قسم نظم المعلومات الإدارية\\nتحت إشراف: لجنة الأساتذة المشرفين والمحكمين"
    p1_team.font.size = Pt(16)
    p1_team.font.color.rgb = C_WHITE
    p1_team.alignment = PP_ALIGN.CENTER
    p1_team.space_before = Pt(30)

    # ==================== SLIDE 2: Problem Statement ====================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2, C_LIGHT_BG)
    add_header(s2, "المشكلة والدافع لدراسة المشروع (Problem Statement)")

    add_card(s2, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0),
             "1. حجم الهدر الغذائي في السوق المحلي",
             [
                 "• تشير الإحصائيات إلى هدر ما يقرب من 9 ملايين طن من الأطعمة الصالحة سنويّاً في مصر.",
                 "• تعاني قطاعات المطاعم، المخابز، ومحلات الحلويات من فوائض يومية طازجة تضطر للتخلص منها عند نهاية ساعات العمل.",
                 "• غياب نظام لوجستي وتقني يربط هذه المنشآت بالمستهلكين المحيطين أو الجمعيات الإغاثية في الوقت الفعلي (Real-Time)."
             ], accent_color=RGBColor(239, 68, 68))

    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "2. التداعيات الاقتصادية والبيئية للهدر",
             [
                 "• خسائر مالية فادحة تتكبدها المنشآت الغذائية في تكاليف الإنتاج غير المستردة.",
                 "• ارتفاع انبعاثات غاز الميثان ومكافئ الكربون (CO2e) الناتج عن تحلل الأغذية في مدافن النفايات.",
                 "• استنزاف مليارات الأمتار المكعبة من البصمة المائية الافتراضية المستهلكة في ري وإنتاج تلك الأطعمة.",
                 "• وجود فجوة اجتماعية بين وفرة الفوائض وحاجة الأسر المتعففة للغذاء."
             ], accent_color=C_AMBER)

    # ==================== SLIDE 3: The Solution & Vision ====================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3, C_LIGHT_BG)
    add_header(s3, "فكرة الحل ورسالة منصة زَادْ (The Solution & Vision)")

    add_card(s3, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0),
             "💡 ما هي منصة زاد (ZAD)؟",
             [
                 "• منصة سحابية تفاعلية تمثل وسيطاً ذكيّاً (Smart Intermediary) بين المنشآت الغذائية، المستهلكين، والجمعيات الخيرية.",
                 "• تتيح للمطاعم والمخابز عرض وجبات الفائض المسائية الطازجة بنسبة خصم تصل إلى 70% للجمهور لإنقاذها من الإتلاف.",
                 "• توفر مساراً حصريّاً للتبرع الخيري المجاني بنسبة 100% للجمعيات الخيرية والمبادرات الإغاثية المعتمدة.",
                 "• تحويل الفاقد الغذائي من تكلفة بيئية ومالية إلى قيمة اقتصادية ومجتمعية مستدامة."
             ], accent_color=C_DARK_GREEN)

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "🎯 القيمة المضافة ونموذج العمل (Value Proposition)",
             [
                 "• للمطاعم: استرداد تكاليف الإنتاج، تحقيق التزام بيئي، والوصول لعملاء جدد في الحي السكني.",
                 "• للمستهلكين: الحصول على وجبات طازجة عالية الجودة بأسعار توفير استثنائية تناسب الظروف الاقتصادية.",
                 "• للجمعيات الخيرية: توفير وجبات إطعام مجانية موثقة بالكود للأسر المستحقة دون أعباء تمويلية.",
                 "• للبيئة والمجتمع: تقليل انبعاثات غازات الاحتباس الحراري وتوفير المياه العذبة."
             ], accent_color=C_AMBER)

    # ==================== SLIDE 4: UN SDGs Alignment ====================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4, C_LIGHT_BG)
    add_header(s4, "التوافق مع أهداف التنمية المستدامة (UN SDGs Alignment)")

    add_card(s4, Inches(8.9), Inches(1.8), Inches(3.7), Inches(5.0),
             "الهدف 2: القضاء على الجوع",
             [
                 "• Zero Hunger (SDG 2)",
                 "• ربط التبرعات الفائضة بشبكة الجمعيات الخيرية والمبادرات الأهلية المعتمدة.",
                 "• مساهمة فعلية في تأمين وجبات الإطعام اليومية للأسر المتعففة وتوسيع نطاق التكافل الاجتماعي."
             ], accent_color=RGBColor(217, 119, 6))

    add_card(s4, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.0),
             "الهدف 12: الاستهلاك والإنتاج المسئول",
             [
                 "• Responsible Consumption & Production",
                 "• خفض معدلات هدر الأغذية وسلاسل التوريد وفق المستهدف العالمي 12.3.",
                 "• تحفيز السلوك الاستهلاكي الرشيد وثقافة حفظ النعمة ومكافحة الإسراف."
             ], accent_color=C_DARK_GREEN)

    add_card(s4, Inches(0.7), Inches(1.8), Inches(3.7), Inches(5.0),
             "الهدف 13: العمل المناخي",
             [
                 "• Climate Action (SDG 13)",
                 "• خفض انبعاثات مكافئ غاز ثاني أكسيد الكربون (CO2e) الناتج عن تحلل المخلفات العضوية.",
                 "• خفض البصمة المائية وحماية الموارد الطبيعية الحيوية للأجيال القادمة."
             ], accent_color=RGBColor(37, 99, 235))

    # ==================== SLIDE 5: Ecosystem & Stakeholders ====================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5, C_LIGHT_BG)
    add_header(s5, "أصحاب المصلحة وتعدد الأدوار (Multi-Role Ecosystem)")

    add_card(s5, Inches(6.9), Inches(1.8), Inches(5.6), Inches(2.4),
             "🏪 منشآت الأغذية (المطاعم والمخابز)",
             [
                 "• رفع وجبات وعروض الفوائض بنوعيها (بيع مخفض أو تبرع خيري).",
                 "• تحديد الكمية المتاحة، السعر، ووقت الاستلام بدقة.",
                 "• التحقق الفوري من أكواد الحجز وتأكيد تسليم الطلبات."
             ], accent_color=C_DARK_GREEN)

    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.4),
             "🤝 الجمعيات الخيرية والمؤسسات الإغاثية",
             [
                 "• حجز حصري لعروض التبرع المجاني بقيمة 0 جنيه.",
                 "• لوحة تحكم مخصصة ترصد الوجبات الإغاثية والأسر المستفيدة.",
                 "• طباعة شهادة أثر مجتمعي وتكافل معتمدة رسمياً."
             ], accent_color=RGBColor(220, 38, 38))

    add_card(s5, Inches(6.9), Inches(4.4), Inches(5.6), Inches(2.4),
             "🛍️ المستهلكون والمشترون (Customers)",
             [
                 "• تصفح الوجبات المخفضة بحسب الحي السكني والتصنيف.",
                 "• حجز مرن يتيح تحديد عدد الوجبات (1، 2، 3...).",
                 "• الاختيار بين الاستلام الذاتي المجاني أو التوصيل المنزلي."
             ], accent_color=C_AMBER)

    add_card(s5, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.4),
             "⚙️ إدارة المنصة وصناع القرار (Admin)",
             [
                 "• إدارة الحسابات، ضبط الصلاحيات، والرقابة الأمنية (RBAC).",
                 "• لوحة تحليلات نظم دعم القرار (MIS Decision Support System).",
                 "• تصدير تقارير تدقيق شاملة بصيغة CSV لكافة العمليات."
             ], accent_color=RGBColor(59, 130, 246))

    # ==================== SLIDE 6: Order Lifecycle ====================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6, C_LIGHT_BG)
    add_header(s6, "دورة حياة الحجز والتسليم (End-to-End Order Lifecycle)")

    add_card(s6, Inches(9.8), Inches(1.8), Inches(2.8), Inches(5.0),
             "المرحلة 1: الطرح والعرض",
             [
                 "• يرفع المطعم الفائض المسائي.",
                 "• تحديد التصنيف (مخبوزات، وجبات، حلويات...).",
                 "• تحديد السعر ووقت الاستلام.",
                 "• إطلاق مؤقت العد التنازلي الحي للإغلاق."
             ], accent_color=C_DARK_GREEN)

    add_card(s6, Inches(6.8), Inches(1.8), Inches(2.8), Inches(5.0),
             "المرحلة 2: الحجز والخصم",
             [
                 "• يختار العميل عدد الوحدات.",
                 "• يختار طريقة الاستلام (محل أو دليفري).",
                 "• خصم فوري متزامن من رصيد المطعم في المخزون.",
                 "• توليد كود حجز فريد ZAD-XXXXX."
             ], accent_color=C_AMBER)

    add_card(s6, Inches(3.8), Inches(1.8), Inches(2.8), Inches(5.0),
             "المرحلة 3: التحقق والتسليم",
             [
                 "• يتوجه العميل للمطعم ويظهر الكود للكاشير ويسدد نقداً.",
                 "• يدخل الكاشير الكود في صندوق التحقق باللوحة.",
                 "• تتحول حالة الطلب فورياً إلى 'تم التسليم بنجاح'."
             ], accent_color=RGBColor(37, 99, 235))

    add_card(s6, Inches(0.8), Inches(1.8), Inches(2.8), Inches(5.0),
             "المرحلة 4: الأثر وإعادة التدوير",
             [
                 "• حساب الأثر البيئي للكربون والماء الموفرين لحظيّاً.",
                 "• مسار إلغاء مرن يعيد الوجبات تلقائيّاً لرصيد المطعم في حال تعذر حضور العميل لمنع الهدر."
             ], accent_color=RGBColor(16, 185, 129))

    # ==================== SLIDE 7: Unique Functional Features ====================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7, C_LIGHT_BG)
    add_header(s7, "الميزات الوظيفية المتقدمة بالمنصة (Key Advanced Features)")

    add_card(s7, Inches(6.9), Inches(1.8), Inches(5.6), Inches(2.4),
             "⏳ مؤقت العد التنازلي الحي (Surplus Countdown)",
             [
                 "• عداد زمني رقمي بالثواني يحسب الوقت المتبقي لإغلاق العرض.",
                 "• تعزيز سرعة اتخاذ القرار لدى العميل لإنقاذ الوجبة (Urgency & FOMO).",
                 "• استمرارية العداد عبر التخزين المحلي (localStorage)."
             ], accent_color=RGBColor(220, 38, 38))

    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.4),
             "📦 الحجز المرن والتوصيل (Multi-Qty & Delivery)",
             [
                 "• إمكانية تحديد كميات متعددة (1، 2، 3 وجبات) بنقرة زر.",
                 "• خيار الاستلام من المحل كاش أو التوصيل المنزلي (+20 ج.م).",
                 "• دعم كامل ودقيق للأرقام الإنجليزية والعربية المشرقية."
             ], accent_color=C_DARK_GREEN)

    add_card(s7, Inches(6.9), Inches(4.4), Inches(5.6), Inches(2.4),
             "🔒 منظومة الأمان وحماية الهوية (Security & RBAC)",
             [
                 "• شرط أمني صارم لقوة كلمة المرور (ألا تقل عن 8 خانات).",
                 "• زر إظهار وإخفاء الباسورد 👁️ لتسهيل التحقق على المستخدم.",
                 "• تشفير غير قابل للفك لكافة كلمات المرور بخوارزمية Scrypt."
             ], accent_color=RGBColor(59, 130, 246))

    add_card(s7, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.4),
             "🔄 الإلغاء الذكي وإعادة المخزون (Smart Restocking)",
             [
                 "• إتاحة إلغاء الحجز للعميل في حال الطوارئ قبل الموعد.",
                 "• إعادة الكمية تلقائيّاً لرصيد الوجبة المتاح لعدم تفويت فرصة إنقاذها.",
                 "• إشعارات منبثقة عائمة (Floating Toasts) لتأكيد الإجراءات."
             ], accent_color=C_AMBER)

    # ==================== SLIDE 8: Charity Dashboard & Certificate ====================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8, C_LIGHT_BG)
    add_header(s8, "بوابة الجمعيات الخيرية وشهادة الأثر (Charity Portal & CSR Award)")

    add_card(s8, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0),
             "🤝 لوحة تحكم مخصصة للمؤسسات الإغاثية",
             [
                 "• لوحة مستقلة تماماً تلبي متطلبات إدارة العمل الخيري المؤسسي.",
                 "• رصد إجمالي الوجبات الإغاثية المستلمة وتوزيعها جغرافياً.",
                 "• حاسبة تقديرية لعدد الأسر المستفيدة (بمعادلة ذكية لتغطية الأسرة).",
                 "• احتساب القيمة السوقية التقديرية للطعام الموزع مجاناً بالجنيه.",
                 "• جدول تتبع التبرعات الجارية في انتظار توجه المندوب للاستلام بالكود."
             ], accent_color=RGBColor(220, 38, 38))

    add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "🏆 شهادة الأثر والتكافل المجتمعي الرسمية (Printable)",
             [
                 "• وثيقة شرفية معتمدة بإطار ذهبي وشعار مائي وعلامة اعتماد رقمية.",
                 "• تتضمن كود الاعتماد الموثق، تاريخ الإصدار، واسم الجمعية الشريكة.",
                 "• توثق أرقام الوجبات المنقذة ومكافئ الكربون والماء الموفرين.",
                 "• مجهزة بتقنيات الطباعة الحصرية (@media print) للطباعة المباشرة بحجم A4 أو الحفظ كـ PDF لتقديمها للجهات المانحة والمشرفة."
             ], accent_color=C_AMBER)

    # ==================== SLIDE 9: MIS Decision Support System (DSS) ====================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9, C_LIGHT_BG)
    add_header(s9, "نظم دعم القرار الإداري والتحليلات (MIS DSS & Analytics)")

    add_card(s9, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0),
             "📊 الرسوم البيانية التفاعلية (Chart.js)",
             [
                 "• منحنى زمني متصل (Line Chart): يحلل نمو الحجوزات والعمليات عبر الأيام ويكشف أوقات الذروة الاستهلاكية.",
                 "• رسم دائري مفرغ (Doughnut Chart): يوضح الحصص النسبية لأصناف الفوائض (مخبوزات، وجبات، حلويات...).",
                 "• رسم شريطي لسلاسل الإمداد (Bar Chart): يقيس كفاءة إنجاز الطلبات (المكتملة بنجاح، المعلقة، والملغاة)."
             ], accent_color=RGBColor(37, 99, 235))

    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "🧠 وحدة دعم القرار الإداري والتوصيات (Executive DSS)",
             [
                 "• حساب مؤشر كفاءة التسليم الميداني (Fulfillment Success Rate %).",
                 "• رصد الصنف الأكثر عرضة للهدر تلقائيّاً من حركة المخزون.",
                 "• تقديم توصيات تنفيذية استراتيجية للإدارة لتوجيه المنشآت بتقديم خصومات مبكرة وتوسيع نطاق التغطية الجغرافية في المناطق الأكثر كثافة.",
                 "• تصدير تقارير تدقيق شاملة بصيغة CSV لإجراء التحليلات الإحصائية المتقدمة."
             ], accent_color=C_DARK_GREEN)

    # ==================== SLIDE 10: Environmental & Social Impact ====================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10, C_LIGHT_BG)
    add_header(s10, "احتساب مؤشرات الأثر البيئي والمجتمعي (Impact Metrics)")

    add_card(s10, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0),
             "🌱 المعادلات العلمية المعتمدة لحساب الأثر",
             [
                 "• تستند المنصة إلى معايير منظمة الأغذية والزراعة (FAO) وبرنامج البيئة (UNEP):",
                 "  - متوسط وزن الوجبة الغذائية = 0.45 كجم.",
                 "  - انبعاثات الكربون المتجنبة: كل 1 كجم طعام منقذ يمنع 2.5 كجم من مكافئ الكربون (CO2e).",
                 "  - البصمة المائية الموفرة: كل 1 كجم طعام منقذ يوفر 1000 لتر من المياه الافتراضية المستهلكة في الزراعة والإنتاج الحيواني.",
                 "• يتم تطبيق هذه المعادلات لحظيّاً فور تأكيد تسليم أي وجبة."
             ], accent_color=C_DARK_GREEN)

    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "📈 الإحصائيات التفاعلية المتصاعدة (CountUp Animations)",
             [
                 "• عرض الأرقام البيئية في كروت تفاعلية بارزة في واجهة الموقع.",
                 "• تشغيل عدادات تصاعدية تفاعلية (GSAP CountUp Animation) عند فتح الموقع لجذب انتباه المستهلك وإبراز أثر مساهمته.",
                 "• احتساب إجمالي الوفورات المالية التي حققها المستهلكون بالجنيه.",
                 "• مؤشر حي لعدد الأسر المستفيدة ومعدل خفض الهدر."
             ], accent_color=C_AMBER)

    # ==================== SLIDE 11: Technical Architecture ====================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11, C_LIGHT_BG)
    add_header(s11, "المعمارية التقنية وتكامل الأنظمة (System Architecture)")

    add_card(s11, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0),
             "⚙️ الباك إند وقواعد البيانات (Backend & Database)",
             [
                 "• Python 3.13 & Flask Framework: بنية سريعة وخفيفة وعالية الكفاءة.",
                 "• SQLite Relational Database: إدارة علائقية متماسكة بروابط Foreign Keys.",
                 "• Role-Based Access Control (RBAC): عزل أمني صارم بين أدوار النظام.",
                 "• Werkzeug Security Scrypt Hashing: تشفير كلمات المرور بأحدث المعايير.",
                 "• Jinja2 Templating: قوالب ديناميكية متقدمة بنظام الوراثة الموحد."
             ], accent_color=C_DARK_GREEN)

    add_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "🎨 الفرونت إند وتجربة المستخدم (Frontend & UI/UX)",
             [
                 "• Bootstrap 5 RTL: هيكل متجاوب بالكامل مع الهواتف الذكية والأجهزة اللوحية.",
                 "• GSAP 3.12 (GreenSock): محرك أنيميشن فائق السلاسة لظهور العناصر والكروت.",
                 "• Lenis Smooth Scrolling: حركة تمرير انسيابية عالية الجودة.",
                 "• Glassmorphism Design: تأثير الزجاج الشفاف الراقي في الهيدر والبطاقات.",
                 "• Font Awesome 6 & Google Cairo Font: أيقونات وخطوط عربية مريحة للعين."
             ], accent_color=RGBColor(37, 99, 235))

    # ==================== SLIDE 12: Conclusion & Future Work ====================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12, C_DEEP_BG)

    tb12 = s12.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    p12_badge = tf12.paragraphs[0]
    p12_badge.text = "★ الخاتمة والآفاق المستقبلية (Conclusion & Future Work) ★"
    p12_badge.font.size = Pt(18)
    p12_badge.font.bold = True
    p12_badge.font.color.rgb = C_AMBER
    p12_badge.alignment = PP_ALIGN.CENTER

    p12_t = tf12.add_paragraph()
    p12_t.text = "الخلاصة والنتائج المحققة"
    p12_t.font.size = Pt(36)
    p12_t.font.bold = True
    p12_t.font.color.rgb = C_WHITE
    p12_t.alignment = PP_ALIGN.CENTER
    p12_t.space_before = Pt(10)

    p12_lines = [
        "1. إثبات جدوى التحول الرقمي في تحويل فاقد الأغذية من تكلفة مهدرة إلى عائد اقتصادي ومجتمعي.",
        "2. بناء نظام معلومات إداري متكامل (MIS) يحقق أهداف التنمية المستدامة (SDGs) ويخدم 4 أطراف رئيسية بتناغم تام.",
        "3. تطوير تجربة مستخدم عالية الرفاهية (High-End UI/UX) تضمن سرعة الاستجابة وكفاءة العمليات الميدانية بالكود.",
        "4. الآفاق المستقبلية: إطلاق تطبيق الهاتف الذكي (Mobile App)، وتطبيق الدفع الإلكتروني عبر المحافظ الذكية (e-Wallets)."
    ]

    for line in p12_lines:
        p = tf12.add_paragraph()
        p.text = line
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.alignment = PP_ALIGN.CENTER
        p.space_before = Pt(8)

    p12_thanks = tf12.add_paragraph()
    p12_thanks.text = "\\nشكراً جزيلاً لحسن استماعكم، ونسعد بتلقي استفسارات وملاحظات لجنة المناقشة الكريمة 🌿"
    p12_thanks.font.size = Pt(18)
    p12_thanks.font.bold = True
    p12_thanks.font.color.rgb = RGBColor(167, 243, 208)
    p12_thanks.alignment = PP_ALIGN.CENTER

    # Save to both locations
    path1 = r"C:\Users\Administrator\Desktop\zad_food_rescue\عرض_مشروع_التخرج_منصة_زاد.pptx"
    path2 = r"C:\Users\Administrator\Desktop\عرض_مشروع_التخرج_منصة_زاد.pptx"

    prs.save(path1)
    prs.save(path2)
    print("Presentation successfully saved to:")
    print(" -", path1)
    print(" -", path2)

if __name__ == "__main__":
    build_zad_presentation()
