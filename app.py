from flask import Flask, request, render_template, jsonify
import json
from datetime import datetime, date, timedelta
import os
import smtplib
from email.mime.text import MIMEText
import logging  # اضافه کردن ماژول لاگینگ

app = Flask(__name__)

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # ذخیره لاگ‌ها تو یه فایل
        logging.StreamHandler()  # نمایش لاگ‌ها تو کنسول
    ]
)

TASKS_FILE = "tasks.json"

def load_tasks():
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    task["deadline"] = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
                    if "priority" not in task:
                        task["priority"] = "Medium"
                logging.info(f"Tasks loaded successfully: {tasks}")
                return tasks
        logging.info("No tasks file found, starting with empty list")
        return []
    except Exception as e:
        logging.error(f"Error loading tasks: {str(e)}")
        raise
def save_tasks(tasks):
    try:
        tasks_to_save = [
            {
                "title": task["title"],
                "duration": task["duration"],
                "deadline": task["deadline"].isoformat(),
                "priority": task["priority"]
            }
            for task in tasks
        ]
        # غیرفعال کردن ذخیره‌سازی فایل موقتاً
        logging.info(f"Would save tasks to {TASKS_FILE}: {tasks_to_save}")
        # with open(TASKS_FILE, "w") as f:
        #     json.dump(tasks_to_save, f, indent=4)
        # logging.info("Tasks saved successfully")
    except Exception as e:
        logging.error(f"Error saving tasks: {str(e)}")
        raise


def send_new_task_reminder(task, email_to, days_before):
    try:
        email_from = os.getenv("EMAIL_FROM", "default_email@example.com")
        password = os.getenv("EMAIL_PASSWORD", "default_password")

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

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_from, password)
            server.send_message(msg)
        logging.info(f"Reminder sent for new task: {task['title']} ({days_before} day(s) before deadline) to {email_to}")
    except Exception as e:
        logging.error(f"Error sending reminder for new task '{task['title']}': {str(e)}")
        logging.error(f"Debug - Email details: From={email_from}, To={email_to}, Subject={msg['Subject']}")
        raise

def send_update_reminder(task, old_task, email_to, days_before):
    try:
        email_from = os.getenv("EMAIL_FROM", "default_email@example.com")
        password = os.getenv("EMAIL_PASSWORD", "default_password")

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

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_from, password)
            server.send_message(msg)
        logging.info(f"Reminder sent for updated task: {task['title']} ({days_before} day(s) before deadline) to {email_to}")
    except Exception as e:
        logging.error(f"Error sending reminder for updated task '{task['title']}': {str(e)}")
        logging.error(f"Debug - Email details: From={email_from}, To={email_to}, Subject={msg['Subject']}")
        raise

# بارگذاری تسک‌ها وقتی برنامه اجرا می‌شه
tasks = load_tasks()

@app.route("/", methods=["GET", "POST"])
def home():
    try:
        if request.method == "POST":
            if "title" in request.form:
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
                    logging.info(f"Task added: {task}")
                    today = date.today()
                    days_diff = (task["deadline"] - today).days
                    if days_diff in [0, 1, 2]:
                        logging.info("Would send new task reminder")  # غیرفعال کردن موقت ایمیل
                        # send_new_task_reminder(task, "majid_0280@yahoo.com", days_diff)
                except ValueError as e:
                    logging.error(f"Error adding task: {e}")
                    task = {"title": title, "duration": duration, "deadline": f"{year}-{month}-{day}", "priority": priority}
                    tasks.append(task)
            elif "delete" in request.form:
                task_index = int(request.form["delete"])
                if 0 <= task_index < len(tasks):
                    tasks.pop(task_index)
                    logging.info(f"Task deleted at index {task_index}")
        tasks.sort(key=lambda x: (x["deadline"], {"Low": 3, "Medium": 2, "High": 1}[x["priority"]]))
        enumerated_tasks = list(enumerate(tasks))
        formatted_tasks = []
        for index, task in enumerated_tasks:
            task_copy = task.copy()
            task_copy["deadline"] = task["deadline"].strftime("%Y-%m-%d")
            formatted_tasks.append((index, task_copy))
        save_tasks(tasks)
        logging.info("Rendering home page")
        return render_template("index.html", tasks=formatted_tasks)
    except Exception as e:
        logging.error(f"Error in home route: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error in home route: {str(e)}"}), 500

@app.route("/edit_task/<int:index>", methods=["POST"])
def edit_task(index):
    try:
        logging.info(f"Received edit request for index {index}")
        if 0 <= index < len(tasks):
            data = request.get_json()
            logging.info(f"Received data: {data}")
            if data:
                title = data.get("title", tasks[index]["title"])
                duration = data.get("duration", tasks[index]["duration"])
                day = data.get("day")
                month = data.get("month")
                year = data.get("year")
                priority = data.get("priority", tasks[index]["priority"])

                logging.info(f"Extracted values: title={title}, duration={duration}, day={day}, month={month}, year={year}, priority={priority}")

                if not all([day, month, year]):
                    logging.warning("Missing required date fields")
                    return jsonify({"status": "error", "message": "Day, month, and year are required"}), 400

                current_deadline = tasks[index]["deadline"]
                if not isinstance(current_deadline, date):
                    logging.error("Current deadline is not a valid date object")
                    return jsonify({"status": "error", "message": "Current deadline is not a valid date object"}), 500

                default_day = current_deadline.day
                default_month = current_deadline.month
                default_year = current_deadline.year

                try:
                    day = int(day) if day else default_day
                    month = int(month) if month else default_month
                    year = int(year) if year else default_year
                except ValueError as e:
                    logging.error(f"Error converting date values to integers: {str(e)}")
                    return jsonify({"status": "error", "message": "Invalid date values: day, month, and year must be integers"}), 400

                logging.info(f"Using values: day={day}, month={month}, year={year}")

                try:
                    deadline = date(year, month, day)
                except ValueError as e:
                    logging.error(f"ValueError creating date: {str(e)}")
                    return jsonify({"status": "error", "message": f"Invalid date: {str(e)}"}), 400

                old_task = tasks[index].copy()
                tasks[index] = {
                    "title": title,
                    "duration": int(duration) if duration else 0,
                    "deadline": deadline,
                    "priority": priority
                }

                logging.info(f"Saving tasks: {tasks}")
                save_tasks(tasks)
                logging.info(f"Task edited at index {index}: {tasks[index]}")

                today = date.today()
                days_diff = (tasks[index]["deadline"] - today).days
                logging.info(f"Days difference: {days_diff}")
                logging.info(f"Deadline: {tasks[index]['deadline']}")
                logging.info(f"Old Deadline: {old_task['deadline']}")
                logging.info(f"Priority: {tasks[index]['priority']}")
                logging.info(f"Old Priority: {old_task['priority']}")
                logging.info(f"Deadline changed: {tasks[index]['deadline'] != old_task['deadline']}")
                logging.info(f"Priority changed: {tasks[index]['priority'] != old_task['priority']}")

                if days_diff in [0, 1, 2]:
                    if tasks[index]["deadline"] != old_task["deadline"] or tasks[index]["priority"] != old_task["priority"]:
                        logging.info("Would send update reminder")
                        # send_update_reminder(tasks[index], old_task, "majid_0280@yahoo.com", days_diff)

                updated_tasks = [{"index": i, "task": task} for i, task in enumerate(tasks)]
                task_response = tasks[index].copy()
                task_response["deadline"] = tasks[index]["deadline"].strftime("%Y-%m-%d")
                updated_tasks_formatted = [{"index": i, "task": {**task, "deadline": task["deadline"].strftime("%Y-%m-%d")}} for i, task in updated_tasks]

                logging.info(f"Returning response: {{'status': 'success', 'task': {task_response}, 'tasks': {updated_tasks_formatted}}}")
                return jsonify({"status": "success", "task": task_response, "tasks": updated_tasks_formatted})
            else:
                logging.warning("No data provided in request")
                return jsonify({"status": "error", "message": "No data provided"}), 400
        else:
            logging.warning(f"Task not found at index {index}")
            return jsonify({"status": "error", "message": "Task not found"}), 404
    except Exception as e:
        logging.error(f"Error in edit_task: {str(e)}", exc_info=True)  # چاپ استک کامل خطا
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
