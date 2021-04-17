from typing import List, Optional

from django.db import transaction
from django.shortcuts import render

from .models import Author, Book


@transaction.atomic()
def get_or_create_book(
    title: str, author_names: List[str], isbn: Optional[str] = None,
):
    if isbn:
        book = Book.objects.filter(isbn=isbn).first()
        if book:
            return book

    authors = []
    for author_name in author_names:
        author, _ = Author.objects.get_or_create(full_name=author_name)
        authors.append(author)

    book, created = Book.objects.get_or_create(title=title, isbn=isbn)
    if not created and book.authors != authors:
        # Instead of modifying existing book, create a copy with this
        # set of authors instead.
        book.id = None
        book.save()

    book.authors.set(authors)

    return book
