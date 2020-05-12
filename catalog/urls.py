# // /catalog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-url'),
]

urlpatterns += [
    path('books/', views.BookListView.as_view(), name='books-url'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail-url'),
    path('authors/', views.AuthorListView.as_view(), name='authors-url'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail-url'),
]

# // p8> add borrower books
urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-loan-url'),
    path('books-in-loan/', views.AllLoanedBooksView.as_view(), name='all-loan-url'),
]

# // p9> form for renew book
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-url'),
]

# // p9> form for editing author
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create-url'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update-url'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete-url'),
    path('book/create/', views.BookCreate.as_view(), name='book-create-url'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update-url'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete-url'),
]

