from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import CourseForm, RegisterForm, InstructorProfileForm
from .models import Course, Instructor, Enrollment, Category


# Create your views here.

class CourseListView(ListView):
    """
    نمایش لیست دوره‌ها با قابلیت جستجو، فیلتر و صفحه‌بندی
    """
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 6

    def get_queryset(self):
        """
        سفارشی‌سازی کوئری با فیلترها و جستجو
        """
        queryset = Course.objects.select_related('instructor').annotate(
            students_count=Count('enrollments')
        ).filter(is_active=True)

        search_query = self.request.GET.get('q', '').strip()
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        sort_by = self.request.GET.get('sort', 'newest')
        category_slug = self.request.GET.get('category', '')

        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)

        # جستجو
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(instructor__user__username__icontains=search_query)
            )

        # فیلتر قیمت
        if min_price:
            try:
                min_price = int(min_price)
                queryset = queryset.filter(price__gte=min_price)
            except ValueError:
                pass

        if max_price:
            try:
                max_price = int(max_price)
                queryset = queryset.filter(price__lte=max_price)
            except ValueError:
                pass

        # مرتب‌سازی
        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
            'popular': '-students_count',
            'newest': '-created_at'
        }
        queryset = queryset.order_by(sort_map.get(sort_by, '-created_at'))

        return queryset

    def get_context_data(self, **kwargs):
        """
        اضافه کردن داده‌های اضافی به context
        """
        context = super().get_context_data(**kwargs)

        context['search_query'] = self.request.GET.get('q', '').strip()
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort_by'] = self.request.GET.get('sort', 'newest')
        context['category_slug'] = self.request.GET.get('category', '')

        # دریافت دسته‌بندی‌ها برای سایدبار
        context['categories'] = Category.objects.all().annotate(
            course_count=Count('courses', filter=Q(courses__is_active=True))
        )

        context['total_results'] = self.get_queryset().count()

        return context


# def course_list(request):
#     """
#     نمایش لیست تمام دوره‌ها
#     """
#     search_query = request.GET.get('q', '').strip()
#     min_price = request.GET.get('min_price', '')
#     max_price = request.GET.get('max_price', '')
#     sort_by = request.GET.get('sort', 'newest')
#     category_slug = request.GET.get('category', '')
#     page_number = request.GET.get('page', 1)
#
#     courses = Course.objects.select_related('instructor').annotate(
#         students_count=Count('enrollments')
#     ).filter(is_active=True)
#
#     if category_slug:
#         courses = courses.filter(categories__slug=category_slug)
#
#     # جست و جو
#     if search_query:
#         courses = courses.filter(
#             Q(title__icontains=search_query) |  # جستجو در عنوان
#             Q(description__icontains=search_query) |  # جستجو در توضیحات
#             Q(instructor__user__username__icontains=search_query)  # جستجو در نام مدرس
#         )
#
#     # قیمت
#     if min_price:
#         try:
#             min_price = int(min_price)
#             courses = courses.filter(price__gte=min_price)
#         except ValueError:
#             min_price = ''
#
#     if max_price:
#         try:
#             max_price = int(max_price)
#             courses = courses.filter(price__lte=max_price)
#         except ValueError:
#             max_price = ''
#
#     # مرتب‌سازی
#     if sort_by == 'price_asc':
#         courses = courses.order_by('price')  # قیمت از کم به زیاد
#     elif sort_by == 'price_desc':
#         courses = courses.order_by('-price')  # قیمت از زیاد به کم
#     elif sort_by == 'popular':
#         courses = courses.order_by('-students_count')  # بیشترین دانشجو
#     elif sort_by == 'newest':
#         courses = courses.order_by('-created_at')  # جدیدترین
#     else:
#         courses = courses.order_by('-created_at')  # پیش‌فرض
#
#     # دریافت همه دسته‌بندی‌ها برای نمایش در سایدبار
#     categories = Category.objects.all().annotate(course_count=Count('courses', filter=Q(courses__is_active=True)))
#
#     #Paginator
#     paginator = Paginator(courses, 6)
#
#     try:
#         page_obj = paginator.page(page_number)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#
#
#
#     # ================ تعداد نتایج ================
#     total_results = courses.count()
#
#     return render(
#         request,
#         "courses/course_list.html",
#         {
#             "courses": page_obj,
#             "page_obj": page_obj,
#             "search_query": search_query,
#             "min_price": min_price,
#             "max_price": max_price,
#             "sort_by": sort_by,
#             "category_slug": category_slug,
#             "categories": categories,
#             "total_results": total_results,
#         },
#     )


class CategoryDetailView(ListView):
    """
    نمایش صفحه اختصاصی یک دسته‌بندی با تمام دوره‌های آن
    """
    template_name = 'courses/category_detail.html'
    context_object_name = 'courses'
    paginate_by = 6

    def get_queryset(self):
        """
        دریافت دوره‌های یک دسته‌بندی خاص
        """
        self.category = get_object_or_404(
            Category.objects.prefetch_related('courses__instructor'),
            slug=self.kwargs['slug']
        )

        return self.category.courses.filter(
            is_active=True
        ).select_related('instructor').annotate(
            students_count=Count('enrollments')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        اضافه کردن اطلاعات دسته‌بندی و لیست همه دسته‌بندی‌ها
        """
        context = super().get_context_data(**kwargs)

        # اطلاعات دسته‌بندی فعلی
        context['category'] = self.category

        # همه دسته‌بندی‌ها برای سایدبار
        context['categories'] = Category.objects.all().annotate(
            course_count=Count('courses', filter=Q(courses__is_active=True))
        )

        # تعداد کل دوره‌های این دسته‌بندی
        context['total_results'] = self.get_queryset().count()

        return context


# def category_detail(request, slug):
#     """
#     نمایش صفحه اختصاصی یک دسته‌بندی با تمام دوره‌های آن
#     """
#     page_number = request.GET.get('page', 1)
#
#     category = get_object_or_404(
#         Category.objects.prefetch_related('courses__instructor'),
#         slug=slug
#     )
#
#     courses = category.courses.filter(
#         is_active=True
#     ).select_related('instructor').annotate(
#         students_count=Count('enrollments')
#     ).order_by('-created_at')
#
#     # دریافت همه دسته‌بندی‌ها برای سایدبار
#     categories = Category.objects.all().annotate(
#         course_count=Count('courses', filter=Q(courses__is_active=True))
#     )
#
#     total_results = courses.count()
#
#     # paginator
#     paginator = Paginator(courses, 6)
#
#     try:
#         page_obj = paginator.page(page_number)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#
#     return render(
#         request,
#         "courses/category_detail.html",
#         {
#             "category": category,
#             "courses": page_obj,
#             "page_obj": page_obj,
#             "categories": categories,
#             "total_results": total_results,
#         }
#     )


class MyCoursesView(LoginRequiredMixin, ListView):
    """
    نمایش دوره‌هایی که کاربر در آنها ثبت‌نام کرده
    تفکیک دوره‌های در حال پیشرفت و تکمیل شده
    """
    template_name = 'courses/my_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 6

    def get_queryset(self):
        """
        دریافت دوره‌های در حال پیشرفت کاربر
        """
        return self.request.user.enrollments.select_related(
            'course__instructor'
        ).filter(is_completed=False)

    def get_context_data(self, **kwargs):
        """
        اضافه کردن دوره‌های تکمیل شده و تعداد کل
        """
        context = super().get_context_data(**kwargs)

        # دوره‌های تکمیل شده (بدون صفحه‌بندی)
        context['completed_courses'] = self.request.user.enrollments.select_related(
            'course__instructor'
        ).filter(is_completed=True)

        # تعداد کل دوره‌های در حال پیشرفت
        context['total_enrollments'] = self.get_queryset().count()

        return context

# @login_required
# def my_courses(request):
#     """
#     نمایش دوره‌هایی که کاربر در آنها ثبت‌نام کرده
#     تفکیک دوره‌های در حال پیشرفت و تکمیل شده
#     """
#     page_number = request.GET.get('page', 1)
#
#     # دوره‌های در حال پیشرفت
#     enrollments = request.user.enrollments.select_related(
#         'course__instructor'
#     ).filter(
#         is_completed=False
#     )
#
#     # دوره‌های تکمیل شده
#     completed_courses = request.user.enrollments.select_related(
#         'course__instructor'
#     ).filter(
#         is_completed=True
#     )
#
#     total_enrollments = enrollments.count()
#
#     paginator = Paginator(enrollments, 6)
#
#     try:
#         page_obj = paginator.page(page_number)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#
#     return render(
#         request,
#         "courses/my_courses.html",
#         {
#             "enrollments": page_obj,
#             "page_obj": page_obj,
#             "completed_courses": completed_courses,
#             "total_enrollments": total_enrollments,
#         }
#     )


class CourseDetailView(DetailView):
    """
    نمایش جزئیات یک دوره
    """
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        """
        بهینه‌سازی کوئری با select_related و prefetch_related
        """
        return Course.objects.select_related('instructor').prefetch_related('enrollments')

    def get_context_data(self, **kwargs):
        """
        اضافه کردن اطلاعات ثبت‌نام کاربر
        """
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                user=self.request.user,
                course=course
            ).exists()
        else:
            context['is_enrolled'] = False

        return context


# def course_detail(request, course_id):
#     """
#     نمایش جزئیات یک دوره
#     بررسی اینکه کاربر قبلاً ثبت‌نام کرده یا نه
#     """
#     course = get_object_or_404(
#         Course.objects.select_related('instructor').prefetch_related('enrollments'),
#         id=course_id,
#     )
#
#     is_enrolled = False
#
#     if request.user.is_authenticated:
#         is_enrolled = Enrollment.objects.filter(
#             user=request.user,
#             course=course,
#         ).exists()
#
#     return render(
#         request,
#         "courses/course_detail.html",
#         {
#             "course": course,
#             "is_enrolled": is_enrolled,
#         },
#     )


class EnrollCourseView(LoginRequiredMixin, View):
    """
    ثبت‌نام کاربر در دوره
    """

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs['pk']
        course = get_object_or_404(
            Course.objects.select_related('instructor'),
            id=course_id
        )

        if not course.is_active:
            messages.error(
                request,
                "This course is currently inactive and cannot be enrolled."
            )
            return redirect("course_detail", pk=course.id)

        if request.user == course.instructor.user:
            messages.error(
                request,
                "You cannot enroll in your own course."
            )
            return redirect("course_detail", pk=course.id)

        if course.capacity > 0:
            current_enrollments = course.enrollments.count()
            if current_enrollments >= course.capacity:
                messages.error(
                    request,
                    "This course is full. No more enrollments accepted."
                )
                return redirect("course_detail", pk=course.id)

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

        return redirect("course_detail", pk=course.id)


# @login_required
# def enroll_course(request, course_id):
#     """
#     ثبت‌نام کاربر در دوره با بررسی موارد امنیتی:
#     1. دوره باید فعال باشد
#     2. کاربر نباید مدرس دوره باشد
#     3. ظرفیت دوره تکمیل نشده باشد
#     4. کاربر قبلاً ثبت‌نام نکرده باشد
#     """
#     course = get_object_or_404(
#         Course.objects.select_related('instructor'),
#         id=course_id,
#     )
#
#     # بررسی اینکه دوره فعال باشد
#     if not course.is_active:
#         messages.error(
#             request,
#             "This course is currently inactive and cannot be enrolled."
#         )
#         return redirect("course_detail", course.id)
#
#     # جلوگیری از ثبت‌نام مدرس در دوره خودش
#     if request.user == course.instructor.user:
#         messages.error(
#             request,
#             "You cannot enroll in your own course."
#         )
#         return redirect("course_detail", course.id)
#
#     # بررسی ظرفیت دوره
#     if course.capacity > 0:
#         current_enrollments = course.enrollments.count()
#         if current_enrollments >= course.capacity:
#             messages.error(
#                 request,
#                 "This course is full. No more enrollments accepted."
#             )
#             return redirect("course_detail", course.id)
#
#     if request.method == "POST":
#         # بررسی اینکه کاربر قبلاً ثبت‌نام کرده است
#         if Enrollment.objects.filter(
#                 user=request.user,
#                 course=course,
#         ).exists():
#             messages.warning(
#                 request,
#                 "You are already enrolled in this course."
#             )
#         else:
#             Enrollment.objects.create(
#                 user=request.user,
#                 course=course,
#             )
#             messages.success(
#                 request,
#                 f"You successfully enrolled in {course.title}."
#             )
#
#         return redirect("course_detail", course.id)
#
#     return redirect("course_detail", course.id)


class UnenrollCourseView(LoginRequiredMixin, View):
    """
    لغو ثبت‌نام کاربر از دوره
    """

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs['pk']
        course = get_object_or_404(Course, id=course_id)

        Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).delete()

        messages.success(
            request,
            "You have unenrolled from this course."
        )

        return redirect("course_detail", pk=course.id)




# @login_required
# def unenroll_course(request, course_id):
#     """
#     لغو ثبت‌نام کاربر از دوره
#     """
#     course = get_object_or_404(
#         Course,
#         id=course_id,
#     )
#     if request.method == "POST":
#         Enrollment.objects.filter(
#             user=request.user,
#             course=course,
#         ).delete()
#
#         messages.success(
#             request,
#             "You have unenrolled from this course."
#         )
#
#         return redirect(
#             "course_detail",
#             course.id,
#         )
#     return redirect(
#         "course_detail",
#         course.id,
#     )


class CourseCreateView(LoginRequiredMixin, CreateView):
    """
    ایجاد دوره جدید
    """
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        """
        تنظیم instructor قبل از ذخیره
        """
        # بررسی وجود Instructor
        if not hasattr(self.request.user, 'instructor'):
            Instructor.objects.create(
                user=self.request.user,
                phone="",
                bio=""
            )

        form.instance.instructor = self.request.user.instructor
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        اضافه کردن عنوان مناسب
        """
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


# @staff_member_required
# def create_course(request):
#     """
#     ایجاد دوره جدید توسط مدرس
#     """
#     if request.method == "POST":
#
#         form = CourseForm(request.POST)
#
#         if form.is_valid():
#             course = form.save(
#                 commit=False,
#             )
#
#             course.instructor = request.user.instructor
#
#             course.save()
#
#             form.save_m2m()
#
#             messages.success(
#                 request,
#                 "Course created successfully.",
#             )
#
#             return redirect("course_list")
#
#     else:
#         form = CourseForm()
#
#     return render(
#         request,
#         "courses/course_form.html",
#         {
#             "form": form,
#         },
#     )


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    ویرایش دوره (فقط مدرس دوره)
    """
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        """
        بررسی اینکه کاربر مدرس این دوره است
        """
        course = self.get_object()
        return self.request.user == course.instructor.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def get_success_url(self):
        """
        بعد از ویرایش به صفحه جزئیات دوره برویم
        """
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk})



# @staff_member_required
# def update_course(request, course_id):
#     """
#     ویرایش دوره (فقط مدرس دوره)
#     """
#     # اطمینان از وجود Instructor
#     if not hasattr(request.user, 'instructor'):
#         Instructor.objects.create(
#             user=request.user,
#             phone="",
#             bio=""
#         )
#
#     course = get_object_or_404(
#         Course,
#         id=course_id,
#     )
#     if course.instructor != request.user.instructor:
#         return HttpResponseForbidden(
#             "You are not allowed to edit this course."
#         )
#
#     if request.method == "POST":
#
#         form = CourseForm(
#             request.POST,
#             instance=course,
#         )
#
#         if form.is_valid():
#             form.save()
#             form.save_m2m()
#
#             messages.success(
#                 request,
#                 "Course updated successfully.",
#             )
#
#             return redirect(
#                 "course_detail",
#                 course.id,
#             )
#
#     else:
#
#         form = CourseForm(
#             instance=course,
#         )
#
#     return render(
#         request,
#         "courses/course_form.html",
#         {
#             "form": form,
#         },
#     )


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    حذف دوره (فقط مدرس دوره)
    """
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        """
        بررسی اینکه کاربر مدرس این دوره است
        """
        course = self.get_object()
        return self.request.user == course.instructor.user



# @staff_member_required
# def delete_course(request, course_id):
#     """
#     حذف دوره (فقط مدرس دوره)
#     """
#     course = get_object_or_404(
#         Course,
#         id=course_id,
#     )
#
#     if course.instructor != request.user.instructor:
#         return HttpResponseForbidden(
#             "You are not allowed to delete this course."
#         )
#
#     if request.method == "POST":
#         course.delete()
#
#         messages.success(
#             request,
#             "Course deleted successfully.",
#         )
#
#         return redirect("course_list")
#
#     return render(
#         request,
#         "courses/course_confirm_delete.html",
#         {
#             "course": course,
#         },
#     )


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


class InstructorProfileView(DetailView):
    """
    نمایش پروفایل عمومی یک مدرس
    """
    model = User
    template_name = 'courses/instructor_profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        """
        دریافت کاربر با username
        """
        return get_object_or_404(
            User.objects.select_related('instructor'),
            username=self.kwargs['username']
        )

    def get_context_data(self, **kwargs):
        """
        اضافه کردن اطلاعات مدرس و دوره‌های او
        """
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # بررسی اینکه کاربر مدرس است
        if not hasattr(user, 'instructor'):
            messages.error(self.request, "This user is not an instructor.")
            # نمی‌توانیم redirect کنیم، پس context خاص می‌دهیم
            context['error'] = "This user is not an instructor."
            return context

        instructor = user.instructor

        # دریافت دوره‌های مدرس با صفحه‌بندی
        courses_qs = instructor.courses.all().prefetch_related('enrollments')

        # صفحه‌بندی دستی (چون DetailView صفحه‌بندی ندارد)
        paginator = Paginator(courses_qs, 4)
        page_number = self.request.GET.get('page', 1)

        try:
            courses = paginator.page(page_number)
        except PageNotAnInteger:
            courses = paginator.page(1)
        except EmptyPage:
            courses = paginator.page(paginator.num_pages)

        context['instructor'] = instructor
        context['courses'] = courses
        context['page_obj'] = courses
        context['total_courses'] = courses_qs.count()

        # بررسی اینکه کاربر جاری خودش است
        context['is_own_profile'] = (
                self.request.user.is_authenticated and
                self.request.user == user
        )

        return context

# def instructor_profile(request, username):
#     """
#     نمایش پروفایل عمومی یک مدرس
#     """
#     page_number = request.GET.get('page', 1)
#
#     user = get_object_or_404(
#         User.objects.select_related('instructor'),
#         username=username
#     )
#
#     # بررسی اینکه این کاربر مدرس است یا نه
#     if not hasattr(user, 'instructor'):
#         messages.error(
#             request,
#             "This user is not an instructor."
#         )
#         return redirect('course_list')
#
#     # دریافت اطلاعات مدرس
#     instructor = user.instructor
#
#     # دریافت دوره‌های این مدرس به همراه تعداد دانشجویان
#     # استفاده از prefetch_related برای بهینه‌سازی
#     courses = instructor.courses.all().prefetch_related('enrollments')
#
#     total_courses = courses.count()
#
#     paginator = Paginator(courses, 4)
#
#     try:
#         courses = paginator.page(page_number)
#     except PageNotAnInteger:
#         courses = paginator.page(1)
#     except EmptyPage:
#         courses = paginator.page(paginator.num_pages)
#
#     # بررسی اینکه کاربر جاری خودش این مدرس است یا نه
#     is_own_profile = False
#     if request.user.is_authenticated and request.user == user:
#         is_own_profile = True
#
#     return render(
#         request,
#         "courses/instructor_profile.html",
#         {
#             "instructor": instructor,
#             "courses": courses,
#             "page_obj": courses,
#             "profile_user": user,
#             "is_own_profile": is_own_profile,
#             "total_courses": total_courses,
#         }
#     )


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
