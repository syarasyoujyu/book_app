from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView,CreateView,DeleteView
from django.views.generic.edit import UpdateView
from .models import Book,Review
from django.core.exceptions import PermissionDenied,ValidationError
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg,Count
from django.core.paginator import Paginator
from .consts import ITEM_PER_PAGE
from copy import deepcopy

############# View Books #######################
class ListBookView(LoginRequiredMixin,ListView):
    template_name="book/book_list.html"
    model=Book
    paginate_by=ITEM_PER_PAGE

    def get_queryset(self,**kwargs):
        queryset = super().get_queryset(**kwargs)
        query = self.request.GET

        q=query.get('q')
        if q:
            queryset = queryset.filter(title__icontains=q)

        return queryset.order_by('title')
# Create your views here.
    
############# Show Detail of a Book #######################
class DetailBookView(LoginRequiredMixin,DetailView):
    template_NAME ="book/book_detail.html"
    model=Book

############# Create Book #######################
class CreateBookView(LoginRequiredMixin,CreateView):
    template_name="book/book_create.html"
    model=Book
    fields={"title","text","category","thumbnail"}
    success_url=reverse_lazy("list-book")
    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)

############# Delete User's Book #######################
class DeleteBookView(LoginRequiredMixin,DeleteView):
    template_name="book/book_delete.html"
    model=Book
    success_url=reverse_lazy("list-book")
    def get_object(self,queryset=None):
        obj=super().get_object(queryset)
        if obj.user !=self.request.user:
            raise PermissionDenied
        return obj
    
############# Edit books of user #######################
class UpdateBookView(LoginRequiredMixin,UpdateView):
    model=Book
    template_name="book/book_update.html"
    fields={"title","text","category","thumbnail"}
    success_url=reverse_lazy("list-book")
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context["user_now"]=self.request.user
        return context
    def get_success_url(self):
        return reverse('detail-book',kwargs={'pk':self.object.id})
    

############# View  Books and Ranking #######################
def index_view(request):
    object_list=Book.objects.all().order_by('-id')
    ranking_list=Book.objects.annotate(avg_rating=Avg('review__rate'),review_num=Count('review')).order_by('-avg_rating')
    paginator=Paginator(ranking_list,ITEM_PER_PAGE)
    page_number=request.GET.get('page',1)
    page_obj=paginator.page(page_number)
    return render(request,"book/index.html",{'object_list':object_list,'ranking_list':ranking_list,'page_obj':page_obj,'page_number':page_number,'fr':ITEM_PER_PAGE*(int(page_number)-1)+1,'to':ITEM_PER_PAGE*(int(page_number)-1)+len(page_obj)})


#############Create Review#######################
class CreateReviewView(LoginRequiredMixin,CreateView):
    model=Review
    fields=('book','title','text','rate')
    templae_name="book/review_form.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context["book"]=Book.objects.get(pk=self.kwargs['book_id'])
        context["user_now"]=self.request.user
        reviewers=[]
        for t in Review.objects.all():
            if t.book == context["book"]:
                name=t.user.id
                reviewers.append(name)
        context["reviewers"]=reviewers
        print(context["user_now"].id in reviewers)
        print(reviewers,context["user_now"].id,context["book"].user)
        return context
    
    def form_valid(self,form):
        form.instance.user =self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('detail-book',kwargs={'pk':self.object.book.id})
