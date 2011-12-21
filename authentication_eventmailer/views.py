from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from django.shortcuts import render_to_response, redirect
from forms import AuthenticationGmailForm, KindEventForm
from models import Kind, Event
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import gdata.contacts.service
import atom
import gdata.contacts
import types
import re
from rapleafApi import RapleafApi
from django.core.mail import send_mass_mail, get_connection, EmailMultiAlternatives 


def index(request):
	form = AuthenticationGmailForm(request.POST)
	return render_to_response('authentication_eventmailer/welcome.html', {'form' : form}, RequestContext(request))

def authentication(request):
	if request.method =='POST':
		form = AuthenticationGmailForm(request.POST)
		if form.is_valid():
			email_address = form.cleaned_data['email_address']
			email_password = form.cleaned_data['password']
			# Session variable
			request.session['email_address_user']=email_address
			request.session['email_password_user']=email_password
			password = form.cleaned_data['password']
			instance_connexion = authentication_google_account(email_address, password)
			if type(instance_connexion) is not types.StringType:
				contact_feed = retrieve_all_contacts(instance_connexion)
				list_emails = print_contacts_from_feed(contact_feed)
				request.session['list_emails'] = list_emails
				kind_event_form = KindEventForm(request.GET)
				return render_to_response('event_creation/home.html', { 'email_address' : email_address, 'kind_form' : kind_event_form}, RequestContext(request))
			else : return render_to_response('authentication_eventmailer/welcome.html', {'form' : form, 'auth_error' : instance_connexion}, RequestContext(request))
	return index(request);




def authentication_google_account(_email, _pw):
	gd_client = gdata.contacts.service.ContactsService()
	gd_client.email = _email
	gd_client.password = _pw
	gd_client.source = 'Google data Contact'
	try:
		gd_client.ProgrammaticLogin()
		return gd_client
	except gdata.service.BadAuthentication as e:
        	print "%s" % e
        	return 'Wrong email or/and password'
    	except Exception as e:
        	print  "%s" % e
        	return 'A problem has occurred'



def retrieve_all_contacts(gd_client):
	query = gdata.contacts.service.ContactsQuery()
	query.max_results = 200
	feed = gd_client.GetContactsFeed(query.ToUri())
	return feed



def print_contacts_from_feed(gfeed):
	list_contacts = []
	for entry in gfeed.entry:
		contact_properties = []
		contact_properties.append(entry.title.text)
		for email in entry.email:
			if email.primary :
				contact_properties.append(email.address)
		list_contacts.append(contact_properties)
		print contact_properties
	list_emails = []
	if len(list_contacts) > 0:
		for contact in list_contacts:
			for item in contact:
				if item is not None:
					item = item.lower()
					if re.match('[a-z0-9]+\.[a-z0-9]+\@[a-z]+\.[a-z]+',str(item)):
						list_emails.append(str(item))
	return list_emails			


def save_event(request):
	if request.method == 'GET':
		q = request.GET.get("js_kind_value")
		if q:
			pkind = transform_text(q)
			kind = verify_kind_exists('kind_value',pkind)
			if kind is None:
				if (verify_get_param(request,'js_gender_value') and verify_get_param(request,'js_age_value')):
					new_kind = Kind(kind_value= pkind,gender_target=request.GET.get('js_gender_value'), age_target=request.GET.get('js_age_value'))
					new_kind.save()
					kind = Kind.objects.get(kind_value=pkind)
		elif request.GET.get('kind_choice'):
			kind = verify_kind_exists('id',request.GET.get('kind_choice'))
			print kind
		else:
			pass	
		event_name_value = request.GET.get("js_event_name")
		description_event_value = request.GET.get("js_event_description")
		if event_name_value is not '' and description_event_value is not '':
			event_name_value = transform_text(event_name_value)
			existent_name = verify_event_properties_exists('name', event_name_value)
			description_event_value = transform_text(description_event_value)
			existent_description = verify_event_properties_exists('description', description_event_value)
			# An event with the passed name or description could not be already stored..
			if existent_description is None  and existent_name is None:
				new_event = Event(name=event_name_value, description=description_event_value, creation_date = datetime.now, kind_event = kind)
				new_event.save()
				return determine_interested_people(request, new_event)			
			return render_to_response('event_creation/home.html', {'email_address' : request.session['email_address_user'],'error_message' : 'Event name/description already exist','kind_form' : KindEventForm(request.GET)}, RequestContext(request))
		return render_to_response('event_creation/home.html', {'email_address' : request.session['email_address_user'],'error_message' : 'An error has occurred','kind_form' : KindEventForm(request.GET)}, RequestContext(request))
	return render_to_response('event_creation/home.html', {'email_address' : request.session['email_address_user'],'error_message': 'An error has occurred','kind_form' : KindEventForm(request.GET)}, RequestContext(request))



def verify_kind_exists(field,vkind):
	try:
		if field is 'kind_value':
			existentObj = Kind.objects.get(kind_value=vkind)
		else:
			existentObj = Kind.objects.get(id=vkind)
	except Kind.DoesNotExist:
    		existentObj = None
	return existentObj



def transform_text(vkind):
	nvkind = ''
	nvkind += vkind[0].upper()
	for i in range(1, len(vkind)):
		nvalue = vkind[i].lower()
		nvkind += nvalue
	return nvkind	


def verify_event_properties_exists(field,value):
	try:
		if field is 'name':
			existentObj = Event.objects.get(name=transform_text(value))
		elif field is 'description':
			existentObj = Event.objects.get(description=transform_text(value))
	except Event.DoesNotExist:
		existentObj = None
	return existentObj


def verify_get_param(request,param):
	return request.GET.get(param)



def determine_interested_people(request, eventInstance):
	# We get the emails' list from the session variable
	list_emails = request.session['list_emails']
	gender = get_string_gender(eventInstance.kind_event.gender_target)
	age = get_value_maximum_age(eventInstance.kind_event.age_target)
	list_char = []
	if gender is not 'Undetermined':
		list_char.append(str(gender))
	
	list_contact_with_properties =properties_contacts(list_emails, request.session['email_address_user'])	
	sorted_contacts = sort_contact(list_contact_with_properties,['gender'],[gender])
	return render_to_response('event_creation/listing.html', {'email_address' : request.session['email_address_user'],'list_interested': sorted_contacts[0], 'list_others': sorted_contacts[1],'gender':gender, 'age':age, 'event_instance':eventInstance },RequestContext(request))

def sort_contact(list_items,list_characteristics,value_characteristics):
	list_interested_people=[]
	list_others = []
	nb_common_char = 0
	for item in list_items:
		if len(list_characteristics) is not 0: 
			for i in  range(0,len(list_characteristics)):
				if item.has_key(list_characteristics[i]) and item[str(list_characteristics[i])] == str(value_characteristics[i]):
					nb_common_char+=1
			if nb_common_char >= 1:
				list_interested_people.append(item['email'])
			else:
				list_others.append(item['email'])
			nb_common_char = 0
		else:
			list_interested_people.append(item['email'])
	return list_interested_people,list_others







def get_string_gender(int_gender):
	if int_gender is 0:
		return 'Male'
	elif int_gender is 1:
		return 'Female'
	else:
		return 'Undetermined'


def get_value_maximum_age(int_age):
	if int_age is 0:
		return 18
	elif int_age is 1:
		return 25
	elif int_age is 2:
		return 35
	elif int_age is 3:
		return 50
	elif int_age is 4:
		return 100
	elif int_age is 5:
		return 0




def properties_contacts(list_emails, user_address):
	info_from_email = []
	api = RapleafApi.RapleafApi(settings.RAPLEAF_KEY)
	try:
		for item in list_emails:
			if item is not user_address:
				info_current_item = {}
				info_current_item['email'] = item
				response = api.query_by_email(item)
  				for k, v in response.iteritems():
					info_current_item[k]= v
				info_from_email.append(info_current_item)
		return info_from_email
	except Exception as e:
		return e


def send_emails(request):
	if request.method =='POST':
		recipients = request.POST.getlist('recipients')
		event_name = request.POST.get('event_name')
		event_description = request.POST.get('event_description')
		event_type = request.POST.get('event_type')
		text_content=str(request.session['email_address_user'])+' has created the event : '+str(event_name)+' and want to invite you, contact him/her for more details'
		_connection = get_connection()
		msg = EmailMultiAlternatives("Event invitation", text_content, request.session['email_address_user'], recipients, connection=_connection)
		msg.send()
		return render_to_response('event_creation/home.html', { 'email_address' : request.session['email_address_user'], 'kind_form' : KindEventForm(request.GET), 'confirm_message':'Emails sent sucessfully'}, RequestContext(request))
	return render_to_response('event_creation/home.html', { 'email_address' : request.session['email_address_user'], 'kind_form' : KindEventForm(request.GET), 'error_message':'Something wrong has occurred'}, RequestContext(request))
