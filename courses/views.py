# courses/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import CourseForm, RegisterForm, InstructorProfileForm
from .models import Course, Instructor, Enrollment, Category


# ================ Mixin‌ها ================

class InstructorRequiredMixin:
    """بررسی و ایجاد خودکار Instructor"""

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'instructor'):
            Instructor.objects.create(user=request.user, phone="", bio="")
            messages.info(request, "Instructor profile created automatically.")
        return super().dispatch(request, *args, **kwargs)


class CourseOwnerRequiredMixin(UserPassesTestMixin):
    """بررسی مالکیت دوره"""

    def test_func(self):
        course = self.get_object()
        return self.request.user == course.instructor.user

    def handle_no_permission(self):
        messages.error(self.request, "You are not allowed to access this page.")
        return redirect('course_list')


class CategoryContextMixin:
    """اضافه کردن دسته‌بندی‌ها به context"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().annotate(
            course_count=Count('courses', filter=Q(courses__is_active=True))
        )
        return context


class SearchParamsMixin:
    """مدیریت پارامترهای جستجو"""

    def get_search_params(self):
        return {
            'search_query': self.request.GET.get('q', '').strip(),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'sort_by': self.request.GET.get('sort', 'newest'),
            'category_slug': self.request.GET.get('category', ''),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_search_params())
        return context


# ================ Views ================

class CourseListView(SearchParamsMixin, CategoryContextMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 6

    def get_queryset(self):
        queryset = Course.objects.select_related('instructor').annotate(
            students_count=Count('enrollments')
        ).filter(is_active=True)

        # اعمال فیلترها از SearchParamsMixin
        params = self.get_search_params()

        if params['category_slug']:
            queryset = queryset.filter(categories__slug=params['category_slug'])

        # جستجو
        if params['search_query']:
            queryset = queryset.filter(
                Q(title__icontains=params['search_query']) |
                Q(description__icontains=params['search_query']) |
                Q(instructor__user__username__icontains=params['search_query'])
            )

        # قیمت
        if params['min_price']:
            try:
                queryset = queryset.filter(price__gte=int(params['min_price']))
            except ValueError:
                pass

        if params['max_price']:
            try:
                queryset = queryset.filter(price__lte=int(params['max_price']))
            except ValueError:
                pass

        # مرتب‌سازی
        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
            'popular': '-students_count',
            'newest': '-created_at'
        }
        queryset = queryset.order_by(sort_map.get(params['sort_by'], '-created_at'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_results'] = self.get_queryset().count()
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.select_related('instructor').prefetch_related('enrollments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['is_enrolled'] = (
                self.request.user.is_authenticated and
                Enrollment.objects.filter(user=self.request.user, course=course).exists()
        )
        return context


class CourseCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        form.instance.instructor = self.request.user.instructor
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class CourseUpdateView(LoginRequiredMixin, CourseOwnerRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk})


class CourseDeleteView(LoginRequiredMixin, CourseOwnerRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')


class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = 'courses/my_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 6

    def get_queryset(self):
        return self.request.user.enrollments.select_related(
            'course__instructor'
        ).filter(is_completed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_courses'] = self.request.user.enrollments.select_related(
            'course__instructor'
        ).filter(is_completed=True)
        context['total_enrollments'] = self.get_queryset().count()
        return context


class CategoryDetailView(CategoryContextMixin, ListView):
    template_name = 'courses/category_detail.html'
    context_object_name = 'courses'
    paginate_by = 6

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['total_results'] = self.get_queryset().count()
        return context


class InstructorProfileView(DetailView):
    model = User
    template_name = 'courses/instructor_profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(
            User.objects.select_related('instructor'),
            username=self.kwargs['username']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        if not hasattr(user, 'instructor'):
            context['error'] = "This user is not an instructor."
            return context

        instructor = user.instructor
        courses_qs = instructor.courses.all().prefetch_related('enrollments')

        paginator = Paginator(courses_qs, 4)
        page_number = self.request.GET.get('page', 1)

        try:
            courses = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            courses = paginator.page(1)

        context['instructor'] = instructor
        context['courses'] = courses
        context['page_obj'] = courses
        context['total_courses'] = courses_qs.count()
        context['is_own_profile'] = (
                self.request.user.is_authenticated and self.request.user == user
        )

        return context


class EnrollCourseView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(
            Course.objects.select_related('instructor'),
            id=self.kwargs['pk']
        )

        if not course.is_active:
            messages.error(request, "This course is currently inactive.")
            return redirect("course_detail", pk=course.id)

        if request.user == course.instructor.user:
            messages.error(request, "You cannot enroll in your own course.")
            return redirect("course_detail", pk=course.id)

        if course.capacity > 0 and course.enrollments.count() >= course.capacity:
            messages.error(request, "This course is full.")
            return redirect("course_detail", pk=course.id)

        if Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.warning(request, "You are already enrolled.")
        else:
            Enrollment.objects.create(user=request.user, course=course)
            messages.success(request, f"You enrolled in {course.title}.")

        return redirect("course_detail", pk=course.id)


class UnenrollCourseView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=self.kwargs['pk'])
        Enrollment.objects.filter(user=request.user, course=course).delete()
        messages.success(request, "You have unenrolled from this course.")
        return redirect("course_detail", pk=course.id)


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        Instructor.objects.create(user=self.object, phone="", bio="")
        login(self.request, self.object)
        messages.success(self.request, "Registration completed successfully.")
        return response


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Instructor
    form_class = InstructorProfileForm
    template_name = 'courses/edit_profile.html'

    def get_object(self):
        if not hasattr(self.request.user, 'instructor'):
            return None
        return self.request.user.instructor

    def get_success_url(self):
        return reverse_lazy('instructor_profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'instructor'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('course_list')
        return super().dispatch(request, *args, **kwargs)