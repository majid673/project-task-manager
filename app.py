from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime, date, timedelta
import os
import smtplib
from email.mime.text import MIMEText
import logging

app = Flask(__name__)

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# تنظیم دیتابیس SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعریف مدل Task برای دیتابیس
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration,
            "deadline": self.deadline,
            "priority": self.priority
        }

# ایجاد دیتابیس و جداول
with app.app_context():
    db.create_all()
    logging.info("Database initialized")

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
@app.route("/", methods=["GET", "POST"])
def home():
    try:
        if request.method == "POST":
            logging.info(f"Received POST request with form data: {request.form}")
            if "title" in request.form:
                title = request.form.get("title", "No title")
                duration = request.form.get("duration", "0")
                day = request.form.get("day", "1")
                month = request.form.get("month", "1")
                year = request.form.get("year", "2025")
                priority = request.form.get("priority", "Medium")
                logging.info(f"Extracted form values: title={title}, duration={duration}, day={day}, month={month}, year={year}, priority={priority}")
                try:
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    duration = int(duration)
                    logging.info(f"Converted values: year={year}, month={month}, day={day}, duration={duration}")
                    deadline = date(year, month, day)
                    task = Task(
                        title=title,
                        duration=duration,
                        deadline=deadline,
                        priority=priority
                    )
                    db.session.add(task)
                    db.session.commit()
                    logging.info(f"Task added: {task.to_dict()}")
                    today = date.today()
                    days_diff = (deadline - today).days
                    if days_diff in [0, 1, 2]:
                        logging.info("Would send new task reminder")
                        # send_new_task_reminder(task.to_dict(), "majid_0280@yahoo.com", days_diff)
                except ValueError as e:
                    logging.error(f"Error adding task: {str(e)}")
                    return jsonify({"status": "error", "message": f"Invalid date or duration: {str(e)}"}), 400
                except Exception as e:
                    logging.error(f"Unexpected error adding task: {str(e)}")
                    return jsonify({"status": "error", "message": f"Server error adding task: {str(e)}"}), 500
            elif "delete" in request.form:
                task_id = int(request.form["delete"])
                task = Task.query.get(task_id)
                if task:
                    db.session.delete(task)
                    db.session.commit()
                    logging.info(f"Task deleted with ID {task_id}")
                else:
                    logging.warning(f"Task not found for deletion with ID {task_id}")
        logging.info("Fetching tasks from database")
        tasks = Task.query.order_by(Task.deadline, db.case(
            (Task.priority == "Low", 3),
            (Task.priority == "Medium", 2),
            (Task.priority == "High", 1)
        )).all()
        logging.info(f"Raw tasks from database: {[{ 'id': task.id, 'title': task.title, 'duration': task.duration, 'deadline': task.deadline, 'priority': task.priority } for task in tasks]}")
        formatted_tasks = [task.to_dict() for task in tasks]
        logging.info("Formatting task deadlines")
        for task in formatted_tasks:
            task["deadline"] = task["deadline"].strftime("%Y-%m-%d")
        logging.info(f"Rendering home page with formatted tasks: {formatted_tasks}")
        return render_template("index.html", tasks=formatted_tasks)
    except Exception as e:
        logging.error(f"Error in home route: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error in home route: {str(e)}"}), 500


@app.route("/edit_task/<int:index>", methods=["POST"])
def edit_task(index):
    try:
        logging.info(f"Received edit request for index {index}")
        task = Task.query.get(index)
        if task:
            data = request.get_json()
            logging.info(f"Received data: {data}")
            if data:
                title = data.get("title", task.title)
                duration = data.get("duration", task.duration)
                day = data.get("day")
                month = data.get("month")
                year = data.get("year")
                priority = data.get("priority", task.priority)

                logging.info(f"Extracted values: title={title}, duration={duration}, day={day}, month={month}, year={year}, priority={priority}")

                if not all([day, month, year]):
                    logging.warning("Missing required date fields")
                    return jsonify({"status": "error", "message": "Day, month, and year are required"}), 400

                try:
                    day = int(day)
                    month = int(month)
                    year = int(year)
                except ValueError as e:
                    logging.error(f"Error converting date values to integers: {str(e)}")
                    return jsonify({"status": "error", "message": "Invalid date values: day, month, and year must be integers"}), 400

                logging.info(f"Using values: day={day}, month={month}, year={year}")

                try:
                    deadline = date(year, month, day)
                except ValueError as e:
                    logging.error(f"ValueError creating date: {str(e)}")
                    return jsonify({"status": "error", "message": f"Invalid date: {str(e)}"}), 400

                old_task = task.to_dict()
                task.title = title
                task.duration = int(duration) if duration else 0
                task.deadline = deadline
                task.priority = priority

                logging.info(f"Updating task with ID {index}: {task.to_dict()}")
                db.session.commit()
                logging.info(f"Task edited with ID {index}")

                today = date.today()
                days_diff = (deadline - today).days
                logging.info(f"Days difference: {days_diff}")
                logging.info(f"Deadline: {task.deadline}")
                logging.info(f"Old Deadline: {old_task['deadline']}")
                logging.info(f"Priority: {task.priority}")
                logging.info(f"Old Priority: {old_task['priority']}")
                logging.info(f"Deadline changed: {task.deadline != old_task['deadline']}")
                logging.info(f"Priority changed: {task.priority != old_task['priority']}")

                if days_diff in [0, 1, 2]:
                    if task.deadline != datetime.strptime(old_task["deadline"], "%Y-%m-%d").date() or task.priority != old_task["priority"]:
                        logging.info("Would send update reminder")
                        # send_update_reminder(task.to_dict(), old_task, "majid_0280@yahoo.com", days_diff)

                updated_tasks = Task.query.order_by(Task.deadline, db.case(
                    (Task.priority == "Low", 3),
                    (Task.priority == "Medium", 2),
                    (Task.priority == "High", 1)
                )).all()
                updated_tasks_formatted = [{"index": task.id, "task": {**task.to_dict(), "deadline": task.deadline.strftime("%Y-%m-%d")}} for task in updated_tasks]

                task_response = task.to_dict()
                task_response["deadline"] = task.deadline.strftime("%Y-%m-%d")
                logging.info(f"Returning response: {{'status': 'success', 'task': {task_response}, 'tasks': {updated_tasks_formatted}}}")
                return jsonify({"status": "success", "task": task_response, "tasks": updated_tasks_formatted})
            else:
                logging.warning("No data provided in request")
                return jsonify({"status": "error", "message": "No data provided"}), 400
        else:
            logging.warning(f"Task not found with ID {index}")
            return jsonify({"status": "error", "message": "Task not found"}), 404
    except Exception as e:
        logging.error(f"Error in edit_task: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
