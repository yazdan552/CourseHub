from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import CourseForm, RegisterForm, InstructorProfileForm
from .models import Course, Instructor, Enrollment, Category


# Create your views here.


def course_list(request):
    """
    نمایش لیست تمام دوره‌ها
    استفاده از annotate برای بهینه‌سازی Query
    +قابلیت جستجو
    +دسته بندی
    """
    search_query = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'newest')
    category_slug = request.GET.get('category', '')

    courses = Course.objects.select_related('instructor').annotate(
        students_count=Count('enrollments')
    ).filter(is_active=True)

    if category_slug:
        courses = courses.filter(categories__slug=category_slug)

    # جست و جو
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |  # جستجو در عنوان
            Q(description__icontains=search_query) |  # جستجو در توضیحات
            Q(instructor__user__username__icontains=search_query)  # جستجو در نام مدرس
        )

    # قیمت
    if min_price:
        try:
            min_price = int(min_price)
            courses = courses.filter(price__gte=min_price)
        except ValueError:
            min_price = ''

    if max_price:
        try:
            max_price = int(max_price)
            courses = courses.filter(price__lte=max_price)
        except ValueError:
            max_price = ''

    # مرتب‌سازی
    if sort_by == 'price_asc':
        courses = courses.order_by('price')  # قیمت از کم به زیاد
    elif sort_by == 'price_desc':
        courses = courses.order_by('-price')  # قیمت از زیاد به کم
    elif sort_by == 'popular':
        courses = courses.order_by('-students_count')  # بیشترین دانشجو
    elif sort_by == 'newest':
        courses = courses.order_by('-created_at')  # جدیدترین
    else:
        courses = courses.order_by('-created_at')  # پیش‌فرض

    # دریافت همه دسته‌بندی‌ها برای نمایش در سایدبار
    categories = Category.objects.all().annotate(course_count=Count('courses', filter=Q(courses__is_active=True)))

    # ================ تعداد نتایج ================
    total_results = courses.count()

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses,
            "search_query": search_query,
            "min_price": min_price,
            "max_price": max_price,
            "sort_by": sort_by,
            "category_slug": category_slug,
            "categories": categories,
            "total_results": total_results,
        },
    )


def category_detail(request, slug):
    """
    نمایش صفحه اختصاصی یک دسته‌بندی با تمام دوره‌های آن
    """
    category = get_object_or_404(
        Category.objects.prefetch_related('courses__instructor'),
        slug=slug
    )

    courses = category.courses.filter(
        is_active=True
    ).select_related('instructor').annotate(
        students_count=Count('enrollments')
    ).order_by('-created_at')

    # دریافت همه دسته‌بندی‌ها برای سایدبار
    categories = Category.objects.all().annotate(
        course_count=Count('courses', filter=Q(courses__is_active=True))
    )

    total_results = courses.count()

    return render(
        request,
        "courses/category_detail.html",
        {
            "category": category,
            "courses": courses,
            "categories": categories,
            "total_results": total_results,
        }
    )

@login_required
def my_courses(request):
    """
    نمایش دوره‌هایی که کاربر در آنها ثبت‌نام کرده
    تفکیک دوره‌های در حال پیشرفت و تکمیل شده
    """
    # دوره‌های در حال پیشرفت
    enrollments = request.user.enrollments.select_related(
        'course__instructor'
    ).filter(
        is_completed=False
    )

    # دوره‌های تکمیل شده
    completed_courses = request.user.enrollments.select_related(
        'course__instructor'
    ).filter(
        is_completed=True
    )

    return render(
        request,
        "courses/my_courses.html",
        {
            "enrollments": enrollments,
            "completed_courses": completed_courses,
        }
    )


def course_detail(request, course_id):
    """
    نمایش جزئیات یک دوره
    بررسی اینکه کاربر قبلاً ثبت‌نام کرده یا نه
    """
    course = get_object_or_404(
        Course.objects.select_related('instructor').prefetch_related('enrollments'),
        id=course_id,
    )

    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).exists()

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
        },
    )


@login_required
def enroll_course(request, course_id):
    """
    ثبت‌نام کاربر در دوره با بررسی موارد امنیتی:
    1. دوره باید فعال باشد
    2. کاربر نباید مدرس دوره باشد
    3. ظرفیت دوره تکمیل نشده باشد
    4. کاربر قبلاً ثبت‌نام نکرده باشد
    """
    course = get_object_or_404(
        Course.objects.select_related('instructor'),
        id=course_id,
    )

    # بررسی اینکه دوره فعال باشد
    if not course.is_active:
        messages.error(
            request,
            "This course is currently inactive and cannot be enrolled."
        )
        return redirect("course_detail", course.id)

    # جلوگیری از ثبت‌نام مدرس در دوره خودش
    if request.user == course.instructor.user:
        messages.error(
            request,
            "You cannot enroll in your own course."
        )
        return redirect("course_detail", course.id)

    # بررسی ظرفیت دوره
    if course.capacity > 0:
        current_enrollments = course.enrollments.count()
        if current_enrollments >= course.capacity:
            messages.error(
                request,
                "This course is full. No more enrollments accepted."
            )
            return redirect("course_detail", course.id)

    if request.method == "POST":
        # بررسی اینکه کاربر قبلاً ثبت‌نام کرده است
        if Enrollment.objects.filter(
                user=request.user,
                course=course,
        ).exists():
            messages.warning(
                request,
                "You are already enrolled in this course."
            )
        else:
            Enrollment.objects.create(
                user=request.user,
                course=course,
            )
            messages.success(
                request,
                f"You successfully enrolled in {course.title}."
            )

        return redirect("course_detail", course.id)

    return redirect("course_detail", course.id)


@login_required
def unenroll_course(request, course_id):
    """
    لغو ثبت‌نام کاربر از دوره
    """
    course = get_object_or_404(
        Course,
        id=course_id,
    )
    if request.method == "POST":
        Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).delete()

        messages.success(
            request,
            "You have unenrolled from this course."
        )

        return redirect(
            "course_detail",
            course.id,
        )
    return redirect(
        "course_detail",
        course.id,
    )


@staff_member_required
def create_course(request):
    """
    ایجاد دوره جدید توسط مدرس
    """
    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():
            course = form.save(
                commit=False,
            )

            course.instructor = request.user.instructor

            course.save()

            form.save_m2m()

            messages.success(
                request,
                "Course created successfully.",
            )

            return redirect("course_list")

    else:
        form = CourseForm()

    return render(
        request,
        "courses/course_form.html",
        {
            "form": form,
        },
    )


@staff_member_required
def update_course(request, course_id):
    """
    ویرایش دوره (فقط مدرس دوره)
    """
    # اطمینان از وجود Instructor
    if not hasattr(request.user, 'instructor'):
        Instructor.objects.create(
            user=request.user,
            phone="",
            bio=""
        )

    course = get_object_or_404(
        Course,
        id=course_id,
    )
    if course.instructor != request.user.instructor:
        return HttpResponseForbidden(
            "You are not allowed to edit this course."
        )

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            instance=course,
        )

        if form.is_valid():
            form.save()
            form.save_m2m()

            messages.success(
                request,
                "Course updated successfully.",
            )

            return redirect(
                "course_detail",
                course.id,
            )

    else:

        form = CourseForm(
            instance=course,
        )

    return render(
        request,
        "courses/course_form.html",
        {
            "form": form,
        },
    )


@staff_member_required
def delete_course(request, course_id):
    """
    حذف دوره (فقط مدرس دوره)
    """
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if course.instructor != request.user.instructor:
        return HttpResponseForbidden(
            "You are not allowed to delete this course."
        )

    if request.method == "POST":
        course.delete()

        messages.success(
            request,
            "Course deleted successfully.",
        )

        return redirect("course_list")

    return render(
        request,
        "courses/course_confirm_delete.html",
        {
            "course": course,
        },
    )


def register(request):
    """
    ثبت‌نام کاربر جدید و ایجاد خودکار Instructor
    """
    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            Instructor.objects.create(
                user=user,
                phone="",
                bio="",
            )

            login(request, user)

            messages.success(
                request,
                "Registration completed successfully.",
            )

            return redirect("course_list")

    else:

        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
        },
    )


def instructor_profile(request, username):
    """
    نمایش پروفایل عمومی یک مدرس
    """
    # دریافت کاربر با username داده شده
    # select_related: اطلاعات instructor را همراه با user دریافت می‌کند
    user = get_object_or_404(
        User.objects.select_related('instructor'),
        username=username
    )

    # بررسی اینکه این کاربر مدرس است یا نه
    if not hasattr(user, 'instructor'):
        messages.error(
            request,
            "This user is not an instructor."
        )
        return redirect('course_list')

    # دریافت اطلاعات مدرس
    instructor = user.instructor

    # دریافت دوره‌های این مدرس به همراه تعداد دانشجویان
    # استفاده از prefetch_related برای بهینه‌سازی
    courses = instructor.courses.all().prefetch_related('enrollments')

    # بررسی اینکه کاربر جاری خودش این مدرس است یا نه
    is_own_profile = False
    if request.user.is_authenticated and request.user == user:
        is_own_profile = True

    return render(
        request,
        "courses/instructor_profile.html",
        {
            "instructor": instructor,
            "courses": courses,
            "profile_user": user,
            "is_own_profile": is_own_profile,
        }
    )


@login_required
def edit_profile(request):
    """
    ویرایش پروفایل مدرس (فقط خود مدرس)
    """
    # بررسی اینکه کاربر مدرس است
    if not hasattr(request.user, 'instructor'):
        messages.error(
            request,
            "You don't have permission to access this page."
        )
        return redirect('course_list')

    instructor = request.user.instructor

    if request.method == "POST":
        form = InstructorProfileForm(
            request.POST,
            instance=instructor
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your profile has been updated successfully."
            )
            return redirect('instructor_profile', username=request.user.username)
    else:
        form = InstructorProfileForm(instance=instructor)

    return render(
        request,
        "courses/edit_profile.html",
        {
            "form": form,
        }
    )
