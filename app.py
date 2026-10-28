import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import cv2
import tempfile
import io

# إعدادات الصفحة
st.set_page_config(page_title="مولد بوسترات المشاريع الذكي", layout="centered", page_icon="🎨")

st.title("🎨 مولد بوسترات المشاريع التلقائي")
st.write("أداتك السريعة لتحويل التقارير، الفيديوهات، والصور إلى بوستر مشروع احترافي!")

st.divider()

# 1. نموذج إدخال البيانات والملفات
with st.form("poster_form"):
    st.subheader("1️⃣ بيانات المشروع والنصوص")
    project_title = st.text_input("عنوان المشروع", placeholder="مثلاً: نظام الإنقاذ الذكي للطوارئ")
    project_subtitle = st.text_input("الشعار أو الفكرة الرئيسية", placeholder="مثلاً: حلول مبتكرة للاستجابة السريعة")
    
    report_text = st.text_area(
        "مستخرج التقرير أو الوصف (اكتبي النقاط في أسطر أو مفصولة بنقاط)", 
        placeholder="• الهدف من المشروع...\n• أهم المميزات والتقنيات المستعملة...\n• النتائج والتوصيات..."
    )

    st.subheader("2️⃣ المرفقات البصرية (فيديو أو صور)")
    uploaded_video = st.file_uploader("ارفعي فيديو للمشروع (استخراج لقطة تلقائية)", type=["mp4", "mov", "avi"])
    uploaded_image = st.file_uploader("أو ارفعي صورة مباشرة للمشروع", type=["png", "jpg", "jpeg"])

    st.subheader("3️⃣ الطابع والتنسيق")
    theme_choice = st.selectbox("اختر ثيم الألوان", ["أزرق داكن (تقني)", "بنفسجي إبداعي", "أخضر بيئي"])
    
    submitted = st.form_submit_button("🚀 توليد البوستر الآن")

# دالة معالجة واستخراج إطار من الفيديو
def extract_frame_from_video(video_file):
    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(video_file.read())
        cap = cv2.VideoCapture(tfile.name)
        
        # الانتقال لمنتصف الفيديو للحصول على إطار واضح
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
            
        success, frame = cap.read()
        cap.release()
        
        if success:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الفيديو: {e}")
    return None

# دالة إنشاء وتصميم البوستر
def create_poster(title, subtitle, text, main_img, theme):
    # أبعاد البوستر (قياسي للطباعة والعرض 1080 × 1350)
    width, height = 1080, 1350
    
    # ضبط خيارات الألوان حسب الثيم
    if theme == "أزرق داكن (تقني)":
        bg_color = (15, 23, 42)
        accent_color = (56, 189, 248)
        text_color = (241, 245, 249)
        card_bg = (30, 41, 59)
    elif theme == "بنفسجي إبداعي":
        bg_color = (30, 27, 75)
        accent_color = (168, 85, 247)
        text_color = (250, 245, 255)
        card_bg = (49, 46, 129)
    else:  # أخضر بيئي
        bg_color = (6, 78, 59)
        accent_color = (52, 211, 153)
        text_color = (236, 253, 245)
        card_bg = (4, 120, 87)

    # إنشاء كانفاس البوستر
    poster = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(poster)
    
    # تحضير الخطوط (الافتراضية في حال عدم توفر خط مخصص)
    try:
        font_title = ImageFont.truetype("arial.ttf", 55)
        font_sub = ImageFont.truetype("arial.ttf", 32)
        font_body = ImageFont.truetype("arial.ttf", 28)
    except:
        font_title = font_sub = font_body = ImageFont.load_default()

    # رسم إطار ورأس البوستر
    draw.rectangle([40, 40, width - 40, height - 40], outline=accent_color, width=4)
    
    # 1. عنوان المشروع
    draw.text((80, 80), title, fill=accent_color, font=font_title)
    if subtitle:
        draw.text((80, 150), subtitle, fill=text_color, font=font_sub)
        
    y_cursor = 220

    # 2. إدراج الصورة المرفوعة أو المستخرجة من الفيديو إن وجدت
    if main_img:
        # تغيير حجم الصورة لتناسب تصميم البوستر
        img_aspect = main_img.width / main_img.height
        target_w = width - 160
        target_h = int(target_w / img_aspect)
        
        # تقييد أقصى ارتفاع للصورة
        if target_h > 450:
            target_h = 450
            target_w = int(target_h * img_aspect)
            
        resized_img = main_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # وضع الصورة في المنتصف
        x_pos = (width - target_w) // 2
        poster.paste(resized_img, (x_pos, y_cursor))
        
        # رسم إطار حول الصورة
        draw.rectangle([x_pos - 2, y_cursor - 2, x_pos + target_w + 2, y_cursor + target_h + 2], outline=accent_color, width=2)
        y_cursor += target_h + 40

    # 3. خلفية مربع النصوص والتقرير
    card_box = [70, y_cursor, width - 70, height - 120]
    draw.rectangle(card_box, fill=card_bg, outline=accent_color, width=1)

    # 4. إضافة المحتوى النصي
    text_y = y_cursor + 30
    lines = text.split('\n')
    for line in lines:
        if line.strip():
            draw.text((100, text_y), line.strip(), fill=text_color, font=font_body)
            text_y += 45
            if text_y > height - 150:  # منع التداخل في الأسفل
                break

    # 5. التذييل الحقوقي
    draw.text((80, height - 90), "تم الإنشاء بواسطة: مولد بوسترات المشاريع الذكي", fill=accent_color, font=font_sub)

    return poster

# 3. عند الضغط على زر التوليد
if submitted:
    if not project_title or not report_text:
        st.warning("⚠️ يرجى كتابة عنوان المشروع ونظرة عامة عن التقرير على الأقل.")
    else:
        with st.spinner("⏳ جاري تحليل المرفقات وتنسيق البوستر..."):
            project_image = None
            
            # معالجة المرفقات (الصورة لها الأولوية ثم الفيديو)
            if uploaded_image is not None:
                project_image = Image.open(uploaded_image)
            elif uploaded_video is not None:
                project_image = extract_frame_from_video(uploaded_video)

            # توليد البوستر النهائي
            final_poster = create_poster(project_title, project_subtitle, report_text, project_image, theme_choice)
            
            st.success("✅ تم توليد بوستر المشروع بنجاح!")
            
            # عرض المعاينة
            st.image(final_poster, caption="معاينة البوستر النهائي", use_container_width=True)
            
            # تجهيز الزر لتنزيل الصورة
            buf = io.BytesIO()
            final_poster.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 تحميل البوستر بجودة عالية (PNG)",
                data=byte_im,
                file_name=f"{project_title}_poster.png",
                mime="image/png"
            )
          
