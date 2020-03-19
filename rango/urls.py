from django.urls import path
from rango import views
from rango.views import AboutView, AddCategoryView, IndexView, ShowCategoryView, RegisterProfile, GoToUrl, AddPage, ProfileView, ListProfilesView

app_name = 'rango'
LOGIN_URL = 'rango:login'

urlpatterns = [
    path('',views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('category/<slug:category_name_slug>/', views.ShowCategoryView.as_view(), name='show_category'),
    path('add_category/', views.AddCategoryView.as_view(), name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', AddPage.as_view(), name='add_page'),
    path('search/', views.search, name='search'),
    path('goto/', views.GoToUrl.as_view(), name='goto'),
    path('register_profile/', views.RegisterProfile.as_view(), name='register_profile'),
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    # path('register/', views.register, name='register'),
    # path('login/', views.user_login,name='login'),
    path('restricted/', views.restricted, name='restricted'),
    # path('logout/', views.user_logout, name='logout'),
]