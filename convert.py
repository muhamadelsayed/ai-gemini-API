import json
import os

# اسم الملف الذي حملته من جوجل درايف
INPUT_FILE = "Copy of Laravel Trucking App APIs Development.json" 
# اسم المحادثة التي تريدها أن تظهر في برنامجك
OUTPUT_NAME = "Laravel Trucking App APIs Development"

def convert_google_studio_json(input_path, output_name):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        new_messages = []
        
        # استخراج المحادثات من هيكل Google Studio
        chunks = data.get('chunkedPrompt', {}).get('chunks', [])
        
        for chunk in chunks:
            role = chunk.get('role')
            text = chunk.get('text')
            
            if role and text:
                # تحويل الأدوار لتناسب نظامنا
                # في جوجل 'model' وفي نظامنا 'assistant'
                clean_role = "assistant" if role == "model" else "user"
                new_messages.append({
                    "role": clean_role,
                    "content": text
                })
        
        # التأكد من وجود مجلد المحادثات
        if not os.path.exists("my_chats"):
            os.makedirs("my_chats")
            
        # حفظ الملف الجديد
        output_path = f"my_chats/{output_name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(new_messages, f, ensure_ascii=False, indent=4)
            
        print(f"✅ تمت العملية! تم إنشاء محادثة باسم: {output_name}")
        print(f"عدد الرسائل المستخرجة: {len(new_messages)}")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء التحويل: {e}")

# تشغيل التحويل
convert_google_studio_json(INPUT_FILE, OUTPUT_NAME)