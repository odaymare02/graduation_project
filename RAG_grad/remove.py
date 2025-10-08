import json

# تحميل الملف
with open(r"C:\Users\user\Desktop\grad_project\RAG_grad\data\plans_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# الحقول اللي بدنا نحذفها
fields_to_remove = ["id", "نوع", "المتطلبات السابقة","عدد الساعات"]

# المرور على جميع المواد وحذف الحقول
for major, courses in data.items():
    for course in courses:
        for field in fields_to_remove:
            course.pop(field, None)  # يحذف الحقل إذا موجود

# حفظ الملف الجديد
with open("plans_cleaned_remove.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("✅ تم حذف الحقول id, نوع, المتطلبات السابقة وحفظ الملف في courses_manual_clean.json")
