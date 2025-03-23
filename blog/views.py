from django.views.generic import ListView
from .models import Category
from django.db.models import Count

class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0) 