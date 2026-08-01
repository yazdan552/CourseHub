# courses/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.CourseListView.as_view(), name="course_list"),
    path("my-courses/", views.MyCoursesView.as_view(), name="my_courses"),
    path("create/", views.CourseCreateView.as_view(), name="create_course"),
    path("register/", views.RegisterView.as_view(), name="register"),

    path("<int:pk>/enroll/", views.EnrollCourseView.as_view(), name="enroll_course"),
    path("<int:pk>/unenroll/", views.UnenrollCourseView.as_view(), name="unenroll_course"),

    path("<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("<int:pk>/edit/", views.CourseUpdateView.as_view(), name="update_course"),
    path("<int:pk>/delete/", views.CourseDeleteView.as_view(), name="delete_course"),

    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("profile/<str:username>/", views.InstructorProfileView.as_view(), name="instructor_profile"),
    path("profile/edit/", views.EditProfileView.as_view(), name="edit_profile"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),

]