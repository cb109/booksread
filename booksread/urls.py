"""booksread URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from books import views as books_views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin", admin.site.urls),
    path(
        "login",
        books_views.LoginView.as_view(),
        name="login",
    ),
    path(
        "logout",
        books_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "books",
        books_views.OwnedBookList.as_view(),
        name="ownedbook-list",
    ),
    path(
        "books/<int:pk>",
        books_views.OwnedBookEdit.as_view(),
        name="ownedbook-edit",
    ),
    path(
        "books/add",
        books_views.add_owned_book,
        name="ownedbook-add",
    ),
    path(
        "books/<int:ownedbook_id>/remove",
        books_views.remove_owned_book,
        name="ownedbook-remove",
    ),
    path(
        "books/<int:ownedbook_id>/rate",
        books_views.set_rating,
        name="ownedbook-rate",
    ),
    path(
        "books/<int:ownedbook_id>/review",
        books_views.set_review,
        name="ownedbook-review",
    ),
    path(
        "books/<int:ownedbook_id>/toggleread",
        books_views.toggle_read,
        name="ownedbook-toggleread",
    ),
    path(
        "search",
        books_views.Search.as_view(),
        name="search",
    ),
    path(
        "",
        books_views.OwnedBookList.as_view(),
        name="fallback",
    ),
]
