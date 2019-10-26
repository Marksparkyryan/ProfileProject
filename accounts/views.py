from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import pluralize

from .forms import ProfileForm, UserForm, ChangePasswordForm, AvatarForm
from .models import Profile, User, City


def sign_in(request):
    """View that handles user sign-in and redirects to next or their 
    profile
    """
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    next_url = request.POST.get(
                        'next',
                        reverse('accounts:profile', kwargs={'user_pk': user.pk})
                    )
                    messages.success(
                        request, f'Welcome back, {user.username}!')
                    return HttpResponseRedirect(next_url)
                else:
                    messages.error(
                        request,
                        "That user account has been disabled."
                    )
            else:
                messages.error(
                    request,
                    "Username or password is incorrect."
                )
    return render(request, 'accounts/sign_in.html', {'form': form})


def sign_up(request):
    """View that handles user sign-up and redirects to user's incomplete 
    profile
    """
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(
                request,
                "You're now a user! You've been signed in, too."
            )
            return HttpResponseRedirect(reverse('accounts:profile',
                                                kwargs={'user_pk': user.id})
                                        )
        messages.error(request, "Something went wrong!")
        return render(request, 'accounts/sign_up.html', {'form': form})
    return render(request, 'accounts/sign_up.html', {'form': form})


@login_required
def edit_profile(request):
    """View that handles the editing of the request user's profile. This is done
    through data received by the user_form, profile_form, and the 
    avatar_form (the avatar form is accepted as an ajax post).
    """
    user = request.user
    existing_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }
    user_form = UserForm(data=existing_data, user=user)
    profile = get_object_or_404(Profile, user=user)
    profile_form = ProfileForm(instance=profile)
    avatar_form = AvatarForm(instance=profile)

    if request.method == 'POST':
        user_form = UserForm(data=request.POST, user=user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            cleaned = user_form.cleaned_data
            user.first_name = cleaned['first_name']
            user.last_name = cleaned['last_name']
            user.email = cleaned['email']
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return HttpResponseRedirect(reverse('accounts:profile',
                                                kwargs={'user_pk': user.id})
                                        )
        avatar_form = AvatarForm(request.POST, request.FILES, instance=profile)
        if avatar_form.is_valid() and request.is_ajax():
            profile.avatar = request.FILES['id_avatar']
            profile.save()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'avatar_form': avatar_form,
        'user': user,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password(request):
    """View that handles changing the user's password. Success redirects 
    user to their profile.
    """
    user = request.user
    password_form = ChangePasswordForm(user=user)
    if request.method == 'POST':
        password_form = ChangePasswordForm(user=user, data=request.POST)
        if password_form.is_valid():
            new_password = password_form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, "Password changed successfully!")
            return HttpResponseRedirect('accounts/profile')
    context = {
        'password_form': password_form,
        'user': user,
    }
    return render(request, 'accounts/change_password.html', context)


def profile(request, user_pk):
    """View that handles the detail view of the user and the user's 
    profile
    """
    user = get_object_or_404(User, pk=user_pk)
    profile = get_object_or_404(Profile, user=user)
    if request.user == user:
        missing = 0 #inform the user of empty profile fields
        for field in profile._meta.fields:
            field_value = field.value_from_object(profile)
            if not field_value and field_value != 0:
                missing += 1
        for field in user._meta.fields:
            field_value = field.value_from_object(user)
            if not field_value and field_value != 0:
                missing += 1
        if missing:
            messages.warning(
                request,
                f'''{missing} field{pluralize(missing)} in your profile 
                {pluralize(missing, "is,are")} missing!
                ''') # using the pluralize template filter directly in the view

    return render(request, 'accounts/profile.html', {'user': user})


def sign_out(request):
    """View handling the user's sign out and redirecting to the home 
    page
    """
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('home'))


def load_cities(request):
    """When the edit profile view is loaded, cities are emitted from the 
    options until a country is selected. When a country is selected, an 
    ajax request to this view will return a list of cities (back to the 
    edit profile template) filtered by the selected country  
    """
    country_code = request.GET.get('country')
    cities = City.objects.filter(country_id=country_code).order_by('name')
    return render(request, 'accounts/city_dropdown_list_options.html', {'cities': cities})
