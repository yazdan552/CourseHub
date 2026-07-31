from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.course_list,
        name="course_list",
    ),

    path(
        "my-courses/",
        views.my_courses,
        name="my_courses",
    ),

    path(
        "create/",
        views.create_course,
        name="create_course",
    ),

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "<int:course_id>/enroll/",
        views.enroll_course,
        name="enroll_course",
    ),

    path(
        "<int:course_id>/unenroll/",
        views.unenroll_course,
        name="unenroll_course",
    ),

    path(
        "<int:course_id>/",
        views.course_detail,
        name="course_detail",
    ),

    path(
        "<int:course_id>/edit/",
        views.update_course,
        name="update_course",
    ),

    path(
        "<int:course_id>/delete/",
        views.delete_course,
        name="delete_course",
    ),

    # .......
    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),
    path(
        "profile/<str:username>/",  # username رو از مدل User می‌گیریم
        views.instructor_profile,
        name="instructor_profile",
    ),
    path(
        "category/<slug:slug>/",
        views.category_detail,
        name="category_detail",
    ),

]
