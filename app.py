from flask import Flask, request, render_template, redirect, url_for, jsonify
import json
from datetime import datetime, date, timedelta
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            for task in tasks:
                task["deadline"] = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
                if "priority" not in task:
                    task["priority"] = "Medium"
            return tasks
    return []


def save_tasks(tasks):
    tasks_to_save = [
        {
            "title": task["title"],
            "duration": task["duration"],
            "deadline": task["deadline"].isoformat(),
            "priority": task["priority"]
        }
        for task in tasks
    ]
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks_to_save, f, indent=4)
    except Exception as e:
       print(f"Error saving tasks to {TASKS_FILE}: {str(e)}")
       raise

def send_new_task_reminder(task, email_to, days_before):
    # تنظیمات ایمیل برای Gmail
    email_from = os.getenv("EMAIL_FROM", "default_email@example.com")
    password = os.getenv("EMAIL_PASSWORD", "default_password")
    
    # ساخت متن ایمیل با فقط اطلاعات فعلی برای تسک جدید
    reminder_text = f"New Task Notification:\n\n"
    reminder_text += f"- Title: {task['title']}\n"
    reminder_text += f"- Duration: {task['duration']} min\n"
    reminder_text += f"- Deadline: {task['deadline']}\n"
    reminder_text += f"- Priority: {task['priority']}\n\n"
    
    if days_before == 0:
        reminder_text += f"Today: This task is due today ({task['deadline']}) with priority {task['priority']}."
    elif days_before == 1:
        reminder_text += f"Tomorrow: This task is due tomorrow ({task['deadline']}) with priority {task['priority']}."
    elif days_before == 2:
        reminder_text += f"2 Days Left: This task is due in 2 days ({task['deadline']}) with priority {task['priority']}."

    msg = MIMEText(reminder_text)
    msg['Subject'] = f"New Task & Reminder: {task['title']} ({days_before} day(s) left)"
    msg['From'] = email_from
    msg['To'] = email_to

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_from, password)
            server.send_message(msg)
        print(f"Reminder sent for new task: {task['title']} ({days_before} day(s) before deadline) to {email_to}")
    except Exception as e:
        print(f"Error sending reminder for new task '{task['title']}': {e}")
        # چاپ دیباگ بیشتر برای خطاها
        print(f"Debug - Email details: From={email_from}, To={email_to}, Subject={msg['Subject']}")
        print(f"Debug - Full exception: {str(e)}")

def send_update_reminder(task, old_task, email_to, days_before):
    # تنظیمات ایمیل برای Gmail
    email_from = "arashar905@gmail.com"  # ایمیل فرستنده
    password = "maym ugmc dytw mbkm"  # رمز عبور اپلیکیشن Gmail
    
    # ساخت متن ایمیل با اطلاعات قبلی و فعلی برای تسک ویرایش‌شده
    reminder_text = f"Task Update Notification:\n\n"
    reminder_text += f"Previous Task Details:\n"
    reminder_text += f"- Title: {old_task['title']}\n"
    reminder_text += f"- Duration: {old_task['duration']} min\n"
    reminder_text += f"- Deadline: {old_task['deadline']}\n"
    reminder_text += f"- Priority: {old_task['priority']}\n\n"
    reminder_text += f"Updated Task Details:\n"
    reminder_text += f"- Title: {task['title']}\n"
    reminder_text += f"- Duration: {task['duration']} min\n"
    reminder_text += f"- Deadline: {task['deadline']}\n"
    reminder_text += f"- Priority: {task['priority']}\n\n"
    
    if days_before == 0:
        reminder_text += f"Today: This task is due today ({task['deadline']}) with priority {task['priority']}."
    elif days_before == 1:
        reminder_text += f"Tomorrow: This task is due tomorrow ({task['deadline']}) with priority {task['priority']}."
    elif days_before == 2:
        reminder_text += f"2 Days Left: This task is due in 2 days ({task['deadline']}) with priority {task['priority']}."

    msg = MIMEText(reminder_text)
    msg['Subject'] = f"Task Update & Reminder: {task['title']} ({days_before} day(s) left)"
    msg['From'] = email_from
    msg['To'] = email_to

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_from, password)
            server.send_message(msg)
        print(f"Reminder sent for updated task: {task['title']} ({days_before} day(s) before deadline) to {email_to}")
    except Exception as e:
        print(f"Error sending reminder for updated task '{task['title']}': {e}")
        # چاپ دیباگ بیشتر برای خطاها
        print(f"Debug - Email details: From={email_from}, To={email_to}, Subject={msg['Subject']}")
        print(f"Debug - Full exception: {str(e)}")

# بارگذاری تسک‌ها وقتی برنامه اجرا می‌شه
tasks = load_tasks()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if "title" in request.form:  # اضافه کردن تسک
            title = request.form.get("title", "No title")
            duration = request.form.get("duration", "0")
            day = request.form.get("day", "1")
            month = request.form.get("month", "1")
            year = request.form.get("year", "2025")
            priority = request.form.get("priority", "Medium")
            try:
                deadline = date(int(year), int(month), int(day))
                task = {
                    "title": title,
                    "duration": int(duration),
                    "deadline": deadline,
                    "priority": priority
                }
                tasks.append(task)
                print(f"Task added: {task}")
                # ارسال یادآوری برای تسک جدید
                today = date.today()
                days_diff = (task["deadline"] - today).days
                if days_diff in [0, 1, 2]:  # یادآوری برای امروز (0)، فردا (1)، و ۲ روز قبل (2)
                    send_new_task_reminder(task, "majid_0280@yahoo.com", days_diff)  # ایمیل گیرنده به‌روزرسانی‌شده
            except ValueError as e:
                print(f"Error adding task: {e}")
                task = {"title": title, "duration": duration, "deadline": f"{year}-{month}-{day}", "priority": priority}
                tasks.append(task)
        elif "delete" in request.form:  # حذف تسک
            task_index = int(request.form["delete"])
            if 0 <= task_index < len(tasks):
                tasks.pop(task_index)
                print(f"Task deleted at index {task_index}")
    tasks.sort(key=lambda x: (x["deadline"], {"Low": 3, "Medium": 2, "High": 1}[x["priority"]]))
    enumerated_tasks = list(enumerate(tasks))
    save_tasks(tasks)  # ذخیره تسک‌ها بعد از هر تغییر
    formatted_tasks = []
    for index, task in enumerated_tasks:
    task_copy = task.copy()
    task_copy["deadline"] = task["deadline"].strftime("%Y-%m-%d")
    formatted_tasks.append((index, task_copy))
    return render_template("index.html", tasks=enumerated_tasks)

@app.route("/edit_task/<int:index>", methods=["POST"])
def edit_task(index):
    if 0 <= index < len(tasks):
        data = request.get_json()
        if data:
            title = data.get("title", tasks[index]["title"])
            duration = data.get("duration", tasks[index]["duration"])
            day = data.get("day", tasks[index]["deadline"].day)
            month = data.get("month", tasks[index]["deadline"].month)
            year = data.get("year", tasks[index]["deadline"].year)
            priority = data.get("priority", tasks[index]["priority"])
            try:
                deadline = date(int(year), int(month), int(day))
                old_task = tasks[index].copy()  # کپی کردن تسک قدیمی برای مقایسه
                tasks[index] = {
                    "title": title,
                    "duration": int(duration),
                    "deadline": deadline,
                    "priority": priority
                }
                save_tasks(tasks)
                print(f"Task edited at index {index}: {tasks[index]}")
                # دیباگ برای چک کردن شرط ارسال یادآوری
                today = date.today()
                days_diff = (tasks[index]["deadline"] - today).days
                print(f"Debug - Days difference: {days_diff}")
                print(f"Debug - Deadline: {tasks[index]['deadline']}")
                print(f"Debug - Old Deadline: {old_task['deadline']}")
                print(f"Debug - Priority: {tasks[index]['priority']}")
                print(f"Debug - Old Priority: {old_task['priority']}")
                print(f"Debug - Deadline changed: {tasks[index]['deadline'] != old_task['deadline']}")
                print(f"Debug - Priority changed: {tasks[index]['priority'] != old_task['priority']}")
                # ارسال دوباره یادآوری فقط اگر ددلاین یا اولویت تغییر کرده باشه
                if days_diff in [0, 1, 2]:  # یادآوری برای امروز (0)، فردا (1)، و ۲ روز قبل (2)
                    # فقط اگر ددلاین یا اولویت تغییر کرده، یادآوری بفرست
                    if tasks[index]["deadline"] != old_task["deadline"] or tasks[index]["priority"] != old_task["priority"]:
                        send_update_reminder(tasks[index], old_task, "majid_0280@yahoo.com", days_diff)  # ایمیل گیرنده به‌روزرسانی‌شده
                # برگرداندن لیست به‌روزرسانی‌شده تسک‌ها به‌صورت JSON
                updated_tasks = [{"index": i, "task": task} for i, task in enumerate(tasks)]
                return jsonify({"status": "success", "task": tasks[index], "tasks": updated_tasks})
            except ValueError as e:
                print(f"Error editing task: {e}")
                return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "error", "message": "Task not found"})

if __name__ == "__main__":
    app.run(debug=True)
