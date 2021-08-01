from typing import List, Optional

import requests
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from .models import Author, Book, OwnedBook, Publisher


def search_google_books(
    isbn: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    max_results: Optional[int] = settings.GOOGLE_BOOKS_MAX_RESULTS,
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


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    template_name = "logout.html"


class OwnedBookList(LoginRequiredMixin, ListView):
    model = OwnedBook

    def get_queryset(self):
        """Return only Books owned by current User."""
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .order_by("book__title")
        )


@login_required
@require_http_methods(("POST",))
def add_owned_book(request):
    book_id = request.POST["book_id"]
    book = Book.objects.get(id=book_id)
    request.user.owned_books.add(book)
    return redirect("ownedbook-list")


@login_required
@require_http_methods(("POST",))
def remove_owned_book(request, ownedbook_id):
    ownedbook = OwnedBook.objects.get(id=ownedbook_id, user=request.user)
    ownedbook.delete()
    return redirect("ownedbook-list")


@login_required
@require_http_methods(("POST",))
def toggle_read(request, ownedbook_id):
    ownedbook = OwnedBook.objects.get(id=ownedbook_id, user=request.user)
    ownedbook.read = not ownedbook.read
    ownedbook.save(update_fields=["read"])
    return redirect("ownedbook-list")


@login_required
@require_http_methods(("POST",))
def set_rating(request, ownedbook_id):
    rating = request.POST["rating"]
    ownedbook = OwnedBook.objects.get(id=ownedbook_id, user=request.user)
    ownedbook.rating = rating
    ownedbook.save(update_fields=["rating"])
    return redirect("ownedbook-list")


@login_required
@require_http_methods(("POST",))
def set_review(request, ownedbook_id):
    review = request.POST["review"]
    ownedbook = OwnedBook.objects.get(id=ownedbook_id, user=request.user)
    ownedbook.review = review
    ownedbook.save(update_fields=["review"])
    return redirect("ownedbook-list")


class Search(LoginRequiredMixin, TemplateView):
    template_name = "books/search.html"


class SearchResults(LoginRequiredMixin, ListView):
    model = Book
    template_name = "books/search_results.html"
    context_object_name = "matching_books"

    def get_queryset(self):
        isbn = self.request.GET.get("isbn", None)
        title = self.request.GET.get("title", None)
        author = self.request.GET.get("author", None)

        if isbn:
            normalized_isbn = _normalize_isbn(isbn)
            google_books_data = search_google_books(isbn=normalized_isbn)
        else:
            google_books_data = search_google_books(title=title, author=author)

        book_ids = []
        volumes = google_books_data.get("items")
        if not volumes:
            return Book.objects.none()

        for volume in volumes:
            book = get_or_create_book(
                title=volume["volumeInfo"]["title"],
                author_names=volume["volumeInfo"].get("authors", []),
                publisher_name=volume["volumeInfo"].get("publisher"),
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

        matching_books = Book.objects.filter(id__in=book_ids)
        return matching_books


def _normalize_isbn(isbn):
    return str(isbn).replace(" ", "").replace("-", "").replace("_", "").replace(".", "")


def _get_isbn_from_volume(volume):
    """Prefer ISBN_13 over ISBN_10."""
    identifier_objs = volume["volumeInfo"]["industryIdentifiers"]
    for identifier_obj in identifier_objs:
        if identifier_obj["type"] == "ISBN_13":
            return identifier_obj["identifier"]
    return identifier_objs[0]["identifier"] if len(identifier_objs) else None
