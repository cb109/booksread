from typing import Optional, Tuple

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from PIL import ImageFile
import requests


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
    thumbnail_width = models.PositiveIntegerField(default=0)
    thumbnail_height = models.PositiveIntegerField(default=0)
    info_url = models.URLField(default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.title} {self.isbn or ''}"

    def update_thumbnail_dimensions_from_url(self) -> bool:
        if self.thumbnail_url:
            thumbnail_dimensions = _get_image_dimensions_from_url(self.thumbnail_url)
            if thumbnail_dimensions:
                self.thumbnail_width, self.thumbnail_height = thumbnail_dimensions
                self.save(update_fields=["thumbnail_width", "thumbnail_height"])
                return True
        return False


class OwnedBook(BaseModel):
    user = models.ForeignKey("books.User", on_delete=models.CASCADE)
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE)

    read = models.BooleanField(default=False)
    """Whether User has read the book in full yet."""

    review = models.TextField(default="", blank=True)
    """Comments/notes about User's impression of the book."""

    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(9)])
    """User's rating between 0-9."""

    def __str__(self):
        return f"{self.user} -> {self.book} {'[x]' if self.read else '[ ]'}"


def _get_image_dimensions_from_url(image_url: str) -> Optional[Tuple[int, int]]:
    # https://stackoverflow.com/a/70514550
    resume_header = {"Range": "bytes=0-2000000"}
    data = requests.get(image_url, stream=True, headers=resume_header).content
    parser = ImageFile.Parser()
    parser.feed(data)
    if parser.image:
        return parser.image.size
    return None
