from django.shortcuts import render


# Create your views here.

def home(request):
    context = {
        "title": "CourseHub",
        "teacher": "Yazdan",
        "course_count": 5,
        "status": "در حال توسعه",
    }
    return render(request, 'core/home.html',context)
