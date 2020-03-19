from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from rango.google_search import run_google_search
from django.views import View
from django.utils.decorators import method_decorator


class SearchAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']
        
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found.')
        except ValueError:
            return HttpResponse('Error - bad category ID.')
        
        p = Page.objects.get_or_create(category=category,title=title,url=url)
        pages = Page.objects.filter(category=category).order_by('-views')
        return render(request, 'rango/page_listing.html', {'pages': pages})

def get_category_list(max_results=0, starts_with=""):
    """ 
    optimise static search functionality
    return a list of categories match the user query<starts_with> ---> query results
    helper method for CateforySuggestionView
    """
    category_list = []

    if starts_with:
    # using the filter method to return a filtered set within all the categories
        category_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results]
    return category_list

class CateforySuggestionView(View):
    # /rango/suggest/
    """ 
    take user query(suggestion), return top 8 results
    suggestion - > user query input
    """
    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''
        
        # acquire the filetered categories
        category_list = get_category_list(max_results=8,
        starts_with=suggestion)
        if len(category_list) == 0:
            # no query results , default displaying all the category(after ranked)
            category_list = Category.objects.order_by('-likes')
            
        return render(request,'rango/categories.html',{'categories': category_list})


class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        context_dict = {}
        # exam the request.GET dict,pick out the category
        # /rango/like_category/?category_id=1
        category_id = request.GET.get('category_id')
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)

        category.likes = category.likes+1
        category.save()
        # do not render the entire page, using ajax
        return HttpResponse(category.likes)

class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()
        return render(request,
        'rango/list_profiles.html',
        {'user_profile_list': profiles})

class ProfileView(View):
    # avoid repeating [DRY]
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        # current seleted detailed form
        form = UserProfileForm({'website': user_profile.website,'picture': user_profile.picture})
        return (user, user_profile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        # username from url, paramised view
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        context_dict = {'user_profile': user_profile,
        'selected_user': user,
        'form': form}
        return render(request, 'rango/profile.html', context_dict)
    
    # update profile
    @method_decorator(login_required)
    def post(self, request, username):
         # username from url, paramised view
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            # refresh the form and commit 
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)
            # return old details
            context_dict = {'user_profile': user_profile,
            'selected_user': user,
            'form': form}
            return render(request, 'rango/profile.html', context_dict)

class RegisterProfile(View):
    @method_decorator(login_required)
    def post(self,request):
        context_dict = {}
        form = UserProfileForm()
        form = UserProfileForm(request.POST, request.FILES)
        # check whether all the form fields are filled correctly
        if form.is_valid():
            # give the time to manipulate the new instance before commiting
            user_profile = form.save(commit=False)
            # refresh current user
            user_profile.user = request.user
            user_profile.save()
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

        context_dict = {'form':form}
        return render(request, 'rango/profile_registration.html', context_dict)
    
    @method_decorator(login_required)
    def get(self,request):
        form = UserProfileForm()
        context_dict = {'form':form}
        return render(request, 'rango/profile_registration.html', context_dict)

@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        # check whether all the form fields are filled correctly
        if form.is_valid():
            # give the time to manipulate the new instance before commiting
            user_profile = form.save(commit=False)
            # refresh current user
            user_profile.user = request.user
            user_profile.save()
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    
    # GET, a blank form to fill out
    context_dict = {'form':form}
    return render(request, 'rango/profile_registration.html', context_dict)

    # # capture details of USerProfile instance
    # # for rendering
    # # user = UserProfile
    # context_dict = {}
    # context_dict['name'] = request.user
    # try:
    #     user = UserProfile.objects.get(id=request.user.id)
    #     context_dict['url'] = user.website
    #     context_dict['img'] = user.picture
    # except:
    #     context_dict['url'] = None
    #     context_dict['img'] = None

    # all_user = UserProfile.objects.all()
    # context_dict['all'] = all_user
    # return render(request,"rango/profile.html",context_dict)


    context_dict = {}
    context_dict['name'] = user
    try:
        user = UserProfile.objects.get(id=user.id)
        context_dict['url'] = user.website
        context_dict['img'] = user.picture
    except:
        context_dict['url'] = None
        context_dict['img'] = None

    all_user = UserProfile.objects.all()
    context_dict['all'] = all_user
    print("all",context_dict)

    return render(request,"rango/showp.html",context = context_dict)

class GoToUrl(View):

    def get(self, request):
        page_id = None
        page_id = request.GET.get('page_id')
        try:
            # pick the page
            page = Page.objects.get(id=page_id)

            # Unknown page
            if page==None:
                return redirect(reverse('rango:index'))
            
            # increment the views field of this page, and save
            page.views = page.views + 1
            page.save()
        except:
            return redirect(reverse('rango:index'))
        return redirect(page.url)

def goto_url(request):
    page_id = None
    if request.method == 'GET':
        page_id = request.GET.get('page_id')
        try:
            # pick the page
            page = Page.objects.get(id=page_id)

            # Unknown page
            if page==None:
                return redirect(reverse('rango:index'))
            
            # increment the views field of this page, and save
            page.views = page.views + 1
            page.save()
        except:
            return redirect(reverse('rango:index'))
        return redirect(page.url)

def search(request):
    result_list = []
    query = ""
    if request.method == 'POST':
        # search engine selection
        selection = request.POST['search-selection']
        print(selection)
        # user query string
        query = request.POST['query'].strip()
        if query:
            if selection == "Bing":
                # run our bing func to get the results list
                result_list = run_query(query)
            else:
                result_list = run_google_search(query)

    return render(request, 'rango/search.html', {'result_list': result_list,'query':query})

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


# Updated the function definition
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits

class IndexView(View):
    def get(self,request):
        category_list = Category.objects.order_by('-likes')[:5]
        page_list = Page.objects.order_by('-views')[:5]
        context_dict = {}
        context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
        context_dict['categories'] = category_list
        context_dict['pages'] = page_list

        visitor_cookie_handler(request)
        return render(request, 'rango/index.html', context=context_dict)

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

    visitor_cookie_handler(request)
    return render(request, 'rango/index.html', context=context_dict)

class AboutView(View):
    def get(self, request):
        context_dict = {}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        return render(request,'rango/about.html',context_dict)

def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Yao Du.'}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    return render(request, 'rango/about.html', context=context_dict)

class ShowCategoryView(View):
    def create_context_dict(self, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category)
            context_dict['pages'] = pages.order_by('-views')
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['pages'] = None      
            context_dict['category'] = None
            context_dict['result_list'] = None
        return context_dict

    def get(self, request, category_name_slug):
        search_engine = request.GET.get('search_engine',False)
        query = request.GET.get('query',False)
        context_dict = self.create_context_dict(category_name_slug)
        # print(query)
        # print(search_engine)
        if search_engine == "site":
            try:
                if query:
                    pages_query = []
                    category_query = Category.objects.filter(slug__istartswith=query)
                    for each in category_query:
                        pages_set = Page.objects.filter(category=each)
                        for p in pages_set:
                            pages_query.append(p)

                    context_dict['category_query'] = category_query
                    context_dict['pages_query'] = pages_query
                    return HttpResponse("1")
                    
            except Category.DoesNotExist:
                # cannot find , .get() raise DoesNotExist exception.
                #display nothing
                context_dict['static_list'] = None
        elif search_engine == "bing":
            # search engine selection
            # user query string
            if query:
                context_dict = self.create_context_dict(category_name_slug)
                context_dict['result_list'] = run_query(query)
            # print(context_dict['result_list'])
            return HttpResponse("1")
        
        return render(request, 'rango/category.html', context_dict)

    def post(self, request, category_name_slug):
        
        search_engine = request.POST['search_engine'].strip()
        context_dict = self.create_context_dict(category_name_slug)
        query = request.POST['query'].strip()
        if search_engine == "site":
            try:
                if query:
                    pages_query = []
                    category_query = Category.objects.filter(slug__istartswith=query)
                    for each in category_query:
                        pages_set = Page.objects.filter(category=each)
                        for p in pages_set:
                            pages_query.append(p)

                    context_dict['category_query'] = category_query
                    context_dict['pages_query'] = pages_query
                    
            except Category.DoesNotExist:
                # cannot find , .get() raise DoesNotExist exception.
                #display nothing
                context_dict['static_list'] = None
        elif search_engine == "bing":
            # search engine selection
            # user query string
            if query:
                context_dict = self.create_context_dict(category_name_slug)
                context_dict['result_list'] = run_query(query)

        return render(request, 'rango/category.html', context_dict)

def show_category(request, category_name_slug):
    # deal with requested passed 'category_name_slug'
    context_dict = {}

    try:
        if request.method == "POST":
            query = request.POST['query'].strip()
            print(query)
            if query:
                category_query = Category.objects.get(slug=query)
                pages_query = Page.objects.filter(category=category_query)
                result_list = [{'category_query':category_query,'pages_query':pages_query}]
                context_dict['result_list'] = result_list
        
        #if find a category name slug with given varaible

        #.get() returns 1 category model instance
        category = Category.objects.get(slug=category_name_slug)
        #return related pages, attribute of page is the one in url

        pages = Page.objects.filter(category=category)
        #add the results ready to be render into templates context
        context_dict['pages'] = pages.order_by('-views')
        context_dict['category'] = category
    except Category.DoesNotExist:
        # cannot find , .get() raise DoesNotExist exception.
        #display nothing
        context_dict['pages'] = None      
        context_dict['category'] = None
        context_dict['result_list'] = None

    #render the response and return it to the client
    return render(request, 'rango/category.html', context=context_dict)

# class-based view: add category
class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self,request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form':form})

    @method_decorator(login_required)
    def post(self,request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        return render(request, 'rango/add_category.html', {'form':form})

@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            # return redirect('/rango/')
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form':form})

class AddPage(View):
    def get_category(self, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None
        return category
    
    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        form = PageForm()
        category = self.get_category(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))

        context_dict = {'form':form, 'category': category}
        return render(request, 'rango/add_page.html', context = context_dict)

    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        category = self.get_category(category_name_slug)
        if category is None:
            return redirect(reverse('rango:index'))

        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
        else:
            print(form.errors)
    
        context_dict = {'form':form, 'category': category}
        return render(request, 'rango/add_page.html', context = context_dict)

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    #cannot find the specific Category
    if category is None:
        # return redirect('/rango/')
        return redirect(reverse('rango:index'))
    #initialise the form
    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)
    
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context = context_dict)



# def register(request):
#     #a boolean value for telling the template
#     # whether the registration is successful
#     # initially  false, when succeeds true.
#     registered = False

#     # POST, handle the form data
#     if request.method == "POST":
#         # try to grab information from the raw form information
#         # note that, we use both UserForm & UserProFileForm(additional attributes)
#         user_form = UserForm(request.POST)
#         profile_form = UserProfileForm(request.POST)

#         # check whether the form data is valid
#         if user_form.is_valid() and profile_form.is_valid():
#             # save the UserForm data into database
#             user = user_form.save()

#             # Note that using the hasher to set password
#             # And update the user instance
#             user.set_password(user.password)
#             user.save()

#             # handle the UserProfile instance
#             # we need to set the user attribute ourselves(self-defined)
#             #we set commit = False, to <delay> the save(iniitially no user instance)
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             # if user provide the icon
#             # get it from the input form then put it into UserProfile mdoel
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
            
#             #save the UserProfile(Form to database) model instance
#             profile.save()

#             # tells the teplates, registration finished
#             registered = True
#         else:
#             # invalid forms data
#             # print problems to the terminal
#             print(user_form.errors, profile_form.errors)
#     else:
#         # not HTTP POST(maybe get HttpRequest)
#         # so provide&tender the blank form for user
#         user_form = UserForm()
#         profile_form = UserProfileForm()

#     # Render the template
#     return render(request,'rango/register.html',context={'user_form':user_form,
#     'profile_form':profile_form,'registered':registered})

# def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check whether the combination is valid
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('rango:index'))
            else:
                # inactive account was used
                return HttpResponse("Your Rango account is disabled.")
        else:
            # bad login details ,cannot log the user in
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        #HTTP GET
        return render(request,'rango/login.html')


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

# @login_required
# def user_logout(request):
#     logout(request)
#     return redirect(reverse('rango:index'))
