from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import AdvUser, Bboard, SubRubric, Comment
from .forms import ChangeUserInfoForm, RegisterUserForm, SearchForm, BboardForm, AIFormSet
from .forms import UserCommentForm, GuestCommentsForm
from .utilities import signer


def index(request):
    bboards = Bboard.objects.filter(is_active=True).select_related('author', 'rubric')
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bboards = bboards.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bboards, 20)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'bboards': page.object_list, 'form': form}
    return render(request, 'main/index.html', context)


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class BoardLoginView(LoginView):
    template_name = 'main/login.html'


class BoardLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
            return get_object_or_404(queryset, pk=self.user_id)


class BoardPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:password_change_done')
    success_message = 'Пароль пользователя изменен'


class BoardPasswordChangeDoneView(TemplateView):
    template_name = 'main/password_change_done.html'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bboards = Bboard.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bboards = bboards.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bboards, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bboards': page.object_list, 'form': form}
    return render(request, 'main/by_rubric.html', context)


def detail(request, rubric_pk, pk):
    bboard = get_object_or_404(Bboard, pk=pk)
    ais = bboard.additionalimage_set.all()
    comments = Comment.objects.filter(bboard=pk, is_active=True)
    initial = {'bboard': bboard.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentsForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')
    context = {'bboard': bboard, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/detail.html', context)


@login_required
def profile(request):
    bboards = Bboard.objects.filter(author=request.user.pk).select_related('rubric', )
    context = {'bboards': bboards}
    return render(request, 'main/profile.html', context)


@login_required
def profile_bboard_detail(request, pk):
    bboard = get_object_or_404(Bboard, pk=pk)
    ais = bboard.additionalimage_set.all()
    comments = Comment.objects.filter(bboard=pk, is_active=True)
    context = {'bboard': bboard, 'ais': ais, 'comments': comments}
    return render(request, 'main/profile_bboard_detail.html', context)


@login_required
def profile_bboard_add(request):
    if request.method == 'POST':
        form = BboardForm(request.POST, request.FILES)
        if form.is_valid():
            bboard = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bboard)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = BboardForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bboard_add.html', context)


@login_required
def profile_bboard_change(request, pk):
    bboard = get_object_or_404(Bboard, pk=pk)
    if request.method == 'POST':
        form = BboardForm(request.POST, request.FILES, instance=bboard)
        if form.is_valid():
            bboard = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bboard)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
    else:
        form = BboardForm(instance=bboard)
        formset = AIFormSet(instance=bboard)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bboard_change.html', context)


@login_required
def profile_bboard_delete(request, pk):
    bboard = get_object_or_404(Bboard, pk=pk)
    if request.method == 'POST':
        bboard.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('main:profile')
    else:
        context = {'bboard': bboard}
        return render(request, 'main/profile_bboard_delete.html', context)
