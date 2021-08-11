import json
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .forms import *

# Views
def index(request):
	return render(request, "devref/index.html", {
		"entry_langs": Entry.LANGS,
		"entries": Entry.objects.all().order_by('name'),
		# "message": "Test message on index",
		# "alert_type": "alert-warning"
	})

@csrf_exempt
def entry_view(request, entry_name):
	
	# Function to add sites to sites/examples sections (DRY)
	def process_site():
		site_form = SiteForm(request.POST)
		if	site_form.is_valid():
			try:
				obj = site_form.save(commit=False)
				obj.entry = entry
				obj.poster = request.user
				obj.link_type = request.POST.get('link_type')
				obj.save()
				response = HttpResponseRedirect(reverse('entry', args=(entry.name,)))
				return response

			except IntegrityError as error:
				context['message'] = error
				return render(request, 'devref/entry.html', context)

	try:
		entry = Entry.objects.get(name=entry_name)
		context = {
			'entry': entry,
			"devdocs": Entry.objects.get(name=entry_name).get_pages().filter(name__iexact='devdocs').first(),
			# 'message': message,
			# 'alert_type': 'alert-success'
		}
		# Logged-in users can add sites, examples and view/edit notes:
		if request.user.is_authenticated:
			context["note_form"] = NoteForm()
			context["site_form"] = SiteForm()
			context['notes'] = Note.objects.filter(user=request.user, entry=entry)
		
		# Add note request
		if request.method == 'POST' and request.POST.get('note') == 'add_note':
			print('Add note form')
			note_form = NoteForm(request.POST)
			if	note_form.is_valid():
				try:
					obj = note_form.save(commit=False)
					obj.entry = entry
					obj.user = request.user
					obj.save()

					response = HttpResponseRedirect(reverse('entry', args=(entry.name,)))
					response['Location'] += '?devvy_note=' + str(obj.id)
					return response

				except IntegrityError as error:
					context['message'] = error
					return render(request, 'devref/entry.html', context)

		# Add site request
		elif request.method == 'POST' and request.POST.get('site') == 'add_site':
			print('Add site form')
			process_site()

		# Add example request
		elif request.method == 'POST' and request.POST.get('site') == 'add_example':
			print('Add example form')
			process_site()

		# Edit/delete note request
		elif request.method == 'PUT':
			data = json.loads(request.body)
			note = Note.objects.get(id=data['note'])

			# Delete
			if data.get('delete'):
				note.delete()
				return HttpResponse(status=200)
			
			# Edit
			elif data.get('edit'):
				if request.user == note.user:
					note.title = data['title']
					note.content = data['content']
					note.save()
					return HttpResponse(status=200)

	except Entry.DoesNotExist:
		return render(request, "devref/entry.html", {
			"message": "That entry doesn't exist yet",
			"alert_type": "alert-danger",
		})

	# If GET request contains gist or note, pass it to context.
	if request.GET.get('gist'):
		context['gist_url'] = request.GET.get('gist')

	# If the user has a note URL but isn't logged-in.
	if request.GET.get('devvy_note') and not request.user.is_authenticated:
			context["message"] = "You need to be logged-in to view your notes."
			context["alert_type"]= "alert-danger"
		
	# Otherwise, when logged-in.
	elif request.GET.get('devvy_note'):
		context['note_content'] = Note.objects.filter(user=request.user, id=request.GET.get('devvy_note')).first()
		
		# If that note doesn't exist
		if context['note_content'] == None:
			context['message'] = "That note doesn't exist."
			context['alert_type'] = 'alert-warning'
			return render(request, 'devref/entry.html', context)

	return render(request, 'devref/entry.html', context)

@csrf_exempt
@login_required
def note_content(request, note_id):
	note = Note.objects.get(id=note_id)

	if request.method == 'GET' and request.user == note.user:
		return JsonResponse(note.serialize())
	else:
		return JsonResponse({'error': 'Only the author can see this note'})

# Search
def search(request):
	if request.method == "GET":
			query = request.GET.get('query')
			entry = Entry.objects.filter(name='query')
			substr = Entry.objects.filter(name__contains=query).order_by('language')

			# If we have such an entry, render it.
			## Used .filter.first() instead of objects.get to be able to get search 
			## results or None instead of DoesNotExist errors.
			if entry.first():
				return render(request, "devref/entry.html", {
						"entry": Entry.objects.get(name=query)
				})
			# If query is a substring of existing entries, render matches.
			elif substr:
				return render(request, 'devref/search.html', {
						"search_entries": substr,
						"query": query
				})
			
			else:
				# If no complete or partial match is found, give feedback.
				return render(request, "devref/search.html", {
						"no_match": query
				})

# User's bookmarks
@login_required
def user_bookmark_view(request):
	user = request.user
	bookmarks = Entry.objects.filter(bookmarked_by=user).order_by('language')

	# If the user has bookmarks, present them
	if bookmarks:
		return render(request, "devref/bookmarks.html", {
				"bookmarks": bookmarks
		})
	
	else:
		return render(request, "devref/bookmarks.html", {
				"no_match": 'no match'
		})

# Bookmark management (check, add, remove)
@csrf_exempt
@login_required
def bookmark_view(request, entry_name):
	try:
		entry = Entry.objects.get(name=entry_name)
	except DoesNotExist:
		return JsonResponse({"error": "Entry not found."})
	
	# Get request (to check already liking)
	if request.method == 'GET':
		return JsonResponse(entry.serialize())
	
	# Put request (to bookmark/un-bookmark)
	elif request.method == 'PUT':
		data = json.loads(request.body)
		if data.get('bookmark') == True:
			entry.bookmarked_by.add(request.user)
			entry.save()
		else:
			entry.bookmarked_by.remove(request.user)
			entry.save()
		
		return HttpResponse(status=204)
	
	else: 
		return JsonResponse({
			"error": "GET or PUT request required"
		}, status=400)

# New entry
@login_required
def new_entry_view(request):
	if request.method == "POST":
		name = request.POST["name"]
		language = request.POST["language"]
		
		# Create new entry
		print('Add new entry')
		entry_form = EntryForm(request.POST)
		if	entry_form.is_valid():
			try:
				entry_form.save()
				entry = Entry.objects.get(name=name)
				response = HttpResponseRedirect(reverse('entry', args=(entry.name,)))
				return response

			except IntegrityError as error:
				context = {
					'message': error,
					'alert_type': 'alert-danger'
				}
				return render(request, 'devref/entry.html', context)

	else:
		return render(request, "devref/new_entry.html", {
			"new_entry_form": EntryForm()
		})

## User account actions
def login_view(request):

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		next_url = request.POST['next'] or 'index'
		user = authenticate(request, username=username, password=password)

		# Check for correct authentication
		if user is not None:
			login(request, user)
			return redirect(next_url)
		else:
			return render(request, "devref/login.html", {
				"message": "Invalid username and/or password.",
				"alert_type": "alert-danger"
			})
	
	else:
		return render(request, "devref/login.html")

def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse("index"))

def register_view(request):
	if request.method == "POST":
		username = request.POST["username"]
		email = request.POST["email"]

		# Pass confirm
		password = request.POST["password"]
		confirm = request.POST["confirmation"]
		if password != confirm:
			return render(request, "devref/register", {
				"message": "Passwords must be the same.",
				"alert_type": "alert-warning"
			})
		
		# Try to create new user
		try:
			user = User.objects.create_user(username, email, password)
			user.save()
		except IntegrityError:
			return render(request, "devref/register", {
				"message": "Username already exists.",
				"alert_type": "alert-danger"
			})
		
		login(request, user)
		return HttpResponseRedirect(reverse("index"))
	else:
		return render(request, "devref/register.html")

