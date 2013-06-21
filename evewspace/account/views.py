#    Eve W-Space
#    Copyright (C) 2013  Andrew Austin and other contributors
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version. An additional term under section
#    7 of the GPL is included in the LICENSE file.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from account.models import RegistrationForm
from account.utils import *
from account.forms import EditProfileForm
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.forms.util import ErrorList
# Create your views here.

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
                    form._errors['regcode'] = ErrorList([u'Invalid Registration Code.'])
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
                form._errors['password'] = ErrorList([u'The password you entered is incorrect.'])
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
