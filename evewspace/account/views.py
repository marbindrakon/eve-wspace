#   Eve W-Space
#   Copyright 2014 Andrew Austin and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from account.models import RegistrationForm
from account.utils import *
from account.forms import EditProfileForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.forms.utils import ErrorList
import pytz
import datetime
import time
# Create your views here.

User = get_user_model()

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid() == True:
            # Enforce ACCOUNT_REQUIRE_REG_CODE
            if settings.ACCOUNT_REQUIRE_REG_CODE:
                if len(get_groups_for_code(form.cleaned_data['regcode'])) != 0:
                    newUser = form.save()
                    newUser.email = form.cleaned_data['email']
                    newUser.save()
                    register_groups(newUser, form.cleaned_data['regcode'])
                    return HttpResponseRedirect(reverse('login'))
                else:
                    form._errors['regcode'] = ErrorList(['Invalid Registration Code.'])
            else:
                newUser = form.save()
                newUser.email = form.cleaned_data['email']
                newUser.save()
                register_groups(newUser, form.cleaned_data['regcode'])
                return HttpResponseRedirect(reverse('login'))

    else:
        form = RegistrationForm()

    context = {'form': form}
    return TemplateResponse(request, "register.html", context)


def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['password']):
                form._errors['password'] = ErrorList(['The password you entered is incorrect.'])
            else:
                request.user.email = form.cleaned_data['email']
                if form.cleaned_data['password1']:
                    request.user.set_password(form.cleaned_data['password1'])
                request.user.save()
                return HttpResponseRedirect('/settings/')
    else:
        form = EditProfileForm()
        form.fields['email'].initial = request.user.email
    return TemplateResponse(request, "edit_profile_form.html",
            {'form': form})


def password_reset_confirm(*args, **kwargs):
    from django.contrib.auth import views
    return views.password_reset_confirm(*args, post_reset_redirect=reverse('login'),
            template_name='password_reset_confirm.html',
            **kwargs)


@permission_required('account.account_admin')
def user_admin(request):
    return HttpResponse()


@permission_required('account.account_admin')
def user_list(request, page_number):
    if request.method == "POST":
        filter_text = request.POST.get('filter', "")
        user_list = User.objects.filter(username__icontains=filter_text)
        is_filtered = True
    else:
        user_list = User.objects.all()
        is_filtered = False
    paginator = Paginator(user_list, 15)
    try:
        page_list = paginator.page(page_number)
    except PageNotAnInteger:
        page_list = paginator.page(1)
    except EmptyPage:
        page_list = paginator.page(paginator.num_pages)
    return TemplateResponse(request, "user_list.html",
            {'member_list': page_list, 'filter': is_filtered})


@permission_required('account.account_admin')
def group_list(request, page_number):
    if request.method == "POST":
        show_system = request.POST.get('system_groups', None)
        filter_text = request.POST.get('filter', "")
        if not show_system:
            group_list = Group.objects.filter(name__icontains=filter_text, profile__visible=True)
        else:
            group_list = Group.objects.filter(name__icontains=filter_text)
        is_filtered = True
    else:
        group_list = Group.objects.filter(profile__visible=True)
        is_filtered = False
    paginator = Paginator(group_list, 15)
    try:
        page_list = paginator.page(page_number)
    except PageNotAnInteger:
        page_list = paginator.page(1)
    except EmptyPage:
        page_list = paginator.page(paginator.num_pages)
    return TemplateResponse(request, "group_list.html",
            {'group_list': page_list, 'filter': is_filtered})


@permission_required('account.account_admin')
def group_admin(request):
    return HttpResponse()


@permission_required('account.account_admin')
def new_user(request):
    if request.method == 'POST':
        error_list = []
        username = request.POST.get('username', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        email = request.POST.get('email', None)
        if not username:
            error_list.append('Username cannot be blank!')
        if password1 != password2:
            error_list.append('Passwords do not match!')
        if not password1:
            error_list.append('Password cannot be blank!')
        if error_list:
            return HttpResponse(render_to_string('create_user_error.html',
                {'errors': error_list}), status=400)
        user = User(username=username, email=email)
        user.save()
        user.set_password(password1)
        user.is_active = True
        user.save()
        if request.POST.get('email_password', None):
            send_pass = True
        else:
            send_pass = False
        if user.email and send_pass:
            message = EmailMessage(
                    subject="Password Reset",
                    body=render_to_string(
                        'password_admin_reset_email.txt',
                        {'admin': request.user, 'member': user,
                            'password': password1,
                            'notify': True}),
                    to=[user.email,])
            message.send(fail_silently=False)
        return HttpResponse()

    return TemplateResponse(request, 'create_user.html')

@permission_required('account.account_admin')
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return TemplateResponse(request, 'user_edit_dialog.html',
            {'member': user, 'group_list': Group.objects.all()})


@permission_required('account.account_admin')
def group_edit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return TemplateResponse(request, 'group_edit_dialog.html',
            {'group': group, 'member_list': group.user_set.all()})


@permission_required('account.account_admin')
def user_group_list(request, user_id):
    if not request.is_ajax():
        raise PermissionDenied
    user = get_object_or_404(User, pk=user_id)
    saved = False
    if request.method == "POST":
        saved = True
        visible_groups = Group.objects.filter(profile__visible=True).all()
        for group in visible_groups:
            if request.POST.get('group_%s' % group.pk, None):
                if group not in user.groups.all():
                    user.groups.add(group)
            elif group in user.groups.all():
                user.groups.remove(group)
        user.save()

    return TemplateResponse(request, 'user_admin_groups.html',
            {'member': user, 'group_list': Group.objects.all(),
                'saved': saved})


@permission_required('account.account_admin')
def profile_admin(request, user_id):
    if not request.is_ajax():
        raise PermissionDenied
    user = get_object_or_404(User, pk=user_id)
    error_list = []
    if request.method == "POST":
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.is_active = request.POST.get('enabled', False)
        password = request.POST.get('new_password', None)
        password_confirm = request.POST.get('confirm_password', None)
        if password and password == password_confirm:
            user.set_password(password)
            if request.POST.get('email_password', None):
                send_pass = True
            else:
                send_pass = False
            if user.email and send_pass:
                message = EmailMessage(
                        subject="Password Reset",
                        body=render_to_string(
                            'password_admin_reset_email.txt',
                            {'admin': request.user, 'member': user,
                                'password': password,
                                'notify': send_pass}),
                        to=[user.email,])
                message.send(fail_silently=False)
        elif password or password_confirm:
            error_list.append("Passwords do not match. Non-Password changes saved.")
        user.save()
        saved = True
    else:
        saved = False
    return TemplateResponse(request, 'user_admin_profile.html',
            {'member': user, 'saved': saved, 'errors': error_list})


@permission_required('account.account_admin')
def group_profile_admin(request, group_id):
    if not request.is_ajax():
        raise PermissionDenied
    group = get_object_or_404(Group, pk=group_id)
    error_list = []
    saved = False
    if request.method == "POST":
        group.name = request.POST.get('group_name', group.name)
        new_regcode = request.POST.get('new_regcode', group.profile.regcode)
        group.profile.regcode = new_regcode
        if group.name:
            group.profile.save()
            group.save()
            saved = True
        else:
            error_list.append('Group name cannot be blank!')
    return TemplateResponse(request, 'group_admin_profile.html',
            {'group': group, 'saved': saved, 'errors': error_list})


@permission_required('account.account_admin')
def delete_user(request, user_id):
    if not request.is_ajax():
        raise PermissionDenied
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.delete()
        return HttpResponse()
    else:
        return HttResponse(status=400)

@permission_required('account.account_admin')
def delete_group(request, group_id):
    if not request.is_ajax():
        raise PermissionDenied
    group = get_object_or_404(Group, pk=group_id)
    if request.method == "POST":
        group.delete()
        return HttpResponse()
    else:
        return HttpResponse(status=400)


@permission_required('account.account_admin')
def disable_group_users(request, group_id):
    if not request.is_ajax():
        raise PermissionDenied
    group = get_object_or_404(Group, pk=group_id)
    if request.method == "POST":
        group.user_set.exclude(username=request.user.username).update(
                is_active=False)
        return HttpResponse()
    else:
        return HttpResponse(status=400)


@permission_required('account.account_admin')
def enable_group_users(request, group_id):
    if not request.is_ajax():
        raise PermissionDenied
    group = get_object_or_404(Group, pk=group_id)
    if request.method == "POST":
        group.user_set.exclude(username=request.user.username).update(
                is_active=True)
        return HttpResponse()
    else:
        return HttpResponse(status=400)


@permission_required('account.account_admin')
def remove_user(request, group_id, user_id):
    if not request.is_ajax():
        raise PermissionDenied
    group = get_object_or_404(Group, pk=group_id)
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.groups.remove(group)
        return HttpResponse()
    else:
        return HttpResponse(status=400)


@permission_required('account.account_admin')
def add_group_user(request, group_id, user_id):
    if not request.is_ajax():
        raise PermissionDenied
    group = get_object_or_404(Group, pk=group_id)
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.groups.add(group)
    else:
        return HttpResponse(status=400)


@permission_required('account.account_admin')
def create_group(request):
    if not request.is_ajax():
        raise PermissionDenied
    if request.method == "POST":
        group_name = request.POST.get('group_name', None)
        if not group_name:
            return HttpResponse(status=400, response='No group name!')
        else:
            group = Group(name=group_name)
            group.save()
            group.profile.regcode = request.POST.get('regcode', None)
            group.profile.save()
            return HttpResponse()
    else:
        return TemplateResponse(request, 'create_group.html')
        
		
@permission_required('auth.change_permission')        
def permissions(request, group_id):
    """
    Get & change permissions as set in the Django auth.
    """
    from django.contrib.auth.models import Permission
    if not request.is_ajax():
        raise PermissionDenied
    else:
    
        group = get_object_or_404(Group, pk=group_id)
        permission_list = Permission.objects.all().order_by('content_type')
        
        if request.method == "POST":
            for perm in permission_list:
                if request.POST.get('perm_%s' % perm.pk, False):
                    if perm not in group.permissions.all():
                        group.permissions.add(perm)
                else:
                    if perm in group.permissions.all():
                        group.permissions.remove(perm)
    
            return HttpResponse()
        else:
            return TemplateResponse(request, 'group_admin_permissions.html',
                {'group': group, 'perm_list': permission_list})
