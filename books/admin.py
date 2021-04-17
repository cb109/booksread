from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Author, Book, OwnedBook, Publisher, User

admin.site.site_header = "BooksRead Admin"

admin.site.register(User, UserAdmin)

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(OwnedBook)
admin.site.register(Publisher)
