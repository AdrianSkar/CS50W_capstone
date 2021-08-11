from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
		list_display = ('id', 'username', 'email')

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
		list_display = ('id', 'name', 'language')

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
		list_display = ('name', 'url', 'entry', 'link_type', 'poster')

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
		list_display = ('user', 'title', 'content', 'entry')




		
