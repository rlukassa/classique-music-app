from django.shortcuts import render, redirect

# Create your views here.

def home(request): # Landing page
    return render(request, "landing/home.html")

def uploadPage(request): # Path menuju halaman upload datasets
    return render(request, "landing/uploadPage.html")