from typing import List, Optional

import requests
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

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
    description: Optional[str] = "",
):
    publisher = None
    if publisher_name:
        publisher, _ = Publisher.objects.get_or_create(name=publisher_name)

    authors = []
    for author_name in author_names:
        author, _ = Author.objects.get_or_create(full_name=author_name)
        authors.append(author.id)

    book, created = Book.objects.get_or_create(
        description=description,
        isbn=isbn,
        publisher=publisher,
        title=title,
    )
    if not created and book.authors != authors:
        book.id = None
        book.save()

    if authors:
        book.authors.set(authors)

    return book


class LoginView(auth_views.LoginView):
    template_name = "login.html"


class LogoutView(auth_views.LogoutView):
    template_name = "logout.html"
