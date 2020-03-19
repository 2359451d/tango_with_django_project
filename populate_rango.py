import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
 'tango_with_django_project.settings')

import django
django.setup()
from rango.models import Category, Page

def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    python_pages = [
        {'title': 'Official Python Tutorial',
            'url': 'http://docs.python.org/3/tutorial/','views':1000},

        {'title': 'How to Think like a Computer Scientist',
            'url': 'http://www.greenteapress.com/thinkpython/','views':251},
        {'title': 'Learn Python in 10 Minutes',
            'url': 'http://www.korokithakis.net/tutorials/python/', 'views':159}
    ]


    django_pages = [
        {'title': 'Official Django Tutorial',
            'url': 'https://docs.djangoproject.com/en/2.1/intro/tutorial01/','views':152},
        {'title': 'Django Rocks',
            'url': 'http://www.djangorocks.com','views':5},
        {'title': 'How to Tango with Django',
            'url': 'http://www.tangowithdjango.com/','views':18}
    ]

    other_pages = [
        {'title':'Bottle',
            'url':'http://bottlepy.org/docs/dev/','views':10},
        {'title':'Flask',
            'url':'http://flask.pocoo.org','views':17} ]
    
    pascal_pages = [
        {'title':'Pascal Tutorial',
            'url':'https://www.tutorialspoint.com/pascal/index.htm','views':10}
    ] 
    perl_pages = [
        {'title':"Beginner's Introduction to Perl",
            'url':'https://www.perl.com/pub/2000/10/begperl1.html/','views':20}
    ] 
    php_pages = [
        {'title':'PHP Tutorial',
            'url':'https://www.w3schools.com/PHP/DEfaULT.asP','views':15},
    ] 
    prolog_pages = [
        {'title':'A Short Tutorial on Prolog',
            'url':'https://www.doc.gold.ac.uk/~mas02gw/prolog_tutorial/prologpages/','views':12},
    ] 
    postscript_pages = [
        {'title':'Postscript Books',
            'url':'https://www.psbooks.co.uk/','views':100}
    ] 
    programming_pages = [
        {'title':'7 Essential Books for Programmers',
            'url':'https://medium.com/better-programming/7-essential-books-for-programmers-869bca83b360','views':100}
    ] 


    cats = {'Python': {'pages': python_pages, 'views':128, 'likes':64},
        'Django': {'pages': django_pages,'views':64,'likes':32},
        'Other Frameworks': {'pages': other_pages,'views':32,'likes':16},
        'Pascal': {'pages': pascal_pages,'views':52,'likes':1},
        'Perl': {'pages': perl_pages,'views':22,'likes':12},
        'PHP': {'pages': php_pages,'views':32,'likes':14},
        'Prolog': {'pages': prolog_pages,'views':32,'likes':11},
        'PostScript': {'pages': postscript_pages,'views':62,'likes':12},
        'Programming': {'pages': programming_pages,'views':82,'likes':1},
        }

    # If you want to add more categories or pages,
    # add them to the dictionaries above.

    # The code below goes through the cats dictionary, then adds each category,
    # and then adds all the associated pages for that category.
    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data['views'], cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'], p['views'])

    # Print out the categories we have added.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f'- {c}: {p}')

def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p

def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c

# Start execution here!
if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
