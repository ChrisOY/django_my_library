# // p10-1> /catalog/tests/ test_models.py
# // run "python manage.py test" to test this file
# // ie. => python manage.py test catalog.tests.test_models

from django.test import TestCase
from catalog.models import Author

#// Create Tests for models.

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='Bob', last_name='Parker')
    
    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')
        
    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')
        
    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)
        
    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEquals(expected_object_name, str(author))
    
    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')


# // python manage.py test catalog.tests.test_models.MyTestClass
class MyTestClass(TestCase):
    # //classmethod objects to be used as constant that won't need modified.
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to setup non-modified data for all class methods.")
        pass
    
    # // setUp: to run before every testing method.
    # // python manage.py test catalog.tests.test_models.MyTestClass.methodName
    # // eg., catalog.tests.test_models.MyTestClass.setUp
    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass
    
    def test_false_is_false(self):
        print("Method: test_false_is_false")
        self.assertFalse(False)
    
    # // test_for_fail
    def test_false_is_true(self):
        print("Method: test_false_is_true")
        self.assertTrue(False)
        
    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two")
        self.assertEqual(1+1, 2)

