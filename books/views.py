from typing import List, Optional

import requests
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from .models import Author, Book, Publisher


def search_google_books(
    isbn: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    max_results: Optional[int] = 5,
    language: Optional[str] = settings.GOOGLE_BOOKS_LANGUAGE_RESTRICT,
) -> dict:
    if not any([isbn, title, author]):
        raise ValueError("Must search by either ISBN or title/author")

    url = settings.GOOGLE_BOOKS_BASE_URL
    query = "?q="
    if isbn:
        query += f"isbn:{isbn}"
    elif title or author:
        if title:
            query += f"intitle:{title}"
        if title and author:
            query += ","
        if author:
            query += f"inauthor:{author}"

    query += f"&maxResults={max_results}"
    if language:
        query += f"&langRestrict={language}"
    url += query

    response = requests.get(url)
    return response.json()


@transaction.atomic()
def get_or_create_book(
    title: str,
    author_names: List[str],
    isbn: Optional[str] = None,
    publisher_name: Optional[str] = None,
):
    publisher = None
    if publisher_name:
        publisher, _ = Publisher.objects.get_or_create(name=publisher_name)

    authors = []
    for author_name in author_names:
        author, _ = Author.objects.get_or_create(full_name=author_name)
        authors.append(author)

    if isbn:
        book, created = Book.objects.get_or_create(
            isbn=isbn,
        )
        if created:
            book.publisher = publisher
            book.title = title
            book.save()
    else:
        book, created = Book.objects.get_or_create(
            publisher=publisher,
            title=title,
        )

    if authors:
        book.authors.set(authors)

    return book


class LoginView(auth_views.LoginView):
    template_name = "login.html"


class LogoutView(auth_views.LogoutView):
    template_name = "logout.html"


class SearchGoogleBooks(ListView):
    model = Book
    template_name = "search-list.html"

    def get_queryset(self):
        isbn = self.request.GET.get("isbn", None)
        title = self.request.GET.get("title", None)
        author = self.request.GET.get("author", None)

        if isbn:
            google_books_data = search_google_books(isbn=isbn)
        else:
            google_books_data = search_google_books(title=title, author=author)

        book_ids = []
        volumes = google_books_data.get("items")
        if not volumes:
            return Book.objects.none()

        for volume in volumes:
            book = get_or_create_book(
                title=volume["volumeInfo"]["title"],
                author_names=volume["volumeInfo"]["authors"],
                isbn=_get_isbn_from_volume(volume),
            )

            search_info = volume.get("searchInfo")
            if search_info:
                description = search_info.get("textSnippet", "")
                if description:
                    book.description = description
                    book.save(update_fields=["description"])

            num_pages = volume["volumeInfo"].get("pageCount", 0)
            if num_pages:
                book.num_pages = num_pages
                book.save(update_fields=["num_pages"])

            image_links = volume["volumeInfo"].get("imageLinks")
            if image_links:
                book.thumbnail_url = image_links.get(
                    "thumbnail", image_links.get("smallThumbnail")
                )
                book.save(update_fields=["thumbnail_url"])

            book.info_url = volume["volumeInfo"]["infoLink"]
            book.save(update_fields=["info_url"])

            book_ids.append(book.id)

        return Book.objects.filter(id__in=book_ids)


def _get_isbn_from_volume(volume):
    """Prefer ISBN_13 over ISBN_10."""
    identifier_objs = volume["volumeInfo"]["industryIdentifiers"]
    for identifier_obj in identifier_objs:
        if identifier_obj["type"] == "ISBN_13":
            return identifier_obj["identifier"]
    return identifier_objs[0]["identifier"] if len(identifier_objs) else None
