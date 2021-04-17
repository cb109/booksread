from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    owned_books = models.ManyToManyField(
        "books.Book", related_name="owners", through="books.OwnedBook"
    )


class Author(models.Model):
    full_name = models.CharField(max_length=128)

    def __str__(self):
        return self.full_name


class Book(models.Model):
    title = models.CharField(max_length=128)
    isbn = models.CharField(
        unique=True, blank=True, null=True, default=None, max_length=32,
    )
    authors = models.ManyToManyField("books.Author", related_name="books")

    def __str__(self):
        return f"{self.title} {self.isbn or ''}"


class OwnedBook(models.Model):
    user = models.ForeignKey("books.User", on_delete=models.CASCADE)
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} -> {self.book}"
