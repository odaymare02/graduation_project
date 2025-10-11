import requests
from bs4 import BeautifulSoup
import json
def info_according_semester():

# قائمة التخصصات مع قيم payload المختلفة
    majors = {
    "CS": "10671",
    "CSec": "10687",
    "MIS": "10676",
    "CAP": "10672",
    "CAP_SW":"10673",
    "CAP_AI":"10674"
}

    base_url = "https://zajelbs.najah.edu/servlet/materials"
    headers = {"User-Agent": "Mozilla/5.0"}

    all_majors_courses = {}

    for major_name, major_val in majors.items():
        payload = {"b": "maj", "var": major_val, "flag": "done"}
        response = requests.post(base_url, data=payload, headers=headers)
        response.encoding = "windows-1256"
        soup = BeautifulSoup(response.text, "html.parser")

        # نأخذ الجدول الثالث مباشرة
        tables = soup.find_all("table")

        target_table = tables[2]  # الجدول الثالث
        courses = {}
        rows = target_table.find_all("tr")[1:]  # تخطي عنوان الجدول

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 12:
                continue

            course_name = " ".join(cols[3].get_text(strip=True).split())

            section_code = cols[2].get_text(strip=True)
            section_num = section_code.split("/")[0] if "/" in section_code else "1"

            room_tag = cols[7].find("a")
            room = room_tag.get_text(strip=True) if room_tag else ""

            schedule = []
            tooltip_div = cols[5].find("div", class_="demo")
            if tooltip_div:
                span_tag = tooltip_div.find("span")
                if span_tag and span_tag.has_attr("data-tooltip"):
                    tooltip_text = span_tag["data-tooltip"]
                    schedule = [line.strip() for line in tooltip_text.split("\n") if line.strip()]
            teacher_tag = cols[10]  
            teacher_name = teacher_tag.get_text(strip=True) if teacher_tag else ""
            if course_name not in courses:
                courses[course_name] = {"الشعب": []}

            courses[course_name]["الشعب"].append({
                "رقم الشعبة": section_num,
                "رقم القاعة": room,
                "الدوام": schedule,
                "المدرس": teacher_name
            })

        all_majors_courses[major_name] = courses
        print(f"✅ تم استخراج {len(courses)} مادة للتخصص {major_name}")
        with open(r"C:\Users\user\Desktop\grad_project\data\info_according_semester.json", "w", encoding="utf-8") as f:
            json.dump(all_majors_courses, f, ensure_ascii=False, indent=4)
def plan_majors():
    majors = {
    "CS": "80671",
    "CSec": "10687",
    "MIS":"10676",
    "CAP":"10672",
    "CAP_SW":"10673",
    "CAP_AI":"10674",
    }

    # أنواع المواد و dispOpt لكل نوع
    material_types = {
        "إجباري تخصص": "31",
        "اختياري تخصص": "32",
        "اختياري تخصص مجموعة ثانية":"36"
    }

    base_url = "https://zajelbs.najah.edu/servlet/UniCurricula"
    headers = {"User-Agent": "Mozilla/5.0"}

    data = {}

    for major_name, majVal in majors.items():
        data[major_name] = {}
        for material_name, dispOpt in material_types.items():
            payload = {
                "majVal": majVal,
                "curVal": "2025-1",  # الخطة المطلوبة
                "dispOpt": dispOpt
            }
            response = requests.post(base_url, headers=headers, data=payload)
            response.encoding = "windows-1256"
            soup = BeautifulSoup(response.text, "html.parser")

            # استخراج عدد الساعات المطلوبة
            hours_tag = soup.find("td", colspan="10")
            if hours_tag:
                text = hours_tag.get_text()
                try:
                    hours = int(''.join(filter(str.isdigit, text.split("=")[-1])))
                except:
                    hours = 0
            else:
                hours = 0

            # استخراج المساقات
            courses = []
            table = soup.find("table", {"border": "1"})
            if table:
                rows = table.find_all("tr")[2:]  # نتجاوز الهيدر
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 6:
                        course_number = cols[1].get_text(strip=True)
                        course_name = cols[3].get_text(strip=True)
                        course_hours = cols[2].get_text(strip=True)

                        # استخراج أسماء المتطلبات السابقة من data-tooltip
                        prereqs_list = []
                        prereq_spans = cols[5].find_all("span", {"data-tooltip": True})
                        for span in prereq_spans:
                            name = span.get("data-tooltip").strip()
                            if name:
                                prereqs_list.append(name)

                        courses.append({
                            "رقم المساق": course_number,
                            "اسم المساق": course_name,
                            "عدد الساعات": int(course_hours) if course_hours.isdigit() else 0,
                            "المتطلبات السابقة": prereqs_list
                        })

            data[major_name][material_name] = {
                "عدد الساعات المطلوبة": hours,
                "المساقات": courses
            }

    # حفظ الداتا في JSON واحد
    with open(r"C:\Users\user\Desktop\grad_project\data\majors_plan_dynamic_info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("تم حفظ الخطط لكل التخصصات في majors_plan_dynamic_info.json")
def require_NNU_material():
    numberCourses = {
        "انجليزي استدراكي":10032100,
        "ثقافة إسلامية":11000101,
        "لغة عربية":11000102,
        "اللغة الانجليزية 1":11000103,
        "دراسات فلسطينية":11000105,
        "خدمة المجتمع و التنمية المستدامة":11000109,
        "مهارات قيادة واتصال":11000117,
        "مقدمة في الذكاء الاصطناعي وعلم البيانات":11000129,
        "لغة انجليزيّة (2)":11000322
    }

    url = "https://zajelbs.najah.edu/servlet/materials"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    all_courses = {}

    for course_name, course_id in numberCourses.items():
        payload = {"b": "num", "var": str(course_id)}
        res = requests.post(url, headers=headers, data=payload)
        res.encoding = "windows-1256"
        soup = BeautifulSoup(res.text, "html.parser")

        sections = []
        rows = soup.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 10:
                # رقم القسم (أول خانة فيها رقم/مساق)
                section_number = cols[2].get_text(strip=True).split("/")[0]

                # القاعة
                room = cols[7].get_text(strip=True)

                # الحرم
                campus = cols[8].get_text(strip=True)

                # الأيام + الساعات + القاعة + الحرم
                days_times = []
                tooltip = cols[5].find("span")
                if tooltip and tooltip.has_attr("data-tooltip"):
                    for line in tooltip["data-tooltip"].split("\n"):
                        if line.strip():
                            days_times.append(line.strip())

                # المدرس
                instructor = cols[10].get_text(strip=True)

                sections.append({
                    "المادة": course_name,  
                    "رقم الشعبة": section_number,
                    "رقم القاعة": room,
                    "الدوام": days_times,
                    "المدرس": instructor,
                    "الحرم": campus
                })

        all_courses[course_name] = {"الشعب": sections}

    # حفظ في JSON
    with open(r"C:\Users\user\Desktop\grad_project\data\mandatory_courses.json", "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=4)
    print("تم حفظ البيانات في mandatory_courses.json")
def get_important_dates(semester="2025-1"):
    url = "https://zajelbs.najah.edu/servlet/calendar"
    payload = {"acaSem": semester}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # إرسال الطلب
    response = requests.post(url, data=payload, headers=headers)
    response.encoding = "windows-1256"

    soup = BeautifulSoup(response.text, "html.parser")

    # العثور على القسم الذي يحتوي على "مواعيد هامة"
    section = soup.find("font", {"color": "red"})
    if not section:
        print("❌ لم يتم العثور على قسم المواعيد الهامة.")
        return None

    parent_td = section.find_parent("td")

    parts = []
    for elem in parent_td.contents:
        if elem.name == "br":
            continue
        if elem.name == "b":
            text = elem.get_text(strip=True)
            if parts:
                parts[-1] += " " + text
            else:
                parts.append(text)
        elif elem.name is None:
            text = elem.strip()
            if text and not text.startswith("مواعيد"):
                parts.append(text)

    result = {
        "مواعيد هامة": parts
    }

    with open(r"C:\Users\user\Desktop\grad_project\data\important_dates.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("تم حفظ البيانات في important_dates.json")
# info_according_semester()
# plan_majors()
# require_NNU_material()
get_important_dates();