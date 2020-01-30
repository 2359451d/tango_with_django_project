from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    about = "<a href='/rango/about/'>About</a>"
    return HttpResponse("Rango says hey there partner!" + about)
    
def about(request):
    index = "<a href='/rango/'>Index</a>"
    return HttpResponse("Rango says here is the about page." + index)