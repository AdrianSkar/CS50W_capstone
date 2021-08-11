from django.urls import path

from . import views

urlpatterns = [
		path("", views.index, name="index"),
		path("entries/<str:entry_name>", views.entry_view, name="entry"),
		path("search/", views.search, name="search"),
		path("bookmarks/", views.user_bookmark_view, name="bookmarks"),
		path("new", views.new_entry_view, name="new_entry"),

		# User accounts
		path("login", views.login_view, name="login"),
		path("logout", views.logout_view, name="logout"),
		path("register", views.register_view, name="register"),

		# "API"
		path("note/<int:note_id>", views.note_content, name="note_content"),
		path("bookmarkers/<str:entry_name>", views.bookmark_view, name="bookmark"),
]
