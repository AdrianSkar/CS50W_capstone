from django.db import models
from django.db.models import Count
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
	id = models.AutoField(primary_key=True)
	

class Entry(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=70)

	# Languages
	LANGS = (
		('HTML', 'HTML'),
		('CSS', 'CSS'),
		('JS', 'JavaScript'),
		('PY', 'Python'),
		('GIT', 'Git'),
	)
	language = models.CharField(max_length=10, choices=LANGS, blank=False)
	bookmarked_by = models.ManyToManyField("User", related_name='bookmarker', blank=True)

	def __str__(self):
			return f"{self.name}, lang: {self.language}"
	
	# Output page links ordered by likes
	def get_pages(self):
		return self.entry_site.filter(link_type='PG').annotate(num_likes=Count('liked_by')).order_by('num_likes')

	# Output page examples ordered by likes
	def get_examples(self):
		return self.entry_site.filter(link_type='EG').annotate(num_likes=Count('liked_by')).order_by('num_likes')

	def serialize(self):
		return {
			"name": self.name,
			"bookmarkers": [User.username for User in self.bookmarked_by.all()]
		}


class Site(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.URLField(max_length=600)
	name = models.CharField(max_length=30)
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='entry_site')

	# Type choice
	SITE_TYPES = (
		('PG', 'Page'),
		('EG', 'Example')
	)
	link_type = models.CharField(max_length= 2, choices=SITE_TYPES, blank=False)

	poster = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="posted_by")
	liked_by = models.ManyToManyField("User", related_name='liker', blank=True)

class Note(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=30)
	content = models.CharField(max_length=3000)
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='entry_note')

	def __str__(self):
			return f"User: {self.user}, entry: {self.entry}"
	
	def serialize(self):
		return {
			"id": self.id,
			"title": self.title,
			"content": self.content
		}
	
