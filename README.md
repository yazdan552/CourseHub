\# 🎓 CourseHub



A modern online learning platform built with \*\*Django\*\*, inspired by platforms like Udemy. CourseHub enables instructors to create and manage courses while allowing students to discover, enroll, and learn through an intuitive interface.



\---



\## ✨ Features



\### 👤 Authentication

\- User registration and login

\- Secure logout

\- Django Authentication System

\- User profile management



\### 📚 Course Management

\- Create, update, delete, and view courses

\- Course detail pages

\- Category organization

\- Instructor ownership validation



\### 🎓 Student Features

\- Enroll in courses

\- Unenroll from courses

\- Capacity validation

\- Personal \*\*My Courses\*\* page



\### 👨‍🏫 Instructor Dashboard

\- Manage created courses

\- View statistics

\- Dashboard charts using Chart.js



\### 🔍 Search \& Navigation

\- Search by title

\- Search by description

\- Search by instructor

\- Category filtering

\- Pagination



\### 🎨 User Experience

\- Responsive design

\- Dark theme

\- Smooth animations

\- SEO-friendly pages

\- Open Graph \& Twitter Cards



\---



\## 🛠 Tech Stack



| Technology | Purpose |

|------------|---------|

| Django 4.2 | Backend Framework |

| SQLite | Database |

| Bootstrap 5 | Frontend UI |

| Chart.js | Dashboard Charts |

| HTML5 / CSS3 | Frontend |

| Django Templates | Server-side Rendering |



\---



\## 📂 Project Structure



```text

CourseHub/

│

├── CourseHub/          # Project configuration

├── courses/            # Main application

│   ├── models.py

│   ├── views.py

│   ├── urls.py

│   ├── forms.py

│   └── admin.py

│

├── templates/

├── static/

├── media/

├── requirements.txt

└── manage.py

```



\---



\## 🚀 Getting Started



\### 1. Clone the repository



```bash

git clone https://github.com/yazdan552/CourseHub.git

cd CourseHub

```



\### 2. Create a virtual environment



\*\*Linux / macOS\*\*



```bash

python -m venv .venv

source .venv/bin/activate

```



\*\*Windows\*\*



```powershell

python -m venv .venv

.venv\\Scripts\\activate

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Create a `.env` file



```env

SECRET\_KEY=your-secret-key

DEBUG=True

```



\### 5. Apply migrations



```bash

python manage.py migrate

```



\### 6. Create a superuser



```bash

python manage.py createsuperuser

```



\### 7. Run the development server



```bash

python manage.py runserver

```



Open your browser and visit:



```

http://127.0.0.1:8000

```



\---



\## 👥 User Roles



\### Student

\- Register an account

\- Browse available courses

\- Search courses

\- Enroll and unenroll

\- View enrolled courses



\### Instructor

\- Create courses

\- Edit existing courses

\- Delete courses

\- Monitor statistics through the dashboard



\### Administrator

\- Access Django Admin

\- Manage users

\- Manage courses

\- Manage categories



\---



\## 📌 Future Improvements



\- Course lessons

\- Video streaming

\- Quiz system

\- Certificates

\- Payment integration

\- Course ratings and reviews

\- Wishlist

\- Email notifications

\- REST API

\- Docker support



\---



\## 🤝 Contributing



Contributions are welcome.



1\. Fork the repository.

2\. Create a feature branch.



```bash

git checkout -b feature/your-feature

```



3\. Commit your changes.



```bash

git commit -m "Add your feature"

```



4\. Push your branch.



```bash

git push origin feature/your-feature

```



5\. Open a Pull Request.



\---



\## 📄 License



This project is licensed under the \*\*MIT License\*\*.



\---



\## 👨‍💻 Author



\*\*Yazdan\*\*



GitHub: \*\*@yazdan552\*\*



\---



\## ⭐ Support



If you find this project useful, consider giving it a ⭐ on GitHub.

