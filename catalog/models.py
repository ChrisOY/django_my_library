# // catalog/models.py
# // 5 models: Genre, Language, Author, Book, BookInstance

from django.db import models
from django.urls import reverse

# //p8> for user to borrow books
from django.contrib.auth.models import User

# // For unique book instances
import uuid
from datetime import date


# // a book Gernre model //
class Genre(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction')
    # // alphabetically by name a-z
    class Meta:
        ordering = ['name']
    # // String to represent model object in Admin_site
    def __str__(self):
        return self.name
    
class Language(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a book natural language (e.g. English, French, Japanese etc.')
    # // It's not working for default value
    # name = models.CharField(max_length=200, help_text='Enter a book natural language (e.g. English, French, Japanese etc.', default='English')
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
    

# // a author can have many books
class Author(models.Model):
    # //Fields: ea field is header of column in table
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    
    # //Metadata: control how the data is stored or used
    class Meta:
        ordering = ['last_name', 'first_name']
    
    # //Methods: 
    def get_absolute_url(self):
        return reverse('author-detail-url', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


# // represent for book model (might have 2 copied)  
class Book(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Characters <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    
    # // 1(language)-to-many(books) & 1(book)-to-1(native-language)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    
    # // String ('Author') means not an object/model.
    # author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    # // should named as 'authors' since many-authors
    author = models.ManyToManyField(Author, help_text='Select author/authors for this book')
    def display_author(self):
        return ', '.join([author.last_name for author in self.author.all()[:3]])
    display_author.short_description = 'Author'
    
     # //p6> to display All authors in book_list.html 
     # // it's a string, not object
    def display_all_authors(self):
        return ', '.join([f'{author.first_name} {author.last_name}' for author in self.author.all()])
    
                         
    genre = models.ManyToManyField(Genre, help_text='Select genre/genres for this book')
    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
    display_genre.short_description = 'Genre'
      
    def get_absolute_url(self):
        return reverse('book-detail-url', args=[str(self.id)])
    
    def __str__(self):
        return self.title
    

# // represent a specific copy of a book (a book might have few copies) //    
class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    # //p8> add field that is 1(user)-to-many(bookinstances)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # //p8> duedate for borrower's record
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False
    
    # // choices for enumeration switch-case
    LOAN_STATUS = ( 
        ('m', 'Maintenance'),
        ('o', 'On Loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')
    
    class Meta:
        ordering = ['due_back']
        # // p8> must has comma after 1st permission
        # // otherwise will show error: ValueError: too many values to unpack (expected 2)
        permissions = (("can_mark_returned", "Set book as returned"),)
        
    def __str__(self):
        # return '{0} ({1})'.format(self.id, self.book.title)
        return f'{self.id} ({self.book.title})'
        
    
    
    
    
    
    
    