# // /catalog/views.py

# //p5> create view for home page
from django.shortcuts import render
from catalog.models import Author, Book, BookInstance, Genre

# //p6> create html views
from django.views import generic
# //p8> only login user can see the view
from django.contrib.auth.mixins import LoginRequiredMixin
# //p8-challenge>
from django.contrib.auth.mixins import PermissionRequiredMixin

# //p9-1> renewbook permission
import datetime
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm, RenewBookModelForm

# //p9-2> edit renew books
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy



# // p5: create home page of site
def index(request):
    num_authors = Author.objects.all().count()
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_genre = Genre.objects.all().count()
    num_mystery_book = Book.objects.filter(genre__name='Mystery').count()
    num_novel_book = Book.objects.filter(genre__name='Novel').count()
    num_sci_book = Book.objects.filter(genre__name='Science & Math').count()
    
    # // p7> counting sessions & record as cookies
    # // change key_name, will recount the cookie/sessions
    num_visits_counts = request.session.get('num_visits_key', 0)
    request.session['num_visits_key'] = num_visits_counts + 1
    
    context = {
        'num_visits': num_visits_counts,
        
        'num_authors': num_authors,
        'num_books': num_books,
        'num_instances': num_instances,
        'num_inst_available': num_instances_available,
        'num_genre': num_genre,
        'num_mystery': num_mystery_book,
        'num_novel': num_novel_book,
        'num_sci': num_sci_book,
    }
    
    return render(request, 'cat_temp/index.html', context=context)
    

# // p6-1: create List view
class BookListView(generic.ListView):
    model = Book
    # // name to link with html
    template_name = 'cat_temp/book_list.html'
    # // name of this view to be used in html source code
    # // by defualt, it is 'book'
    context_object_name = 'my_book_list'
    paginate_by = 10

    # get 5 specific book title with chemistry
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='chemistry')[:5]
    # to override the method use get_queryset
    # queryset = Book.objects.filter(title__icontains='chemistry')[:5]
class AuthorListView(generic.ListView):
    model = Author
    template_name = 'cat_temp/author_list.html'
    context_object_name = 'my_author_list'
    paginate_by = 10
    
    
# // p6-2: create Detail view  
# // error cuz it's belogn to DetailView
# class BookDetailView(generic.ListView):
class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'cat_temp/book_detail.html'
    context_object_name = 'select_book'
    

# class AuthorDetailView(generic.ListView):
# // error cuz it's belogn to DetailView
class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'cat_temp/author_detail.html'
    context_object_name = 'select_author'
    

# // VIP: LoginRequiredMinxin put before generic.ListView;
# class LoanedBooksByUserListView(generic.ListView, LoginRequiredMixin):
# // else will show TypeError ~~~~
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'cat_temp/user_loan.html'
    context_object_name = 'loan_books'
    paginate_by = 10
    
    def get_queryset(self):
        # // crash for filter borrower
        # //TypeError: 'AnonymousUser' object is not iterable
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


# m1> class AllLoanedBooksView(generic.ListView): 
# // p8challenge> to use permission
class AllLoanedBooksView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'cat_temp/users_loan_all.html'
    context_object_name = 'loan_books'
    paginate_by = 10
    # // all-loaned-books only visible to user who has permission
    permission_required = 'catalog.can_mark_returned'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


# // p9-1> need to have permission to renew book
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    # // m2> RenewBookModelForm(ModelForm)
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-loan-url'))
    else:
        proposed_renewal_date = datetime.date.today()+datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})
    
    # // m1> RenewBookForm(forms.Form)
    # if request.method == 'POST':
    #     form = RenewBookForm(request.POST)
    #     if form.is_valid():
    #         book_instance.due_back = form.cleaned_data['renewal_date']
    #         book_instance.save()
    #         return HttpResponseRedirect(reverse('all-loan-url'))
    # else:
    #     proposed_renewal_date = datetime.date.today()+datetime.timedelta(weeks=3)
    #     form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    
    return render(request, 'cat_temp/renew_book.html', context)
    

# // p9-2a> create/edit/delete author records
# m1> class AuthorCreate(CreateView):
# // challenge to get author create/update/delete with special permission
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    success_url = reverse_lazy('authors-url')
    template_name = 'cat_temp/form_author.html'
    # initial = {'date_of_death': '01/31/2120'}
    permission_required = 'catalog.can_mark_returned'
    
class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'cat_temp/form_author.html'
    permission_required = 'catalog.can_mark_returned'
    
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    template_name = 'cat_temp/confirm_delete_author.html'
    success_url = reverse_lazy('authors-url')
    permission_required = 'catalog.can_mark_returned'
    
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books-url')
    template_name = 'cat_temp/form_book.html'
    ermission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    template_name = 'cat_temp/form_book.html'
    permission_required = 'catalog.can_mark_returned'
    
class BookDelete(PermissionRequiredMixin, UpdateView):
    model = Book
    template_name = 'cat_temp/confirm_delete_book.html'
    success_url = reverse_lazy('books-url')
    permission_required = 'catalog.can_mark_returned'





# from django.shortcuts import get_object_or_404
# def book_detail_view(request, primary_key):
#     # m2> django framework
#     book = get_object_or_404(Book, pk=primary_key)
#     return render(request, 'cat_temp/book_detail.html', context={'book': book}) 
    # m1> try-except
    # try:
    #     book = Book.objects.get(pk=primary_key)
    # except Book.DoesNotExist:
    #     raise Http404('Book does not exist')
    # return render(request, 'cat_temp/book_detail.html', context={'book': book})  
