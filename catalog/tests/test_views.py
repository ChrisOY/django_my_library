# // p10-3> /catalog/tests/ test_views.py
# // p10-3a> Testing AuthorListView
from django.test import TestCase
from django.urls import reverse
from catalog.models import Author

# // p10-3b> Testing Login User Authentication
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from catalog.models import BookInstance, Book, Genre, Language

# // p10-3c> Testing forms
import uuid
from django.contrib.auth.models import Permission


# //=====================================
# // p10-3a> test simple view
# //=====================================
class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # // 13 authors per page
        number_of_authors = 13
        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors-url'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors-url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cat_temp/author_list.html')
        # // FAIL
        # self.assertTemplateUsed(response, 'catalog/cat_temp/author_list.html')
        
    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors-url'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['my_author_list']) == 10)
    
    # // total = 13 authors whcih declared in top of class method
    # // get 2nd page and confirm it has remain 4 items only
    def test_lists_all_authors(self):
        response = self.client.get(reverse('authors-url')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['my_author_list']) == 3) 
        # // False cause 404 (Error) != 200  
        # self.assertTrue(len(response.context['my_author_list']) == 4)

    
# //====================================================
# // p10-3b> test views are restrict to logged in users
# //====================================================
class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0z&3iD')
        test_user1.save()
        test_user2.save()
        
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My Book Summary',
            isbn='ABCDEFG001',
            language=test_language,
            # // Demo is foreignerKey, mine is many2many
            # author=test_author,
        )
        # //ManyToManyField in Book model: Genre & Author
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        author_objects_for_book = Author.objects.all()
        test_book.author.set(author_objects_for_book)
        
        # // create 30 bookinstance objects
        # // testuser1 borrow 15 books
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy%2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Special Imprint 2020',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )
    
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-loan-url'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')
        
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-loan-url'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cat_temp/user_loan.html')    
        
    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-loan-url'))  
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue('loan_books' in response.context)
        # self.assertTrue('bookinstance_list' in response.context)
        
        # // check there's zero in loan list
        self.assertEqual(len(response.context['loan_books']), 0)
        
        # // change 10 books to be loaned
        books = BookInstance.objects.all()[:10]
        for book in books:
            book.status = 'o'
            book.save()
        response = self.client.get(reverse('my-loan-url'))  
        self.assertEqual(str(response.context['user']), 'testuser1')    
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue('loan_books' in response.context)
        # self.assertTrue('bookinstance_list' in response.context)
        
        # confirm all books belong to testuser1 are on loaned
        for bookitem in response.context['loan_books']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)
            
    def test_pages_paginated_to_ten(self):
        # // change all books on loan.
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-loan-url'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['loan_books']), 10)     
            
    def test_pages_ordered_by_due_date(self):
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-loan-url'))  
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        # //AssertionError: 15 != 10
        self.assertEqual(len(response.context['loan_books']), 10)
        
        last_date = 0
        for book in response.context['loan_books']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back
            


# //=================================
# // p10-3c> test views with forms
# //=================================
class RenewBookInstancesTest(TestCase):
    def setUp(self):
        # // create users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0z&3iD')
        test_user1.save()
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()
        
        # // create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My Book Summary',
            isbn='ABCDEFG001',
            language=test_language,
            # // Demo is foreignerKey, mine is many2many
            # author=test_author,
        )
        # //ManyToManyField in Book model: Genre & Author
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        author_objects_for_book = Author.objects.all()
        test_book.author.set(author_objects_for_book)
        test_book.save()
        
        # // create test_user1 bookinstances
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Special Imprint 2020',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )
        
        # // create test_user2 bookinstances
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Special Imprint 2020',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )
          
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}))
        
        # // MUST manaully check redirect. Cannot use assertRedirect
        # // redirect-url is unpredictable
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)
        
    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance2.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        
    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)
        
    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cat_temp/renew_book.html')
        
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        
        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        # // ModelForm field: due_back
        self.assertEqual(response.context['form'].initial['due_back'], date_3_weeks_in_future)
        # // form field: renewal_date
        # self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)
        
    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        # //m2> follow=True to ensure the request returns the final destination home page
        response = self.client.post(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}), {'due_back': valid_date_in_future}, follow=True)
        self.assertRedirects(response, '/catalog/')
        # //m1> 
        # response = self.client.post(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}), {'due_back': valid_date_in_future})
        # self.assertRedirects(response, reverse('all-loan-url'))
    
    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}), {'due_back': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal in past')
    
    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.get(reverse('renew-book-url', kwargs={'pk': self.test_bookinstance1.pk}), {'due_back': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal more than 4 weeks ahead')
        # //console run from above
        # //AssertionError: The field 'due_back' on form 'form' in context 0 contains no errors
        # // m1> RenewBook old method using Form with old_field 'renewal_date'
        # self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')
        # //AssertionError: The form 'form' in context 0 does not contain the field 'renewal_date'


# //=================================
# // p10-x1> challenge
# //================================= 
class AuthorCreateViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0z&3iD')
        test_user1.save()
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-create-url'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/create/')
        
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author-create-url'))
        self.assertEqual(response.status_code, 403)
            
    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('author-create-url'))
        self.assertEqual(response.status_code, 200)
    
    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('author-create-url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cat_temp/form_author.html')
            
    def test_form_date_of_death_initially_set_to_expected_date(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.get(reverse('author-create-url'))
        self.assertEqual(response.status_code, 200)
        
        expected_initial_date = datetime.date(2018, 1, 5)
        response_date = response.context['form'].initial['date_of_death']
        response_date = datetime.datetime.strptime(response_date, "%d/%m/%Y").date()
        self.assertEqual(response_date, expected_initial_date)
        
    def test_redirect_to_detail_view_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0z&3iD')
        response = self.client.post(reverse('author-create-url'), {'first_name': 'Christian Name', 'last_name': 'Surname'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/author/'))
        
    
        
    
    
    