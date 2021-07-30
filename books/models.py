from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class User(BaseModel, AbstractUser):
    owned_books = models.ManyToManyField(
        "books.Book", related_name="owners", through="books.OwnedBook"
    )


class Author(BaseModel):
    full_name = models.CharField(max_length=128)

    def __str__(self):
        return self.full_name


class Publisher(BaseModel):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Book(BaseModel):
    title = models.CharField(max_length=128)
    isbn = models.CharField(
        unique=True,
        blank=True,
        null=True,
        default=None,
        max_length=32,
    )
    authors = models.ManyToManyField("books.Author", related_name="books")
    publisher = models.ForeignKey(
        "books.Publisher",
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="books",
    )
    description = models.TextField(default="")
    num_pages = models.IntegerField(default=0)
    thumbnail_url = models.URLField(default=None, blank=True, null=True)
    info_url = models.URLField(default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.title} {self.isbn or ''}"


class OwnedBook(BaseModel):
    user = models.ForeignKey("books.User", on_delete=models.CASCADE)
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} -> {self.book}"
