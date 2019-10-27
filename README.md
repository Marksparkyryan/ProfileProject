# ProfileProject
The profile project is an app that features a user's information in a profile-like format. Users can sign up, fill out a profile, update their profile, update their password, update their avatar, and explore other profiles in the database.   

<br/>

# Features
* A profile model that is one-to-one with the default Django user model
* An embedded text editor for the bio field
* An image editor for the avatar field
* An auto-rotating avatar corousel on the home page
* A password strength meter
* An ajax call to populate the cities list dependent on country selection

<br/>

# installation

1. cd into your directory of projects (or wherever you prefer to keep your clones)
2. git clone ```https://github.com/Marksparkyryan/ProfileProject.git``` to clone the app
3. ```virtualenv .venv``` to create your virtual environment
4. ```source .venv/bin/activate``` to activate the virtual environment
5. ```pip install -r ProfileProject/requirements.txt``` to install app requirements
6. cd into the ProfileProject/profile_project directory
7. ```python manage.py runserver``` to serve the site to your local host (in DEBUG mode)
8. visit ```http://127.0.0.1:8000/``` to see some profiles! 

<br/>

# Credits
Default profile avatars are provided by:
https://www.vecteezy.com/vector-art/138704-set-of-cute-owls-vector
<br/>
The profile bio text editor is powered by:
https://quilljs.com/docs/quickstart/
<br/>
The home page avatar carousel powered by:
https://kenwheeler.github.io/slick/
<br/>
In the edit profile page, the ajax feature on the cities selection list was possible by following Vitor Freitas' tutorial: https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
<br/>
The password field strength meter powered by:https://github.com/dropbox/zxcvbn

