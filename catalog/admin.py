# // 5 models: Genre, Language, Author, Book, BookInstance

from django.contrib import admin
from .models import Author, Book, BookInstance, Genre, Language

# // Inline to add inside different admin_model
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    
class BooksInline(admin.TabularInline):
    # model = Book
    # // many-to-many relationship
    model = Book.author.through
    extra = 3

# p4m2> Advanced configuration of admin site
# // Define AuthorAdmin class, then register Author & AuthorAdmin
class AuthorAdmin(admin.ModelAdmin):
    # // show all authors
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    # // add new author with 3 rows where
    # // 3rd row has 2 columns.
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    # // Error: cuz 'catalog.Book' has no ForeignKey to 'catalog.Author'
    # // I make modify in catalog.Book to have many authors.
    inlines = [BooksInline]
    # pass

admin.site.register(Author, AuthorAdmin)


# // Register Admin classe for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_author', 'display_genre')
    inlines = [BooksInstanceInline]
    # pass

# // Register Admin classe for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    # // p8> adding borrower field
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    
    # // make 2 sets (as section) which includ fields
    fieldsets = (
        (None, {'fields': ('book', 'imprint', 'id')}),
        ('Availability', {'fields': ('status', 'due_back', 'borrower')}),
    )
    # pass


# p4m1> simply register all models with admin site
admin.site.register(Genre)
admin.site.register(Language)
# admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)
