from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    return render(request, 'rango/index.html', context=context_dict)
    
def about(request):
    name_dict = {'name': 'Yao Du'}
    return render(request, 'rango/about.html',context=name_dict)

def show_category(request, category_name_slug):
    # deal with requested passed 'category_name_slug'
    context_dict = {}

    try:
        #if find a category name slug with given varaible

        #.get() returns 1 category model instance
        category = Category.objects.get(slug=category_name_slug)
        #return related pages, attribute of page is the one in url

        pages = Page.objects.filter(category=category)

        #add the results ready to be render into templates context
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        # cannot find , .get() raise DoesNotExist exception.
        #display nothing

        context_dict['pages'] = None      
        context_dict['category'] = None
    
    #render the response and return it to the client
    return render(request, 'rango/category.html', context=context_dict)