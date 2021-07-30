from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Author, Book, OwnedBook, Publisher, User


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "created_at",
        "id",
    )


class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author_names",
        "publisher",
        "num_pages",
        "created_at",
        "id",
    )
    filter_horizontal = ("authors",)
    autocomplete_fields = ("publisher",)
    search_fields = ("title",)

    def author_names(self, book):
        return ", ".join(
            [author.full_name for author in book.authors.order_by("full_name")]
        )


class PublisherAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
        "id",
    )
    search_fields = ("name",)


class OwnedBookAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "book",
        "created_at",
        "id",
    )
    autocomplete_fields = ("user", "book")


admin.site.site_header = "BooksRead Admin"

admin.site.register(User, UserAdmin)

admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(OwnedBook, OwnedBookAdmin)
admin.site.register(Publisher, PublisherAdmin)
