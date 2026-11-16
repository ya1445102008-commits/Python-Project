import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import csv
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from PIL import Image, ImageTk

# ============================================
# نظام إدارة البطولة – النسخة المحسنة
# ============================================

# إعدادات المظهر العام
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ------------------------------
# المتغيرات العامة
# ------------------------------
participants = []          # قائمة المشاركين (كل مشارك لديه id)
next_participant_id = 1    # لتوليد معرفات جديدة
current_lang = "ar"        # اللغة الحالية
data_file = "tournament_data.json"  # ملف حفظ البيانات

# أسماء الفرق الأربعة المحددة مسبقاً (مع ترجمة)
TEAM_NAMES = {
    "ar": ["فريق 1", "فريق 2", "فريق 3", "فريق 4"],
    "en": ["Team 1", "Team 2", "Team 3", "Team 4"]
}

# ------------------------------
# دوال مساعدة للترجمة
# ------------------------------
def tr(ar_text, en_text):
    """إرجاع النص حسب اللغة الحالية"""
    return ar_text if current_lang == "ar" else en_text

# ------------------------------
# بناء الأحداث (مع معرفات)
# ------------------------------
def build_events():
    """إنشاء قوائم الأحداث مع معرفات فريدة"""
    # أحداث فردية رياضية
    ind_sports_ar = [
        "100م جري", "200م جري", "400م جري", "قفز طويل", "قفز عالي",
        "رمي الجلة", "رمي الرمح", "سباحة 50م", "دراجات", "رماية"
    ]
    ind_sports_en = [
        "100m Sprint", "200m Sprint", "400m Run", "Long Jump", "High Jump",
        "Shot Put", "Javelin Throw", "50m Swimming", "Cycling", "Archery"
    ]
    # أحداث فردية أكاديمية
    ind_acad_ar = [
        "مسابقة رياضيات", "مسابقة فيزياء", "مسابقة كيمياء", "مسابقة أحياء",
        "شطرنج", "برمجة", "ثقافة عامة", "تهجئة", "مناظرة", "تعبير كتابي"
    ]
    ind_acad_en = [
        "Math Quiz", "Physics Quiz", "Chemistry Quiz", "Biology Quiz",
        "Chess", "Programming", "General Knowledge", "Spelling Bee",
        "Debate", "Essay Writing"
    ]
    # أحداث جماعية رياضية
    team_sports_ar = [
        "تتابع 4x100م", "كرة قدم", "كرة سلة", "كرة طائرة",
        "كرة يد", "شد حبل", "كرة ماء", "كريكيت", "هوكي", "رجبي"
    ]
    team_sports_en = [
        "4x100m Relay", "Soccer", "Basketball", "Volleyball",
        "Handball", "Tug of War", "Water Polo", "Cricket", "Hockey", "Rugby"
    ]
    # أحداث جماعية أكاديمية
    team_acad_ar = [
        "مشروع جماعي", "مناظرة جماعية", "معرض علوم",
        "مسابقة معلومات جماعية", "روبوت", "محاكاة الأمم المتحدة",
        "دراسة حالة", "تصميم هندسي", "رياضيات جماعية", "أسئلة عامة"
    ]
    team_acad_en = [
        "Team Project", "Group Debate", "Science Fair",
        "Quiz Bowl", "Robotics", "Model UN",
        "Case Study", "Engineering Design", "Team Math", "Trivia"
    ]

    events = []
    event_id = 1
    # فردي رياضي
    for ar, en in zip(ind_sports_ar, ind_sports_en):
        events.append({
            "id": event_id,
            "name_ar": ar,
            "name_en": en,
            "category_ar": "رياضي",
            "category_en": "Sports",
            "is_team": False,
            "results": {}  # مفتاح: معرف المشارك، قيمة: الترتيب
        })
        event_id += 1
    # فردي أكاديمي
    for ar, en in zip(ind_acad_ar, ind_acad_en):
        events.append({
            "id": event_id,
            "name_ar": ar,
            "name_en": en,
            "category_ar": "أكاديمي",
            "category_en": "Academic",
            "is_team": False,
            "results": {}
        })
        event_id += 1
    # جماعي رياضي
    for ar, en in zip(team_sports_ar, team_sports_en):
        events.append({
            "id": event_id,
            "name_ar": ar,
            "name_en": en,
            "category_ar": "رياضي",
            "category_en": "Sports",
            "is_team": True,
            "results": {}
        })
        event_id += 1
    # جماعي أكاديمي
    for ar, en in zip(team_acad_ar, team_acad_en):
        events.append({
            "id": event_id,
            "name_ar": ar,
            "name_en": en,
            "category_ar": "أكاديمي",
            "category_en": "Academic",
            "is_team": True,
            "results": {}
        })
        event_id += 1
    return events

all_events = build_events()
print(f"عدد الأحداث الإجمالي: {len(all_events)}")  # للتأكد من العدد

# ------------------------------
# دوال حفظ وتحميل البيانات
# ------------------------------
def save_data():
    """حفظ جميع البيانات إلى ملف JSON"""
    data = {
        "participants": participants,
        "next_id": next_participant_id,
        "events": [
            {
                "id": e["id"],
                "name_ar": e["name_ar"],
                "name_en": e["name_en"],
                "category_ar": e["category_ar"],
                "category_en": e["category_en"],
                "is_team": e["is_team"],
                "results": e["results"]
            }
            for e in all_events
        ]
    }
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror(tr("خطأ", "Error"), tr(f"فشل الحفظ: {e}", f"Save failed: {e}"))

def load_data():
    """تحميل البيانات من ملف JSON"""
    global participants, next_participant_id, all_events
    if not os.path.exists(data_file):
        return
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # التحقق من أن participants هي قائمة، وإلا نبدأ بقائمة فارغة
        loaded_parts = data.get("participants", [])
        if isinstance(loaded_parts, list):
            participants = loaded_parts
        else:
            participants = []  # إذا كانت البيانات مخزنة بشكل خاطئ (مثل قاموس) نستخدم قائمة فارغة

        next_participant_id = data.get("next_id", 1)
        loaded_events = data.get("events", [])

        # دمج الأحداث المحملة مع الأحداث الافتراضية
        for loaded_event in loaded_events:
            found = False
            for e in all_events:
                if e["id"] == loaded_event["id"]:
                    e.update(loaded_event)
                    found = True
                    break
            if not found:
                all_events.append(loaded_event)
    except Exception as e:
        messagebox.showerror(tr("خطأ", "Error"), tr(f"فشل التحميل: {e}", f"Load failed: {e}"))

# ------------------------------
# دوال تحديث الواجهة حسب اللغة
# ------------------------------
def toggle_language():
    global current_lang
    if current_lang == "ar":
        current_lang = "en"
        ctk.set_appearance_mode("light")
    else:
        current_lang = "ar"
        ctk.set_appearance_mode("dark")
    update_ui_language()
    update_event_list()  # تحديث قائمة الأحداث بعد تغيير اللغة
    update_table()
    update_dashboard_text()

def update_ui_language():
    window.title(tr("نظام إدارة البطولة", "Tournament Management System"))
    lbl_type.configure(text=tr("نوع المشارك", "Participant Type"))
    radio_ind.configure(text=tr("فردي", "Individual"))
    radio_team.configure(text=tr("فريق", "Team"))
    lbl_name.configure(text=tr("الاسم:", "Name:"))
    lbl_team_select.configure(text=tr("اختر الفريق:", "Select Team:"))
    btn_add.configure(text=tr("إضافة مشارك", "Add Participant"))
    lbl_category.configure(text=tr("فئة الفعالية", "Event Category"))
    btn_sports.configure(text=tr("رياضي", "Sports"))
    btn_academic.configure(text=tr("أكاديمي", "Academic"))
    lbl_event.configure(text=tr("الفعالية:", "Event:"))
    lbl_participants.configure(text=tr("المشاركون", "Participants"))
    tree.heading("Name", text=tr("الاسم", "Name"))
    tree.heading("Type", text=tr("النوع", "Type"))
    tree.heading("Team", text=tr("الفريق", "Team"))
    tree.heading("Points", text=tr("النقاط", "Points"))
    tree.heading("Events", text=tr("الأحداث", "Events"))
    lbl_score_name.configure(text=tr("اسم المشارك:", "Participant Name:"))
    lbl_rank.configure(text=tr("الترتيب:", "Rank:"))
    btn_add_score.configure(text=tr("إضافة نتيجة", "Add Result"))
    lbl_results.configure(text=tr("النتائج النهائية", "Final Results"))
    btn_results.configure(text=tr("عرض النتائج", "Show Results"))
    btn_export_csv.configure(text=tr("تصدير CSV", "Export CSV"))
    btn_export_pdf.configure(text=tr("تصدير PDF", "Export PDF"))
    btn_search.configure(text=tr("بحث", "Search"))
    btn_edit.configure(text=tr("تعديل", "Edit"))
    btn_delete.configure(text=tr("حذف", "Delete"))
    btn_details.configure(text=tr("تفاصيل", "Details"))
    lbl_dashboard.configure(text=tr("لوحة المعلومات", "Dashboard"))
    btn_chart.configure(text=tr("عرض الرسم البياني", "Show Chart"))
    btn_manage_events.configure(text=tr("إدارة الأحداث", "Manage Events"))
    btn_help.configure(text=tr("مساعدة", "Help"))
    # تحديث قيم الفرق في القائمة المنسدلة
    team_combo.configure(values=TEAM_NAMES[current_lang])
    team_combo.set(TEAM_NAMES[current_lang][0])
    # تحديث شريط التقدم
    update_progress_bars()

def update_dashboard_text():
    total_participants = len(participants)
    total_individuals = sum(1 for p in participants if p["type"] == "Individual")
    total_teams = len(set(p["team"] for p in participants if p["type"] == "Team" and p["team"]))
    completed_events = sum(1 for e in all_events if e["results"])
    total_points = sum(p["points"] for p in participants)
    top_participant = max(participants, key=lambda x: x["points"]) if participants else None
    top_team_points = {}
    for p in participants:
        if p["type"] == "Team" and p["team"]:
            top_team_points[p["team"]] = top_team_points.get(p["team"], 0) + p["points"]
    best_team = max(top_team_points, key=top_team_points.get) if top_team_points else None
    best_team_points = top_team_points.get(best_team, 0) if best_team else 0

    if current_lang == "ar":
        text = f"إجمالي: {total_participants} | فرق: {total_teams} | أفراد: {total_individuals} | فعاليات مكتملة: {completed_events} من {len(all_events)}"
        text += f"\nإجمالي النقاط: {total_points} | أعلى مشارك: {top_participant['name'] if top_participant else '-'} ({top_participant['points'] if top_participant else 0})"
        text += f" | أفضل فريق: {best_team if best_team else '-'} ({best_team_points})"
    else:
        text = f"Total: {total_participants} | Teams: {total_teams} | Individuals: {total_individuals} | Completed: {completed_events} of {len(all_events)}"
        text += f"\nTotal Points: {total_points} | Top Participant: {top_participant['name'] if top_participant else '-'} ({top_participant['points'] if top_participant else 0})"
        text += f" | Best Team: {best_team if best_team else '-'} ({best_team_points})"
    lbl_dashboard_value.configure(text=text)

# دالة لعرض تفاصيل لوحة المعلومات في نافذة منبثقة
def show_dashboard_details():
    total_participants = len(participants)
    total_individuals = sum(1 for p in participants if p["type"] == "Individual")
    total_teams = len(set(p["team"] for p in participants if p["type"] == "Team" and p["team"]))
    completed_events = sum(1 for e in all_events if e["results"])
    total_points = sum(p["points"] for p in participants)
    top_participant = max(participants, key=lambda x: x["points"]) if participants else None
    top_team_points = {}
    for p in participants:
        if p["type"] == "Team" and p["team"]:
            top_team_points[p["team"]] = top_team_points.get(p["team"], 0) + p["points"]
    best_team = max(top_team_points, key=top_team_points.get) if top_team_points else None
    best_team_points = top_team_points.get(best_team, 0) if best_team else 0

    if current_lang == "ar":
        details = f"إجمالي المشاركين: {total_participants}\n"
        details += f"عدد الفرق: {total_teams}\n"
        details += f"عدد الأفراد: {total_individuals}\n"
        details += f"الفعاليات المكتملة: {completed_events} من {len(all_events)}\n"
        details += f"إجمالي النقاط: {total_points}\n"
        details += f"أعلى مشارك: {top_participant['name'] if top_participant else '-'} ({top_participant['points'] if top_participant else 0})\n"
        details += f"أفضل فريق: {best_team if best_team else '-'} ({best_team_points})"
    else:
        details = f"Total Participants: {total_participants}\n"
        details += f"Teams: {total_teams}\n"
        details += f"Individuals: {total_individuals}\n"
        details += f"Completed Events: {completed_events} of {len(all_events)}\n"
        details += f"Total Points: {total_points}\n"
        details += f"Top Participant: {top_participant['name'] if top_participant else '-'} ({top_participant['points'] if top_participant else 0})\n"
        details += f"Best Team: {best_team if best_team else '-'} ({best_team_points})"

    messagebox.showinfo(tr("تفاصيل لوحة المعلومات", "Dashboard Details"), details)

# ------------------------------
# دوال إدارة المشاركين
# ------------------------------
def add_participant():
    global next_participant_id
    try:
        print("=== بدء إضافة مشارك ===")
        name = entry_name.get().strip()
        ptype = participant_type.get().strip()
        print(f"الاسم: '{name}' - النوع: '{ptype}'")

        # تحويل القيم العربية إلى إنجليزية إذا لزم الأمر (للتوافق)
        if ptype == "فردي":
            ptype = "Individual"
        elif ptype == "فريق":
            ptype = "Team"

        team = team_combo.get() if ptype == "Team" else ""
        print(f"الفريق: '{team}'")

        if not name:
            messagebox.showerror(tr("خطأ", "Error"), tr("الاسم مطلوب", "Name is required"))
            return

        if ptype == "Individual":
            # التحقق من عدد الأفراد
            if sum(1 for p in participants if p["type"] == "Individual") >= 20:
                msg = tr("لا يمكن إضافة أكثر من 20 فرد", "Cannot add more than 20 individuals")
                messagebox.showerror(tr("خطأ", "Error"), msg)
                return
            # التحقق من تكرار الاسم
            if any(p["name"] == name for p in participants):
                msg = tr("الاسم موجود مسبقاً", "Name already exists")
                messagebox.showerror(tr("خطأ", "Error"), msg)
                return
            participants.append({
                "id": next_participant_id,
                "name": name,
                "type": "Individual",
                "team": "",
                "points": 0,
                "events": []
            })
            next_participant_id += 1
            print("تمت إضافة فرد جديد")
        else:  # Team
            if not team:
                messagebox.showerror(tr("خطأ", "Error"), tr("الرجاء اختيار الفريق", "Please select a team"))
                return

            # تحويل اسم الفريق إلى النسخة العربية (للتخزين الموحد)
            team_ar = None
            if current_lang == "ar":
                team_ar = team
            else:
                # البحث المرن عن اسم الفريق بالإنجليزية
                team_lower = team.lower().strip()
                found = False
                for idx, en_name in enumerate(TEAM_NAMES["en"]):
                    if en_name.lower() == team_lower:
                        team_ar = TEAM_NAMES["ar"][idx]
                        found = True
                        break
                if not found:
                    messagebox.showerror(tr("خطأ", "Error"), tr("الفريق غير صحيح", "Invalid team"))
                    return

            # التحقق من أن الفريق ضمن القائمة (للسلامة)
            if team_ar not in TEAM_NAMES["ar"]:
                messagebox.showerror(tr("خطأ", "Error"), tr("الفريق غير صحيح", "Invalid team"))
                return

            # التحقق من عدد أعضاء الفريق
            team_members = [p for p in participants if p["type"] == "Team" and p["team"] == team_ar]
            if len(team_members) >= 5:
                msg = tr(f"الفريق {team_ar} اكتمل (5 أعضاء)", f"Team {team_ar} is full (5 members)")
                messagebox.showerror(tr("خطأ", "Error"), msg)
                return

            # التحقق من تكرار الاسم
            if any(p["name"] == name for p in participants):
                msg = tr("الاسم موجود مسبقاً", "Name already exists")
                messagebox.showerror(tr("خطأ", "Error"), msg)
                return

            participants.append({
                "id": next_participant_id,
                "name": name,
                "type": "Team",
                "team": team_ar,
                "points": 0,
                "events": []
            })
            next_participant_id += 1
            print("تمت إضافة عضو فريق جديد")

        # تحديث الواجهة
        print("تحديث الجدول...")
        update_table()
        entry_name.delete(0, tk.END)
        print("تحديث لوحة المعلومات...")
        update_dashboard_text()
        print("تحديث أشرطة التقدم...")
        update_progress_bars()
        print("حفظ البيانات...")
        save_data()
        msg = tr("تمت الإضافة بنجاح", "Added successfully")
        messagebox.showinfo(tr("نجاح", "Success"), msg)
        print("=== انتهت الإضافة بنجاح ===")
    except Exception as e:
        print(f"!!! خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror(tr("خطأ", "Error"), tr(f"حدث خطأ غير متوقع: {e}", f"Unexpected error: {e}"))

def update_table(filter_text=""):
    for row in tree.get_children():
        tree.delete(row)
    filtered = participants
    if filter_text:
        filtered = [p for p in participants if filter_text.lower() in p["name"].lower()]
    for i, p in enumerate(filtered):
        tag = 'even' if i % 2 == 0 else 'odd'
        events_count = len(p["events"])
        # عرض اسم الفريق حسب اللغة
        team_display = p["team"]
        if current_lang == "en" and p["team"] in TEAM_NAMES["ar"]:
            idx = TEAM_NAMES["ar"].index(p["team"])
            team_display = TEAM_NAMES["en"][idx]
        tree.insert("", tk.END, values=(p["name"], p["type"], team_display, p["points"], events_count), tags=(tag,), iid=p["id"])

def search_participant():
    text = search_entry.get().strip()
    update_table(text)

def edit_participant():
    selected = tree.selection()
    if not selected:
        msg = tr("اختر مشاركاً للتعديل", "Select a participant to edit")
        messagebox.showwarning(tr("تنبيه", "Warning"), msg)
        return
    participant_id = int(selected[0])
    participant = next((p for p in participants if p["id"] == participant_id), None)
    if not participant:
        return

    # نافذة تعديل
    edit_dialog = ctk.CTkToplevel(window)
    edit_dialog.title(tr("تعديل مشارك", "Edit Participant"))
    edit_dialog.geometry("500x500")
    edit_dialog.transient(window)
    edit_dialog.grab_set()

    # إطار للبيانات الأساسية
    main_frame = ctk.CTkFrame(edit_dialog)
    main_frame.pack(fill="x", padx=10, pady=5)

    # الاسم
    ctk.CTkLabel(main_frame, text=tr("الاسم:", "Name:")).pack(pady=5)
    name_entry = ctk.CTkEntry(main_frame, width=300)
    name_entry.insert(0, participant["name"])
    name_entry.pack(pady=5)

    # النوع
    ctk.CTkLabel(main_frame, text=tr("النوع:", "Type:")).pack(pady=5)
    type_var = tk.StringVar(value=participant["type"])
    type_combo = ctk.CTkComboBox(main_frame, values=[tr("فردي", "Individual"), tr("فريق", "Team")], variable=type_var, state="readonly")
    type_combo.pack(pady=5)

    # إطار الفريق (سيتم إخفاؤه/إظهاره حسب النوع)
    team_frame = ctk.CTkFrame(main_frame)
    team_frame.pack(fill="x", pady=5)
    
    ctk.CTkLabel(team_frame, text=tr("الفريق:", "Team:")).pack(pady=5)
    team_combo_edit = ctk.CTkComboBox(team_frame, values=TEAM_NAMES[current_lang], state="readonly")
    if participant["team"]:
        if current_lang == "ar":
            team_combo_edit.set(participant["team"])
        else:
            idx = TEAM_NAMES["ar"].index(participant["team"])
            team_combo_edit.set(TEAM_NAMES["en"][idx])
    else:
        team_combo_edit.set(TEAM_NAMES[current_lang][0])
    team_combo_edit.pack(pady=5)

    # تحديث ظهور إطار الفريق حسب النوع
    def update_team_visibility(*args):
        if type_var.get() == tr("فريق", "Team"):
            team_frame.pack(fill="x", pady=5)
        else:
            team_frame.pack_forget()
    
    type_var.trace_add("write", update_team_visibility)
    update_team_visibility()  # تطبيق الحالة الأولية

    # إطار الأحداث المسجلة (لإمكانية حذفها)
    events_frame = ctk.CTkFrame(edit_dialog)
    events_frame.pack(fill="both", expand=True, padx=10, pady=5)

    ctk.CTkLabel(events_frame, text=tr("الأحداث المسجلة:", "Registered Events:"), font=("Cairo", 12, "bold")).pack(anchor="w", padx=5, pady=2)

    # إنشاء إطار للقائمة مع سكرول
    list_frame = ctk.CTkFrame(events_frame)
    list_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # استخدام Text لعرض الأحداث (لأنه يدعم التحديد)
    events_text = ctk.CTkTextbox(list_frame, height=150)
    events_text.pack(fill="both", expand=True)

    # تعبئة الأحداث المسجلة
    event_list = []
    for event_id in participant["events"]:
        event = next((e for e in all_events if e["id"] == event_id), None)
        if event:
            rank = event["results"].get(participant_id, "?")
            event_name = event["name_ar"] if current_lang == "ar" else event["name_en"]
            line = f"{event_name} - {tr('الترتيب', 'Rank')}: {rank}\n"
            events_text.insert("end", line)
            event_list.append(event_id)  # نحتفظ بترتيب الأحداث

    events_text.configure(state="disabled")  # جعله للقراءة فقط

    # زر حذف الحدث المحدد
    def delete_selected_event():
        # الحصول على النص المحدد
        try:
            selected_text = events_text.selection_get()
        except:
            messagebox.showwarning(tr("تنبيه", "Warning"), tr("اختر حدثاً من القائمة", "Select an event from the list"))
            return
        
        # البحث عن الحدث المطابق (مقارنة بسيطة)
        lines = events_text.get("1.0", "end-1c").split("\n")
        selected_line = selected_text.strip()
        found = False
        for i, line in enumerate(lines):
            if line.strip() == selected_line:
                # حذف هذا الحدث من المشارك
                if i < len(event_list):
                    event_id = event_list[i]
                    event = next((e for e in all_events if e["id"] == event_id), None)
                    if event and participant_id in event["results"]:
                        # حذف النقاط من المشارك
                        rank = event["results"][participant_id]
                        if participant["type"] == "Individual":
                            points_map = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}
                        else:
                            points_map = {1:40, 2:30, 3:20, 4:10}
                        points = points_map.get(rank, 0)
                        participant["points"] -= points
                        # إزالة من قائمة أحداث المشارك
                        participant["events"].remove(event_id)
                        # إزالة من نتائج الحدث
                        del event["results"][participant_id]
                        found = True
                        break
        if found:
            # تحديث العرض
            events_text.configure(state="normal")
            events_text.delete("1.0", "end")
            event_list.clear()
            for event_id in participant["events"]:
                event = next((e for e in all_events if e["id"] == event_id), None)
                if event:
                    rank = event["results"].get(participant_id, "?")
                    event_name = event["name_ar"] if current_lang == "ar" else event["name_en"]
                    line = f"{event_name} - {tr('الترتيب', 'Rank')}: {rank}\n"
                    events_text.insert("end", line)
                    event_list.append(event_id)
            events_text.configure(state="disabled")
            messagebox.showinfo(tr("نجاح", "Success"), tr("تم حذف الحدث", "Event deleted"))
        else:
            messagebox.showerror(tr("خطأ", "Error"), tr("لم يتم العثور على الحدث", "Event not found"))

    ctk.CTkButton(events_frame, text=tr("حذف الحدث المحدد", "Delete Selected Event"), command=delete_selected_event).pack(pady=5)

    # زر الحفظ
    def save_edit():
        new_name = name_entry.get().strip()
        new_type = type_var.get()
        new_team = team_combo_edit.get() if new_type == tr("فريق", "Team") else ""

        if not new_name:
            messagebox.showerror(tr("خطأ", "Error"), tr("الاسم مطلوب", "Name required"))
            return

        # تحقق من عدم تكرار الاسم (باستثناء نفسه)
        if any(p["id"] != participant_id and p["name"] == new_name for p in participants):
            messagebox.showerror(tr("خطأ", "Error"), tr("الاسم موجود مسبقاً", "Name already exists"))
            return

        # تحديث البيانات
        participant["name"] = new_name
        participant["type"] = "Individual" if new_type == tr("فردي", "Individual") else "Team"
        if participant["type"] == "Team":
            if current_lang == "ar":
                participant["team"] = new_team
            else:
                idx = TEAM_NAMES["en"].index(new_team)
                participant["team"] = TEAM_NAMES["ar"][idx]
        else:
            participant["team"] = ""

        # ملاحظة: لا نحذف الأحداث المسجلة عند تغيير النوع (قد تكون غير متوافقة لكننا نتركها للمستخدم)

        update_table()
        update_dashboard_text()
        update_progress_bars()
        save_data()
        edit_dialog.destroy()
        messagebox.showinfo(tr("نجاح", "Success"), tr("تم التعديل بنجاح", "Edited successfully"))

    ctk.CTkButton(main_frame, text=tr("حفظ", "Save"), command=save_edit).pack(pady=10)
def delete_participant():
    selected = tree.selection()
    if not selected:
        msg = tr("اختر مشاركاً للحذف", "Select a participant to delete")
        messagebox.showwarning(tr("تنبيه", "Warning"), msg)
        return
    participant_id = int(selected[0])
    participant = next((p for p in participants if p["id"] == participant_id), None)
    if not participant:
        return

    # التحقق من وجود نتائج مسجلة لهذا المشارك
    has_results = False
    for event in all_events:
        if participant_id in event["results"]:
            has_results = True
            break

    if has_results:
        confirm = tr(f"المشارك {participant['name']} لديه نتائج مسجلة. هل تريد حذفه مع حذف نتائجه؟", 
                     f"Participant {participant['name']} has recorded results. Delete them as well?")
        if not messagebox.askyesno(tr("تأكيد", "Confirm"), confirm):
            return
        # حذف النتائج المرتبطة
        for event in all_events:
            if participant_id in event["results"]:
                del event["results"][participant_id]
    else:
        confirm = tr(f"هل تريد حذف {participant['name']}؟", f"Delete {participant['name']}?")
        if not messagebox.askyesno(tr("تأكيد", "Confirm"), confirm):
            return

    participants.remove(participant)
    update_table()
    update_dashboard_text()
    update_progress_bars()
    save_data()

def show_participant_details():
    selected = tree.selection()
    if not selected:
        msg = tr("اختر مشاركاً لعرض التفاصيل", "Select a participant to view details")
        messagebox.showwarning(tr("تنبيه", "Warning"), msg)
        return
    participant_id = int(selected[0])
    participant = next((p for p in participants if p["id"] == participant_id), None)
    if not participant:
        return

    details_win = ctk.CTkToplevel(window)
    details_win.title(tr("تفاصيل المشارك", "Participant Details"))
    details_win.geometry("600x400")
    details_win.transient(window)
    details_win.grab_set()

    # معلومات أساسية
    info_frame = ctk.CTkFrame(details_win)
    info_frame.pack(fill="x", padx=10, pady=5)
    team_display = participant["team"]
    if current_lang == "en" and participant["team"] in TEAM_NAMES["ar"]:
        idx = TEAM_NAMES["ar"].index(participant["team"])
        team_display = TEAM_NAMES["en"][idx]
    ctk.CTkLabel(info_frame, text=tr(f"الاسم: {participant['name']}", f"Name: {participant['name']}"), font=("Cairo", 14, "bold")).pack(anchor="w")
    ctk.CTkLabel(info_frame, text=tr(f"النوع: {participant['type']}", f"Type: {participant['type']}")).pack(anchor="w")
    if participant["type"] == "Team":
        ctk.CTkLabel(info_frame, text=tr(f"الفريق: {team_display}", f"Team: {team_display}")).pack(anchor="w")
    ctk.CTkLabel(info_frame, text=tr(f"إجمالي النقاط: {participant['points']}", f"Total Points: {participant['points']}")).pack(anchor="w")

    # جدول الأحداث المسجلة
    tree_frame = ctk.CTkFrame(details_win)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
    columns = ("event", "rank", "points")
    event_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    event_tree.pack(fill="both", expand=True)
    event_tree.heading("event", text=tr("الحدث", "Event"))
    event_tree.heading("rank", text=tr("الترتيب", "Rank"))
    event_tree.heading("points", text=tr("النقاط", "Points"))
    event_tree.column("event", width=250)
    event_tree.column("rank", width=100)
    event_tree.column("points", width=100)

    # تعبئة البيانات
    for event_id in participant["events"]:
        event = next((e for e in all_events if e["id"] == event_id), None)
        if event and participant_id in event["results"]:
            rank = event["results"][participant_id]
            # حساب النقاط بناءً على الترتيب
            if participant["type"] == "Individual":
                points_map = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}
                points = points_map.get(rank, 0)
            else:
                points_map = {1:40, 2:30, 3:20, 4:10}
                points = points_map.get(rank, 0)
            event_name = event["name_ar"] if current_lang == "ar" else event["name_en"]
            event_tree.insert("", tk.END, values=(event_name, rank, points))

def toggle_team_selection():
    if participant_type.get() == "Team":
        team_combo.configure(state="readonly")
        lbl_team_select.configure(text_color=("black", "white"))
    else:
        team_combo.configure(state="disabled")
        lbl_team_select.configure(text_color="gray")

# ------------------------------
# دوال الأحداث والنتائج
# ------------------------------
def select_category(cat):
    category_var.set(cat)
    update_event_list()

def update_event_list():
    ptype = participant_type.get()
    cat = category_var.get()  # Arabic category
    events = [e for e in all_events if e["is_team"] == (ptype == "Team") and e["category_ar"] == cat]
    if current_lang == "ar":
        names = [e["name_ar"] for e in events]
    else:
        names = [e["name_en"] for e in events]
    event_combo.configure(values=names)
    if names:
        event_combo.set(names[0])

def add_result():
    name = entry_score_name.get().strip()
    event_display_name = event_combo.get()
    try:
        rank = int(entry_rank.get())
    except:
        msg = tr("الترتيب يجب أن يكون رقماً", "Rank must be a number")
        messagebox.showerror(tr("خطأ", "Error"), msg)
        return

    if not event_display_name:
        msg = tr("اختر حدثاً أولاً", "Select an event first")
        messagebox.showerror(tr("خطأ", "Error"), msg)
        return

    # البحث عن الحدث
    event = None
    if current_lang == "ar":
        event = next((e for e in all_events if e["name_ar"] == event_display_name), None)
    else:
        event = next((e for e in all_events if e["name_en"] == event_display_name), None)

    if not event:
        messagebox.showerror(tr("خطأ", "Error"), tr("الحدث غير موجود", "Event not found"))
        return

    # البحث عن المشارك بالاسم (نفترض أن الأسماء فريدة)
    participant = next((p for p in participants if p["name"] == name), None)
    if not participant:
        msg = tr("المشارك غير موجود", "Participant not found")
        messagebox.showerror(tr("خطأ", "Error"), msg)
        return

    # التحقق من توافق النوع
    if event["is_team"] != (participant["type"] == "Team"):
        msg = tr("نوع المشارك لا يتوافق مع نوع الحدث", "Participant type does not match event type")
        messagebox.showerror(tr("خطأ", "Error"), msg)
        return

    # التحقق من عدم تجاوز 5 أحداث
    if len(participant["events"]) >= 5:
        msg = tr("لا يمكن إضافة أكثر من 5 أحداث لهذا المشارك", "Cannot add more than 5 events for this participant")
        messagebox.showerror(tr("خطأ", "Error"), msg)
        return

    # التحقق من عدم تكرار نفس الحدث
    if event["id"] in participant["events"]:
        msg = tr("تم تسجيل هذا الحدث مسبقاً لهذا المشارك", "This event already registered for this participant")
        messagebox.showerror(tr("خطأ", "Error"), msg)
        return

    # التحقق من عدم تكرار الترتيب في نفس الحدث (لأن كل ترتيب فريد)
    if rank in event["results"].values():
        msg = tr("هذا الترتيب مستخدم بالفعل في هذا الحدث", "This rank is already taken in this event")
        messagebox.showerror(tr("خطأ", "Error"), msg)
        return

    # حساب النقاط
    if participant["type"] == "Individual":
        points_map = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}
        points = points_map.get(rank, 0)
        if points == 0:
            warn = tr("الترتيب خارج نطاق النقاط (يحصل على 0)", "Rank out of points range (gets 0)")
            messagebox.showwarning(tr("تنبيه", "Warning"), warn)
    else:  # Team
        points_map = {1:40, 2:30, 3:20, 4:10}
        points = points_map.get(rank, 0)
        if points == 0:
            warn = tr("الترتيب خارج نطاق النقاط (يحصل على 0)", "Rank out of points range (gets 0)")
            messagebox.showwarning(tr("تنبيه", "Warning"), warn)

    # تسجيل النتيجة
    participant["points"] += points
    participant["events"].append(event["id"])
    event["results"][participant["id"]] = rank

    update_table()
    entry_score_name.delete(0, tk.END)
    entry_rank.delete(0, tk.END)
    update_dashboard_text()
    save_data()
    msg = tr(f"تمت إضافة {points} نقطة للمشارك {name} في حدث {event_display_name}", f"Added {points} points to {name} in {event_display_name}")
    messagebox.showinfo(tr("نجاح", "Success"), msg)

# ------------------------------
# دوال النتائج النهائية والتصدير
# ------------------------------
def show_results():
    if not participants:
        msg = tr("لا يوجد مشاركون", "No participants")
        messagebox.showinfo(tr("معلومات", "Info"), msg)
        return
    sorted_parts = sorted(participants, key=lambda x: x["points"], reverse=True)
    if current_lang == "ar":
        msg = "الترتيب النهائي:\n\n"
        for p in sorted_parts:
            events_count = len(p["events"])
            if p["type"] == "Individual":
                msg += f"{p['name']} (فردي) - {p['points']} نقطة (شارك في {events_count} أحداث)\n"
            else:
                msg += f"{p['name']} (فريق: {p['team']}) - {p['points']} نقطة (شارك في {events_count} أحداث)\n"
    else:
        msg = "Final Standings:\n\n"
        for p in sorted_parts:
            events_count = len(p["events"])
            team_display = p["team"]
            if p["team"] in TEAM_NAMES["ar"]:
                idx = TEAM_NAMES["ar"].index(p["team"])
                team_display = TEAM_NAMES["en"][idx]
            if p["type"] == "Individual":
                msg += f"{p['name']} (Individual) - {p['points']} pts (participated in {events_count} events)\n"
            else:
                msg += f"{p['name']} (Team: {team_display}) - {p['points']} pts (participated in {events_count} events)\n"
    messagebox.showinfo(tr("النتائج النهائية", "Final Results"), msg)

def export_csv():
    filename = "tournament_results.csv"
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if current_lang == "ar":
                writer.writerow(["الاسم", "النوع", "الفريق", "النقاط", "عدد الأحداث"])
            else:
                writer.writerow(["Name", "Type", "Team", "Points", "Events"])
            for p in participants:
                team_display = p["team"]
                if current_lang == "en" and p["team"] in TEAM_NAMES["ar"]:
                    idx = TEAM_NAMES["ar"].index(p["team"])
                    team_display = TEAM_NAMES["en"][idx]
                writer.writerow([p["name"], p["type"], team_display, p["points"], len(p["events"])])
        msg = tr(f"تم التصدير إلى {filename}", f"Exported to {filename}")
        messagebox.showinfo(tr("تصدير", "Export"), msg)
    except Exception as e:
        messagebox.showerror(tr("خطأ", "Error"), tr(f"فشل التصدير: {e}", f"Export failed: {e}"))

def export_pdf():
    filename = "tournament_results.pdf"
    try:
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        if current_lang == "ar":
            c.drawString(200, height - 50, "نتائج البطولة")
        else:
            c.drawString(200, height - 50, "Tournament Results")
        c.setFont("Helvetica", 12)
        y = height - 80
        # عناوين الأعمدة
        if current_lang == "ar":
            c.drawString(50, y, "الاسم")
            c.drawString(200, y, "النوع")
            c.drawString(300, y, "الفريق")
            c.drawString(400, y, "النقاط")
            c.drawString(480, y, "الأحداث")
        else:
            c.drawString(50, y, "Name")
            c.drawString(200, y, "Type")
            c.drawString(300, y, "Team")
            c.drawString(400, y, "Points")
            c.drawString(480, y, "Events")
        y -= 20
        for p in participants:
            team_display = p["team"]
            if current_lang == "en" and p["team"] in TEAM_NAMES["ar"]:
                idx = TEAM_NAMES["ar"].index(p["team"])
                team_display = TEAM_NAMES["en"][idx]
            c.drawString(50, y, p["name"])
            c.drawString(200, y, p["type"])
            c.drawString(300, y, team_display)
            c.drawString(400, y, str(p["points"]))
            c.drawString(480, y, str(len(p["events"])))
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        msg = tr(f"تم التصدير إلى {filename}", f"Exported to {filename}")
        messagebox.showinfo(tr("تصدير", "Export"), msg)
    except Exception as e:
        messagebox.showerror(tr("خطأ", "Error"), tr(f"فشل التصدير: {e}", f"Export failed: {e}"))

# ------------------------------
# دوال إضافية: رسم بياني، إدارة الأحداث، شريط التقدم، المساعدة
# ------------------------------
def show_chart():
    if not participants:
        messagebox.showinfo(tr("معلومات", "Info"), tr("لا توجد بيانات للرسم", "No data to plot"))
        return
    # تجميع النقاط حسب الفريق
    team_points = {}
    for p in participants:
        if p["type"] == "Team" and p["team"]:
            team_points[p["team"]] = team_points.get(p["team"], 0) + p["points"]
    if not team_points:
        messagebox.showinfo(tr("معلومات", "Info"), tr("لا توجد فرق", "No teams"))
        return

    # رسم بياني
    fig, ax = plt.subplots(figsize=(6,4))
    teams = list(team_points.keys())
    points = list(team_points.values())
    if current_lang == "en":
        # ترجمة أسماء الفرق
        teams_en = [TEAM_NAMES["en"][TEAM_NAMES["ar"].index(t)] for t in teams]
        ax.bar(teams_en, points, color='green')
    else:
        ax.bar(teams, points, color='green')
    ax.set_xlabel(tr("الفريق", "Team"))
    ax.set_ylabel(tr("النقاط", "Points"))
    ax.set_title(tr("توزيع النقاط بين الفرق", "Points Distribution Among Teams"))

    # عرض الرسم في نافذة جديدة
    chart_win = ctk.CTkToplevel(window)
    chart_win.title(tr("الرسم البياني", "Chart"))
    chart_win.geometry("700x500")
    canvas = FigureCanvasTkAgg(fig, master=chart_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def manage_events():
    """نافذة لإضافة أو تعديل الأحداث"""
    events_win = ctk.CTkToplevel(window)
    events_win.title(tr("إدارة الأحداث", "Manage Events"))
    events_win.geometry("800x600")
    events_win.transient(window)
    events_win.grab_set()

    # إطار للأزرار
    btn_frame = ctk.CTkFrame(events_win)
    btn_frame.pack(fill="x", padx=10, pady=5)

    def add_new_event():
        # نافذة إضافة حدث
        add_win = ctk.CTkToplevel(events_win)
        add_win.title(tr("إضافة حدث", "Add Event"))
        add_win.geometry("400x400")
        add_win.transient(events_win)
        add_win.grab_set()

        ctk.CTkLabel(add_win, text=tr("الاسم بالعربية:", "Arabic Name:")).pack(pady=5)
        ar_entry = ctk.CTkEntry(add_win, width=300)
        ar_entry.pack(pady=5)

        ctk.CTkLabel(add_win, text=tr("الاسم بالإنجليزية:", "English Name:")).pack(pady=5)
        en_entry = ctk.CTkEntry(add_win, width=300)
        en_entry.pack(pady=5)

        ctk.CTkLabel(add_win, text=tr("الفئة:", "Category:")).pack(pady=5)
        cat_var = tk.StringVar(value=tr("رياضي", "Sports"))
        cat_combo = ctk.CTkComboBox(add_win, values=[tr("رياضي", "Sports"), tr("أكاديمي", "Academic")], variable=cat_var, state="readonly")
        cat_combo.pack(pady=5)

        ctk.CTkLabel(add_win, text=tr("النوع:", "Type:")).pack(pady=5)
        type_var = tk.StringVar(value=tr("فردي", "Individual"))
        type_combo = ctk.CTkComboBox(add_win, values=[tr("فردي", "Individual"), tr("جماعي", "Team")], variable=type_var, state="readonly")
        type_combo.pack(pady=5)

        def save_new_event():
            ar_name = ar_entry.get().strip()
            en_name = en_entry.get().strip()
            category = cat_var.get()
            etype = type_var.get()
            if not ar_name or not en_name:
                messagebox.showerror(tr("خطأ", "Error"), tr("جميع الحقول مطلوبة", "All fields required"))
                return
            # تحويل الفئة والنوع إلى القيم الداخلية (عربية)
            cat_ar = "رياضي" if category == tr("رياضي", "Sports") else "أكاديمي"
            is_team = (etype == tr("جماعي", "Team"))
            new_id = max(e["id"] for e in all_events) + 1
            all_events.append({
                "id": new_id,
                "name_ar": ar_name,
                "name_en": en_name,
                "category_ar": cat_ar,
                "category_en": "Sports" if cat_ar == "رياضي" else "Academic",
                "is_team": is_team,
                "results": {}
            })
            save_data()
            add_win.destroy()
            messagebox.showinfo(tr("نجاح", "Success"), tr("تمت الإضافة", "Added"))
            refresh_events_list()

        ctk.CTkButton(add_win, text=tr("حفظ", "Save"), command=save_new_event).pack(pady=10)

    ctk.CTkButton(btn_frame, text=tr("إضافة حدث", "Add Event"), command=add_new_event).pack(side="left", padx=5)

    # جدول لعرض الأحداث
    tree_frame = ctk.CTkFrame(events_win)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
    columns = ("id", "name_ar", "name_en", "category", "type")
    event_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    event_tree.pack(fill="both", expand=True)
    event_tree.heading("id", text="ID")
    event_tree.heading("name_ar", text=tr("الاسم عربي", "Arabic Name"))
    event_tree.heading("name_en", text=tr("الاسم إنجليزي", "English Name"))
    event_tree.heading("category", text=tr("الفئة", "Category"))
    event_tree.heading("type", text=tr("النوع", "Type"))

    def refresh_events_list():
        for row in event_tree.get_children():
            event_tree.delete(row)
        for e in all_events:
            cat = e["category_ar"] if current_lang == "ar" else e["category_en"]
            typ = tr("جماعي", "Team") if e["is_team"] else tr("فردي", "Individual")
            event_tree.insert("", tk.END, values=(e["id"], e["name_ar"], e["name_en"], cat, typ))

    refresh_events_list()

    # أزرار تعديل/حذف
    edit_frame = ctk.CTkFrame(events_win)
    edit_frame.pack(fill="x", padx=10, pady=5)

    def edit_selected_event():
        selected = event_tree.selection()
        if not selected:
            return
        event_id = int(event_tree.item(selected[0])['values'][0])
        event = next((e for e in all_events if e["id"] == event_id), None)
        if not event:
            return
        # نافذة تعديل مشابهة للإضافة
        edit_win = ctk.CTkToplevel(events_win)
        edit_win.title(tr("تعديل حدث", "Edit Event"))
        edit_win.geometry("400x400")
        edit_win.transient(events_win)
        edit_win.grab_set()

        ctk.CTkLabel(edit_win, text=tr("الاسم بالعربية:", "Arabic Name:")).pack(pady=5)
        ar_entry = ctk.CTkEntry(edit_win, width=300)
        ar_entry.insert(0, event["name_ar"])
        ar_entry.pack(pady=5)

        ctk.CTkLabel(edit_win, text=tr("الاسم بالإنجليزية:", "English Name:")).pack(pady=5)
        en_entry = ctk.CTkEntry(edit_win, width=300)
        en_entry.insert(0, event["name_en"])
        en_entry.pack(pady=5)

        ctk.CTkLabel(edit_win, text=tr("الفئة:", "Category:")).pack(pady=5)
        cat_var = tk.StringVar(value=event["category_ar"] if current_lang == "ar" else event["category_en"])
        cat_combo = ctk.CTkComboBox(edit_win, values=[tr("رياضي", "Sports"), tr("أكاديمي", "Academic")], variable=cat_var, state="readonly")
        cat_combo.pack(pady=5)

        ctk.CTkLabel(edit_win, text=tr("النوع:", "Type:")).pack(pady=5)
        type_var = tk.StringVar(value=tr("جماعي", "Team") if event["is_team"] else tr("فردي", "Individual"))
        type_combo = ctk.CTkComboBox(edit_win, values=[tr("فردي", "Individual"), tr("جماعي", "Team")], variable=type_var, state="readonly")
        type_combo.pack(pady=5)

        def save_edit_event():
            new_ar = ar_entry.get().strip()
            new_en = en_entry.get().strip()
            category = cat_var.get()
            etype = type_var.get()
            if not new_ar or not new_en:
                messagebox.showerror(tr("خطأ", "Error"), tr("جميع الحقول مطلوبة", "All fields required"))
                return
            cat_ar = "رياضي" if category == tr("رياضي", "Sports") else "أكاديمي"
            is_team = (etype == tr("جماعي", "Team"))
            event["name_ar"] = new_ar
            event["name_en"] = new_en
            event["category_ar"] = cat_ar
            event["category_en"] = "Sports" if cat_ar == "رياضي" else "Academic"
            event["is_team"] = is_team
            save_data()
            edit_win.destroy()
            refresh_events_list()
            messagebox.showinfo(tr("نجاح", "Success"), tr("تم التعديل", "Edited"))

        ctk.CTkButton(edit_win, text=tr("حفظ", "Save"), command=save_edit_event).pack(pady=10)

    def delete_selected_event():
        selected = event_tree.selection()
        if not selected:
            return
        event_id = int(event_tree.item(selected[0])['values'][0])
        event = next((e for e in all_events if e["id"] == event_id), None)
        if not event:
            return
        # التحقق من عدم وجود نتائج مسجلة
        if event["results"]:
            messagebox.showerror(tr("خطأ", "Error"), tr("لا يمكن حذف حدث له نتائج مسجلة", "Cannot delete an event with recorded results"))
            return
        confirm = tr(f"هل تريد حذف الحدث {event['name_ar']}؟", f"Delete event {event['name_en']}?")
        if messagebox.askyesno(tr("تأكيد", "Confirm"), confirm):
            all_events.remove(event)
            save_data()
            refresh_events_list()

    ctk.CTkButton(edit_frame, text=tr("تعديل", "Edit"), command=edit_selected_event).pack(side="left", padx=5)
    ctk.CTkButton(edit_frame, text=tr("حذف", "Delete"), command=delete_selected_event).pack(side="left", padx=5)

def update_progress_bars():
    """تحديث أشرطة التقدم: عدد الأفراد وعدد أعضاء كل فريق"""
    # الأفراد
    individual_count = sum(1 for p in participants if p["type"] == "Individual")
    if progress_individual:  # التأكد من أن المتغير موجود
        progress_individual.set(individual_count / 20)
    if lbl_individual_progress:
        lbl_individual_progress.configure(text=tr(f"الأفراد: {individual_count}/20", f"Individuals: {individual_count}/20"))

    # الفرق
    for i, team_ar in enumerate(TEAM_NAMES["ar"]):
        team_count = sum(1 for p in participants if p["type"] == "Team" and p["team"] == team_ar)
        if i < len(progress_teams):
            progress_teams[i].set(team_count / 5)
        if i < len(lbl_team_progress):
            lbl_team_progress[i].configure(text=tr(f"{team_ar}: {team_count}/5", f"{TEAM_NAMES['en'][i]}: {team_count}/5"))

def show_help():
    help_text = tr(
        """
دليل المستخدم - نظام إدارة البطولة

الحدود:
- الحد الأقصى للأفراد: 20
- الحد الأقصى لأعضاء الفريق الواحد: 5
- الحد الأقصى للأحداث لكل مشارك: 5

كيفية الاستخدام:
1. إضافة مشارك: اختر النوع (فردي/فريق)، أدخل الاسم، واختر الفريق إذا كان فريقاً، ثم اضغط إضافة.
2. تسجيل نتيجة: اختر الفئة (رياضي/أكاديمي)، ثم اختر الحدث، أدخل اسم المشارك والترتيب، ثم اضغط إضافة نتيجة.
3. يمكنك تعديل أو حذف مشارك من خلال الجدول.
4. عرض التفاصيل: حدد مشاركاً واضغط على زر "تفاصيل".
5. يمكنك تصدير النتائج إلى CSV أو PDF.
6. يمكنك إدارة الأحداث (إضافة، تعديل، حذف) من زر "إدارة الأحداث".
7. يمكنك عرض رسم بياني لتوزيع النقاط بين الفرق.

ملاحظات:
- الأسماء يجب أن تكون فريدة.
- عند حذف مشارك له نتائج، سيتم حذف نتائجه أيضاً.
- يتم حفظ البيانات تلقائياً بعد كل عملية.
        """,
        """
User Guide - Tournament Management System

Limits:
- Maximum individuals: 20
- Maximum team members per team: 5
- Maximum events per participant: 5

How to use:
1. Add participant: Choose type (Individual/Team), enter name, select team if team, then click Add.
2. Record result: Choose category (Sports/Academic), select event, enter participant name and rank, then click Add Result.
3. You can edit or delete a participant from the table.
4. View details: Select a participant and click "Details".
5. You can export results to CSV or PDF.
6. You can manage events (add, edit, delete) from "Manage Events" button.
7. You can view a chart of points distribution among teams.

Notes:
- Names must be unique.
- When deleting a participant with results, their results will also be deleted.
- Data is automatically saved after each operation.
        """
    )
    messagebox.showinfo(tr("مساعدة", "Help"), help_text)

# ------------------------------
# بناء واجهة المستخدم
# ------------------------------
window = ctk.CTk()
window.geometry("1400x900")
window.title(tr("نظام إدارة البطولة", "Tournament Management System"))

# إطار علوي مع شعار وأزرار
top_frame = ctk.CTkFrame(window)
top_frame.pack(fill="x", padx=10, pady=5)

lang_btn = ctk.CTkButton(top_frame, text="English", width=80, command=toggle_language)
lang_btn.pack(side="right", padx=5)

title_label = ctk.CTkLabel(top_frame, text=tr("🏆 نظام إدارة البطولة", "🏆 Tournament Management System"), font=("Cairo", 20, "bold"))
title_label.pack(side="left", padx=10)

# لوحة المعلومات مع زر عرض التفاصيل
dashboard_frame = ctk.CTkFrame(window)
dashboard_frame.pack(fill="x", padx=10, pady=5)

# إطار داخلي للعنوان والزر
dashboard_header = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
dashboard_header.pack(fill="x", padx=5, pady=2)

lbl_dashboard = ctk.CTkLabel(dashboard_header, text=tr("لوحة المعلومات", "Dashboard"), font=("Cairo", 14, "bold"))
lbl_dashboard.pack(side="left", padx=5)

btn_dashboard_details = ctk.CTkButton(dashboard_header, text=tr("عرض التفاصيل", "View Details"), width=120, command=show_dashboard_details)
btn_dashboard_details.pack(side="right", padx=5)

lbl_dashboard_value = ctk.CTkLabel(dashboard_frame, text="", font=("Segoe UI", 12), justify="left")
lbl_dashboard_value.pack(anchor="w", padx=5)

# أشرطة التقدم
progress_frame = ctk.CTkFrame(window)
progress_frame.pack(fill="x", padx=10, pady=5)

# تقدم الأفراد
ind_frame = ctk.CTkFrame(progress_frame)
ind_frame.pack(side="left", padx=10, fill="x", expand=True)
lbl_individual_progress = ctk.CTkLabel(ind_frame, text=tr("الأفراد: 0/20", "Individuals: 0/20"))
lbl_individual_progress.pack()
progress_individual = ctk.DoubleVar()
ind_progress = ctk.CTkProgressBar(ind_frame, variable=progress_individual)
ind_progress.pack(fill="x", padx=5)
ind_progress.set(0)

# تقدم الفرق (4 أشرطة)
progress_teams = []
lbl_team_progress = []
for i, team_ar in enumerate(TEAM_NAMES["ar"]):
    team_frame = ctk.CTkFrame(progress_frame)
    team_frame.pack(side="left", padx=5, fill="x", expand=True)
    lbl = ctk.CTkLabel(team_frame, text=tr(f"{team_ar}: 0/5", f"{TEAM_NAMES['en'][i]}: 0/5"))
    lbl.pack()
    prog = ctk.DoubleVar()
    bar = ctk.CTkProgressBar(team_frame, variable=prog)
    bar.pack(fill="x", padx=5)
    bar.set(0)
    progress_teams.append(prog)
    lbl_team_progress.append(lbl)

# نوع المشارك
frame_type = ctk.CTkFrame(window)
frame_type.pack(fill="x", padx=10, pady=5)
lbl_type = ctk.CTkLabel(frame_type, text=tr("نوع المشارك", "Participant Type"), font=("Cairo", 12, "bold"))
lbl_type.pack(side="left", padx=5)

participant_type = tk.StringVar(value="Individual")  # المتغير الذي أشار إليه المستخدم

radio_ind = ctk.CTkRadioButton(frame_type, text=tr("فردي", "Individual"), variable=participant_type, value="Individual", command=toggle_team_selection)
radio_ind.pack(side="left", padx=5)
radio_team = ctk.CTkRadioButton(frame_type, text=tr("فريق", "Team"), variable=participant_type, value="Team", command=toggle_team_selection)
radio_team.pack(side="left", padx=5)

# إضافة مشارك
frame_add = ctk.CTkFrame(window)
frame_add.pack(fill="x", padx=10, pady=5)
lbl_name = ctk.CTkLabel(frame_add, text=tr("الاسم:", "Name:"), font=("Cairo", 12))
lbl_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_name = ctk.CTkEntry(frame_add, width=200)
entry_name.grid(row=0, column=1, padx=5, pady=5)

lbl_team_select = ctk.CTkLabel(frame_add, text=tr("اختر الفريق:", "Select Team:"), font=("Cairo", 12))
lbl_team_select.grid(row=1, column=0, padx=5, pady=5, sticky="w")
team_combo = ctk.CTkComboBox(frame_add, values=TEAM_NAMES[current_lang], width=200, state="readonly")
team_combo.grid(row=1, column=1, padx=5, pady=5)
team_combo.set(TEAM_NAMES[current_lang][0])

btn_add = ctk.CTkButton(frame_add, text=tr("إضافة مشارك", "Add Participant"), command=add_participant)
btn_add.grid(row=0, column=2, padx=10, rowspan=2)

# فئة الفعالية
frame_category = ctk.CTkFrame(window)
frame_category.pack(fill="x", padx=10, pady=5)
lbl_category = ctk.CTkLabel(frame_category, text=tr("فئة الفعالية", "Event Category"), font=("Cairo", 12, "bold"))
lbl_category.pack(side="left", padx=5)
category_var = tk.StringVar(value="رياضي")
btn_sports = ctk.CTkButton(frame_category, text=tr("رياضي", "Sports"), width=100, command=lambda: select_category("رياضي"))
btn_sports.pack(side="left", padx=5)
btn_academic = ctk.CTkButton(frame_category, text=tr("أكاديمي", "Academic"), width=100, command=lambda: select_category("أكاديمي"))
btn_academic.pack(side="left", padx=5)

# اختيار الفعالية
frame_event = ctk.CTkFrame(window)
frame_event.pack(fill="x", padx=10, pady=5)
lbl_event = ctk.CTkLabel(frame_event, text=tr("الفعالية:", "Event:"), font=("Cairo", 12))
lbl_event.pack(side="left", padx=5)
event_combo = ctk.CTkComboBox(frame_event, values=[], width=400, state="readonly")
event_combo.pack(side="left", padx=5)

# جدول المشاركين
frame_table = ctk.CTkFrame(window)
frame_table.pack(fill="both", expand=True, padx=10, pady=5)
lbl_participants = ctk.CTkLabel(frame_table, text=tr("المشاركون", "Participants"), font=("Cairo", 14, "bold"))
lbl_participants.pack(anchor="w", padx=5)

search_frame = ctk.CTkFrame(frame_table)
search_frame.pack(fill="x", padx=5, pady=5)
search_entry = ctk.CTkEntry(search_frame, placeholder_text=tr("بحث بالاسم...", "Search by name..."), width=200)
search_entry.pack(side="left", padx=5)
btn_search = ctk.CTkButton(search_frame, text=tr("بحث", "Search"), width=60, command=search_participant)
btn_search.pack(side="left", padx=5)
btn_edit = ctk.CTkButton(search_frame, text=tr("تعديل", "Edit"), width=60, command=edit_participant)
btn_edit.pack(side="left", padx=5)
btn_delete = ctk.CTkButton(search_frame, text=tr("حذف", "Delete"), width=60, command=delete_participant)
btn_delete.pack(side="left", padx=5)
btn_details = ctk.CTkButton(search_frame, text=tr("تفاصيل", "Details"), width=60, command=show_participant_details)
btn_details.pack(side="left", padx=5)

columns = ("Name", "Type", "Team", "Points", "Events")
tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=12)
tree.pack(fill="both", expand=True, padx=5, pady=5)
tree.heading("Name", text=tr("الاسم", "Name"))
tree.heading("Type", text=tr("النوع", "Type"))
tree.heading("Team", text=tr("الفريق", "Team"))
tree.heading("Points", text=tr("النقاط", "Points"))
tree.heading("Events", text=tr("الأحداث", "Events"))
tree.column("Name", width=200)
tree.column("Type", width=100)
tree.column("Team", width=150)
tree.column("Points", width=100)
tree.column("Events", width=80)
tree.tag_configure('odd', background='#2b2b2b')
tree.tag_configure('even', background='#3b3b3b')

# إضافة نتيجة
frame_score = ctk.CTkFrame(window)
frame_score.pack(fill="x", padx=10, pady=5)
lbl_score_name = ctk.CTkLabel(frame_score, text=tr("اسم المشارك:", "Participant Name:"), font=("Cairo", 12))
lbl_score_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_score_name = ctk.CTkEntry(frame_score, width=150)
entry_score_name.grid(row=0, column=1, padx=5, pady=5)
lbl_rank = ctk.CTkLabel(frame_score, text=tr("الترتيب:", "Rank:"), font=("Cairo", 12))
lbl_rank.grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_rank = ctk.CTkEntry(frame_score, width=80)
entry_rank.grid(row=0, column=3, padx=5, pady=5)
btn_add_score = ctk.CTkButton(frame_score, text=tr("إضافة نتيجة", "Add Result"), command=add_result)
btn_add_score.grid(row=0, column=4, padx=10, pady=5)

# النتائج النهائية والتصدير
frame_result = ctk.CTkFrame(window)
frame_result.pack(fill="x", padx=10, pady=5)
lbl_results = ctk.CTkLabel(frame_result, text=tr("النتائج النهائية", "Final Results"), font=("Cairo", 14, "bold"))
lbl_results.pack(side="left", padx=5)
btn_results = ctk.CTkButton(frame_result, text=tr("عرض النتائج", "Show Results"), command=show_results)
btn_results.pack(side="left", padx=5)
btn_export_csv = ctk.CTkButton(frame_result, text=tr("تصدير CSV", "Export CSV"), command=export_csv)
btn_export_csv.pack(side="left", padx=5)
btn_export_pdf = ctk.CTkButton(frame_result, text=tr("تصدير PDF", "Export PDF"), command=export_pdf)
btn_export_pdf.pack(side="left", padx=5)

# أزرار إضافية
frame_extra = ctk.CTkFrame(window)
frame_extra.pack(fill="x", padx=10, pady=5)
btn_chart = ctk.CTkButton(frame_extra, text=tr("عرض الرسم البياني", "Show Chart"), command=show_chart)
btn_chart.pack(side="left", padx=5)
btn_manage_events = ctk.CTkButton(frame_extra, text=tr("إدارة الأحداث", "Manage Events"), command=manage_events)
btn_manage_events.pack(side="left", padx=5)
btn_help = ctk.CTkButton(frame_extra, text=tr("مساعدة", "Help"), command=show_help)
btn_help.pack(side="left", padx=5)

# تحميل البيانات المحفوظة
load_data()

# تحديث الواجهة بالترتيب الصحيح
update_table()
update_dashboard_text()
update_progress_bars()
update_event_list()
toggle_team_selection()  # تفعيل/تعطيل اختيار الفريق حسب النوع الافتراضي

# تشغيل التطبيق
window.mainloop()