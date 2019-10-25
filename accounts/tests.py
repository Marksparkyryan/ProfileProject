from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.test import TestCase

from cities_light.models import Country, City
from .forms import ProfileForm, UserForm
from .models import Profile

import datetime
import os
import random

class AccountsViewsTests(TestCase):
    fixtures = ['country_city_data.json']

    def get_avatar(self):
        path = settings.MEDIA_ROOT + '/owls'
        files = os.listdir(path)
        index = random.randint(0, len(files) - 1)
        return 'owls/' + files[index]

    def setUp(self):
        self.user1 = User.objects.create(
            username="Johny",
            first_name="John",
            last_name="Smith",
            email="johnsmith@email.com",
            password="TestPassword123@#$",
        )
        self.profile1 = Profile.objects.create(
            user=self.user1,
            date_of_birth="1985-08-18",
            bio="A little about John and his life.",
            avatar=self.get_avatar(),
            cats_or_dogs="Dogs",
            favourite_colour="Green",
            hobby="Photography",
            country=Country.objects.get(name='Canada'),
            city=City.objects.get(name='Toronto'),
        )
        self.user2 = User.objects.create(
            username="Janey",
            first_name="Jane",
            last_name="Smith",
            email="janesmith@email.com",
            password="janesmithjaney"
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            date_of_birth="1988-07-04",
            bio="A little about Jane and her life.",
            avatar=self.get_avatar(),
            cats_or_dogs="Cats",
            favourite_colour="Blue",
            hobby="Crosswords",
            country=Country.objects.get(name='United States'),
            city=City.objects.get(name='Chicago'),
        )

    def test_signin_view(self):
        """make sure sign-in view renders"""
        resp = self.client.get(reverse('accounts:sign_in'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/sign_in.html')

    def test_signin_view_reidrects(self):
        """make sure signin view redirects upon successful login"""
        resp = self.client.post('/accounts/sign_in/', {
            'username': 'Johny',
            'password': 'TestPassword123@#$',
        })
        self.assertEqual(resp.status_code, 200)

    def test_signin_view_redirects_baduser(self):
        """make sure singin view redirects bad login with message"""
        resp = self.client.post('/accounts/sign_in/', {
            'username': 'baduser',
            'password': 'baduserpassword',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp,
                            "Please enter a correct username and password. "
                            "Note that both fields may be case-sensitive.")

    def test_signup_view(self):
        """make sure sign-up view renders"""
        resp = self.client.get(reverse('accounts:sign_up'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/sign_up.html')
    
    def test_signup_view_valid_password(self):
        """make sure sign-up view allows user with good password to 
        sign up
        """
        resp = self.client.post('/accounts/sign_up/', {
            'username': 'goodusername',
            'password1': 'GoodUserPassword123@#$',
            'password2': 'GoodUserPassword123@#$',
        })
        self.assertEqual(resp.status_code, 302)

    def test_signup_view_invalid_password(self):
        """make sure sign-up view allows user with good password to 
        sign up
        """
        resp = self.client.post('/accounts/sign_up/', {
            'username': 'badusername',
            'password1': 'badusernamepassword',
            'password2': 'badusernamepassword',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/sign_up.html')
        self.assertContains(resp, "Something went wrong!")

    def test_profile_view(self):
        """make sure profile view renders correctly"""
        resp = self.client.get(reverse('accounts:profile',
                                       kwargs={'user_pk': self.user1.id}))
        self.assertTemplateUsed(resp, 'accounts/profile.html')
        self.assertContains(resp, "Misc")
        self.assertContains(resp, "Photography")

    def test_profile_view_bad_pk(self):
        """make sure 404 displayed with out of range pk"""
        resp = self.client.get(reverse('accounts:profile',
                                        kwargs={'user_pk': 0}))
        self.assertEqual(resp.status_code, 404)

    def test_edit_profile_view_session(self):
        """make sure edit profile view renders correctly for user that 
        is logged in
        """
        session = self.client.force_login(self.user1)
        resp = self.client.get(reverse('accounts:edit_profile'))
        self.assertTemplateUsed(resp, 'accounts/edit_profile.html')
        self.assertContains(resp, "Change Password")
    
    def test_edit_profile_view_no_session(self):
        """make sure edit profile view doesn't render for user that 
        isn't logged in, and is redirected to log in view
        """
        resp = self.client.get(reverse('accounts:edit_profile'), follow=True)
        self.assertTemplateUsed(resp, 'accounts/sign_in.html')

    def test_change_password_view(self):
        """make sure change password view renders correctly for logged 
        in user
        """
        session = self.client.force_login(self.user1)
        resp = self.client.get(reverse('accounts:change_password'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/change_password.html')
    
    def test_change_password_view_no_session(self):
        """make sure change password view doesn't render for user 
        without logged in session
        """
        resp = self.client.get(reverse('accounts:change_password'), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/sign_in.html')
    
    def test_sign_out_view(self):
        """make sure sign out view logs user out"""
        session = self.client.force_login(self.user1)
        resp = self.client.get(reverse('home'))
        self.assertContains(resp,"Sign out")
        resp = self.client.get(reverse('accounts:sign_out'), follow=True)
        self.assertContains(resp, 'Sign in')


class AccountsProfileModelTests(TestCase):
    fixtures = ['country_city_data.json']

    def get_avatar(self):
        path = settings.MEDIA_ROOT + '/owls'
        files = os.listdir(path)
        index = random.randint(0, len(files) - 1)
        return 'owls/' + files[index]

    def setUp(self):
        self.user1 = User.objects.create(
            username="Johny",
            first_name="John",
            last_name="Smith",
            email="johnsmith@email.com",
            password="TestPassword123@#$",
        )
        self.profile1 = Profile.objects.create(
            user=self.user1,
            date_of_birth="1985-08-18",
            bio="A little about John and his life.",
            avatar=self.get_avatar(),
            cats_or_dogs="Dogs",
            favourite_colour="Green",
            hobby="Photography",
            country=Country.objects.get(name='Canada'),
            city=City.objects.get(name='Toronto'),
        )
    
    def test_str_is_username(self):
        """test model __str__ method"""
        user = User.objects.get(pk=self.user1.pk)
        self.assertEqual(str(user), user.username)

    def test_avatar(self):
        user = User.objects.get(pk=self.user1.pk)
        self.assertIsNotNone(user.profile.avatar)


class AccountsFormsTests(TestCase):
    fixtures = ['country_city_data.json']

    def get_avatar(self):
        path = settings.MEDIA_ROOT + '/owls'
        files = os.listdir(path)
        index = random.randint(0, len(files) - 1)
        return 'owls/' + files[index]

    def setUp(self):
        self.user1 = User.objects.create(
            username="Johny",
            first_name="John",
            last_name="Smith",
            email="johnsmith@email.com",
            password="TestPassword123@#$",
        )
        self.profile1 = Profile.objects.create(
            user=self.user1,
            date_of_birth="1985-08-18",
            bio="A little about John and his life.",
            avatar=self.get_avatar(),
            cats_or_dogs="Dogs",
            favourite_colour="Green",
            hobby="Photography",
            country=Country.objects.get(name='Canada'),
            city=City.objects.get(name='Thorold'),
        )
    
    def test_profile_form_init(self):
        ProfileForm(instance=self.profile1)

    def test_profile_form_date_format(self):
        profile_data = {
            'date_of_birth': '1985-08-18',
            'bio': "A little about me and more",
            'cats_or_dogs': 'Dogs',
            'favourite_colour': 'green',
            'hobby': 'photography',
            'country': 1,
        }
        profile_form = ProfileForm(data=profile_data)
        self.assertTrue(profile_form.is_valid())

        profile_data['date_of_birth'] = '08/18/1985'
        self.assertTrue(profile_form.is_valid())

        profile_data['date_of_birth'] = '08/18/85'
        self.assertTrue(profile_form.is_valid())

        profile_data['date_of_birth'] = ''
        self.assertTrue(profile_form.is_valid())
    


     
        










    
        


    
