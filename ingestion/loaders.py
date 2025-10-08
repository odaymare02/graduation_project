import json
from pathlib import Path
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

BASE_DIR = Path(__file__).resolve().parent.parent




def prepare_passage(text):
    return f"passage: {text.strip()}"

def clean_text(text):
    return re.sub(r'(?<![\n.،:؛])\n(?![\n])', ' ', text).strip()

# -------------------- تحميل المستندات --------------------
def load_guide():
    pdf_path = BASE_DIR / "data" / "guide.pdf"
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    for i, page in enumerate(pages):
        page.page_content = clean_text(page.page_content)
        page.metadata["major"] = "General"
        page.metadata["name"] = f"General - الصفحة {i+1}"
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " "]
    )
    return splitter.split_documents(pages)

def load_resources():
    resource_path = BASE_DIR / "data" / "cResourse.json"
    with open(resource_path, "r", encoding="utf-8") as f:
        course_resource = json.load(f)

    def format_resource_item(item):
        return f"المادة: {item.get('المادة', '')}\nالنوع: {item.get('النوع', '')}\nالعنوان: {item.get('العنوان', '')}\nالرابط: {item.get('الرابط', '')}".strip()

    docs = []
    for major, resources in course_resource.items():
        for item in resources:
            content = prepare_passage(format_resource_item(item))
            docs.append(Document(
                page_content=content,
                metadata={
                    "major": major,
                    "subject": item.get("المادة", ""),
                    "type": item.get("النوع", ""),
                    "title": item.get("العنوان", ""),
                    "url": item.get("الرابط", ""),
                    "name":"مصادر للدراسة"
                }
            ))
    return docs

def load_courses():
    plan_path = BASE_DIR / "data" / "majors_plan_static_info.json"
    with open(plan_path, "r", encoding="utf-8") as f:
        course_data = json.load(f)

    def format_course(course):
        return f"""
اسم المادة: {course.get("اسم المادة", "")}
السنة: {course.get("السنة", "")}
الفصل: {course.get("الفصل", "")}
وصف المساق: {course.get("وصف المساق", "")}
""".strip()

    docs = []
    for major, courses in course_data.items():
        for course in courses:
            docs.append(Document(
                page_content=prepare_passage(format_course(course)),
                metadata={
                    "major": major,
                    "subject": course.get("اسم المادة", ""),
                    "year": course.get("السنة", ""),
                    "semester": course.get("الفصل", ""),
                    "description": course.get("وصف المساق", ""),
                    "name":"الخطط الدراسية-ثابتة"
                }
            ))
    return docs

def load_profs():
    prof_path = BASE_DIR / "data" / "prof.json"
    with open(prof_path, "r", encoding="utf-8") as f:
        prof_data = json.load(f)

    def format_prof(prof):
        return f"""
الاسم: {prof.get("الاسم", "")}
المواد التي يدرسها: {', '.join(prof.get("المواد التي يدرسها", []))}
البريد الإلكتروني: {prof.get("البريد الإلكتروني", "")}
الوصف: {prof.get("الوصف", "")}
""".strip()

    docs = []
    for major, profs in prof_data.items():
        for prof in profs:
            docs.append(Document(
                page_content=prepare_passage(format_prof(prof)),
                metadata={
                    "major": major,
                    "name": prof.get("الاسم", ""),
                    "email": prof.get("البريد الإلكتروني", ""),
                    "subjects": prof.get("المواد التي يدرسها", []),
                    "description": prof.get("الوصف", "")
                }
            ))
    return docs

def load_projects():
    info_path = BASE_DIR / "data" / "info.json"
    with open(info_path, "r", encoding="utf-8") as f:
        info_data = json.load(f)

    docs = []
    for project in info_data:
        docs.append(Document(
            page_content=prepare_passage(f"مؤسسو المشروع: {', '.join(project.get('مؤسسين المشروع', []))}\nالمشرف: {project.get('المشرف', '')}"),
            metadata={
                "founders": project.get("مؤسسين المشروع", []),
                "supervisor": project.get("المشرف", ""),
                "major":"General",
                "name":"معلومات المشروع"
            }
        ))
    return docs

def load_schedule():
    schedule_path = BASE_DIR / "data" / "info_according_semester.json"
    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    docs = []
    for major, courses in schedule_data.items():  # كل تخصص
        for course_name, course_info in courses.items():  # كل مادة
            for section in course_info.get("الشعب", []):
                page_content = prepare_passage(
                    f"المادة: {course_name}\n"
                    f"الشعبة: {section.get('رقم الشعبة', '')}\n"
                    f"القاعة: {section.get('رقم القاعة', '')}\n"
                    f"الدوام: {'; '.join(section.get('الدوام', []))}\n"
                    f"المدرس: {section.get('المدرس', '')}"
                )
                docs.append(Document(
                    page_content=page_content,
                    metadata={
                        "major": major,
                        "subject": course_name,
                        "section": section.get("رقم الشعبة", ""),
                        "room": section.get("رقم القاعة", ""),
                        "schedule": "; ".join(section.get("الدوام", [])),
                        "teacher": section.get("المدرس", ""),
                        "name":"الجدول حسب الفصل الحالي"

                    }
                ))
    return docs


def load_mandatory_courses():
    schedule_path = BASE_DIR / "data" / "mandatory_courses.json"
    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    docs = []
    for course_name, course_info in schedule_data.items():  # المادة مباشرة
        for section in course_info.get("الشعب", []):
            page_content = prepare_passage(
                f"المادة: {course_name}\n"
                f"الشعبة: {section.get('رقم الشعبة', '')}\n"
                f"القاعة: {section.get('رقم القاعة', '')}\n"
                f"الدوام: {'; '.join(section.get('الدوام', []))}\n"
                f"المدرس: {section.get('المدرس', '')}\n"
                f"الحرم: {section.get('الحرم', '')}"
            )
            docs.append(Document(
                page_content=page_content,
                metadata={
                    "major":"General",
                    "subject": course_name,
                    "section": section.get("رقم الشعبة", ""),
                    "room": section.get("رقم القاعة", ""),
                    "schedule": "; ".join(section.get("الدوام", [])),
                    "teacher": section.get("المدرس", ""),
                    "campus": section.get("الحرم", ""),
                    "name":"اجباري الجامعة"
                }
            ))
    return docs

def load_course_info():
    course_info_path = BASE_DIR / "data" / "majors_plan_dynamic_info.json"
    with open(course_info_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for major, major_data in data.items():
        for category, info in major_data.items():  # category: "إجباري جامعة" أو "اختياري"
            required_hours = info.get("عدد الساعات المطلوبة", 0)  # ⬅️ تخزين عدد الساعات المطلوبة
            for course in info.get("المساقات", []):
                page_content = prepare_passage(
                    f"المادة: {course.get('اسم المساق', '')}\n"
                    f"رقم المساق: {course.get('رقم المساق', '')}\n"
                    f"عدد الساعات: {course.get('عدد الساعات', '')}\n"
                    f"المتطلبات السابقة: {', '.join(course.get('المتطلبات السابقة', []))}\n"
                    f"عدد الساعات المطلوبة للفئة: {required_hours}"  
                )
                docs.append(Document(
                    page_content=page_content,
                    metadata={
                        "major": major,
                        "category": category,
                        "subject": course.get('اسم المساق', ''),
                        "course_number": course.get('رقم المساق', ''),
                        "hours": course.get('عدد الساعات', 0),
                        "prerequisites": ", ".join(course.get('المتطلبات السابقة', [])),
                        "required_hours": required_hours, 
                        "name": "الخطط الدراسية-متغيرة"
                    }
                ))
    return docs
def load_tips():
    tip_path = BASE_DIR / "data" / "tips.json"
    with open(tip_path, "r", encoding="utf-8") as f:
        tips_data = json.load(f)

    docs = []
    for major, courses in tips_data.items():
        for course in courses:
            docs.append(Document(
                page_content=prepare_passage(f"اسم المادة: {course.get('اسم المادة', '')}\nنصائح: {'; '.join(course.get('نصائح', []))}"),
                metadata={
                    "major": major,
                    "subject": course.get("اسم المادة", ""),
                    "name":"نصائح للمواد"
                }
            ))
    return docs
def sanitize_metadata(doc: Document) -> Document:
    """
    تحويل أي قيمة في metadata تكون قائمة إلى نص مفصول بفاصلة.
    """
    new_meta = {}
    for k, v in doc.metadata.items():
        if isinstance(v, list):
            new_meta[k] = ", ".join(v)
        else:
            new_meta[k] = v
    doc.metadata = new_meta
    return doc
# -------------------- جمع كل المستندات --------------------
all_docs = (
    load_guide() +
    load_resources() +
    load_courses() +
    load_projects() +
    load_profs() +
    load_tips()+
    load_schedule()+
    load_mandatory_courses()+
    load_course_info()
)
all_docs = [sanitize_metadata(doc) for doc in all_docs]
