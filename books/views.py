from typing import List, Optional

from django.db import transaction
from django.shortcuts import render

from .models import Author, Book, Publisher


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
        description=description, isbn=isbn, publisher=publisher, title=title,
    )
    if not created and book.authors != authors:
        book.id = None
        book.save()

    if authors:
        book.authors.set(authors)

    return book
