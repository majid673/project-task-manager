# Project Task Manager

Welcome to Project Task Manager! This is a web application built with Flask to help users organize and track their daily tasks efficiently. The application allows users to add, edit, and delete tasks, and sends email reminders for upcoming deadlines.

## Features

- **Task Management**: Add, edit, and delete tasks with details like title, duration, deadline, and priority.
- **Email Reminders**: Sends email notifications for new and updated tasks with reminders for today, tomorrow, and 2 days before the deadline.
- **Priority Sorting**: Automatically sorts tasks by deadline and priority (Low, Medium, High).
- **Responsive Design**: Works on both desktop and mobile devices.
- **JSON Storage**: Stores tasks in a `tasks.json` file for simplicity.

## Demo

You can view the live demo of the project here:  
[https://project-task-manager-6dvb.onrender.com](https://project-task-manager-6dvb.onrender.com)

## Project Structure

The project is structured as follows:

- `app.py`: The main Flask application file.
- `tasks.json`: Stores tasks in JSON format.
- `static/style.css`: Contains the CSS styles for the application.
- `templates/`: Contains HTML templates for rendering pages (`index.html`, `login.html`).

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **Storage**: JSON (`tasks.json`)
- **Email Notifications**: Uses Gmail SMTP for sending reminders

## How to Run Locally

To run the project locally on your machine, follow these steps:

1. **Clone the repository**:  git clone https://github.com/majid673/project-task-manager.git
                      
2. **Navigate to the project folder**: cd project-task-manager
   
3. **Create a virtual environment** (optional but recommended):
                  -python -m venv venv
                  -Activate the virtual environment:    - On Windows:    venv\Scripts\activate    - On Mac/Linux:  source venv/bin/activate 
                                                                                   
4. **Install dependencies**:  pip install -r requirements.txt
 
5. **Set up environment variables (optional)**: If you want to use email reminders, set up your Gmail App Password and update the `email_from` and `password` in 
                                                 `app.py`.
6. **Run the application**:  flask run
                             The application will be available at `http://127.0.0.1:5000`.
## Deployment on Render

This project is deployed on Render. To deploy your own instance:

1. **Create a Render account**: Sign up at [Render](https://render.com/).
2. **Create a new Web Service**: Connect your GitHub repository (`majid673/project-task-manager`).
3. **Configure the service**:
                 - **Build Command**: `pip install -r requirements.txt`
                 - **Start Command**: `gunicorn app:app`
4. **Deploy**: Click "Create Web Service" and wait for the deployment to complete.
5. **Note**: Email reminders are disabled in the current deployment due to Render's network restrictions. You can enable them locally or use a service like 
             SendGrid.

## Contact

Feel free to reach out to me if you have any questions or want to collaborate:

- **Email**: [arashar905@gmail.com](mailto:arashar905@gmail.com)
- **GitHub**: [majid673](https://github.com/majid673)

---

Thank you for checking out my project!  
