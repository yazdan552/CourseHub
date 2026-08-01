\# 🎓 CourseHub - Online Learning Platform



CourseHub is a complete online learning platform built with Django, inspired by platforms like Udemy. It allows instructors to create courses and students to enroll and learn.



\---



\## ✨ Features



\- Authentication - Login, Logout, Register with Django's built-in User model

\- Course CRUD - Create, Read, Update, Delete courses

\- Enrollment - Enroll and unenroll with validation (capacity, active status)

\- Instructor Profile - View and edit instructor profiles

\- Advanced Search - Search by title, description, instructor with filters

\- Categories - Organize courses with categories and dedicated pages

\- Pagination - Pagination on all list pages

\- Dashboard - Instructor dashboard with statistics and charts

\- Dark Theme - Custom dark theme with smooth animations

\- Responsive - Works on mobile, tablet, and desktop

\- SEO Ready - Meta tags, Open Graph, Twitter Cards



\---



\## 🛠️ Technologies



\- Django 4.2 - Backend Framework

\- SQLite - Database

\- Bootstrap 5 - UI Framework

\- Chart.js - Charts in Dashboard

\- Inter Font - Modern typography

\- CSS Variables - Dark theme management



\---



\## 📦 Installation



\### 1. Clone the repository



git clone https://github.com/yazdan552/CourseHub.git

cd CourseHub



\### 2. Create virtual environment



python -m venv .venv

source .venv/bin/activate



On Windows:

.venv\\Scripts\\activate



\### 3. Install dependencies



pip install -r requirements.txt



\### 4. Environment variables



Create a .env file in the root directory:



SECRET\_KEY=your-secret-key-here

DEBUG=True



\### 5. Apply migrations



python manage.py makemigrations

python manage.py migrate



\### 6. Create superuser



python manage.py createsuperuser



\### 7. Run the server



python manage.py runserver



Visit http://127.0.0.1:8000 to see the application.



\---



\## 🗂️ Project Structure



CourseHub/

├── CourseHub/                 # Project settings

├── courses/                   # Main app

│   ├── admin.py              # Admin configuration

│   ├── models.py             # 4 models

│   ├── views.py              # 13 Class-Based Views

│   ├── urls.py               # 11 URLs

│   └── forms.py              # 3 forms

├── templates/                 # 11 HTML templates

├── static/                    # CSS, JS files

└── media/                     # User uploaded files



\---



\## 🚀 Usage



For Students:

1\. Register an account

2\. Browse and search courses

3\. Enroll in courses

4\. View My Courses

5\. Track your progress



For Instructors:

1\. Register (Instructor created automatically)

2\. Create, edit, and delete courses

3\. View Dashboard with statistics and charts



For Admin:

1\. Login as superuser

2\. Access Django admin panel

3\. Manage all data



\---



\## 🤝 Contributing



1\. Fork the repository

2\. Create a feature branch: git checkout -b feature/your-feature

3\. Commit changes: git commit -m "Add your feature"

4\. Push: git push origin feature/your-feature

5\. Create a Pull Request



\---



\## 📄 License



This project is licensed under the MIT License - see the LICENSE file for details.



\---



\## 📞 Contact



\- Author: Yazdan

\- GitHub: yazdan552



\---



\## ⭐ Support



If you find this project helpful, please give it a star on GitHub!

