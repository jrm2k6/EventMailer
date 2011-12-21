from django import forms
from django.db import models
from authentication_eventmailer.models import Kind

GENDER_CHOICES = (
	(0,'Male'),
	(1,'Female'),
	(2,'Not determined')
)

AGE_CHOICES = (
	(0,'Under 18'),
	(1,'18-25'),
	(2,'25-35'),
	(3,'35-50'),
	(4,'Up 50')
	)

class AuthenticationGmailForm(forms.Form):
	email_address = forms.CharField(max_length=80, label='Enter your gmail address')
	password = forms.CharField(max_length=80, label='Password',  widget=forms.PasswordInput)	


class KindEventForm(forms.Form):
	kind_choice = forms.ModelChoiceField(queryset=Kind.objects.all(), label = 'Which kind of event do you want to create?')
	#target_choice = forms.CharField(max_length=200, widget = forms.Select(choices=GENDER_CHOICES))
	#age_choice = forms.CharField(max_length=200, choices=AGE_CHOICES)
