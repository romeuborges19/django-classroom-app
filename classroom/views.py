from django.shortcuts import render

# Create your views here.

def classroom_view(request):
    render(request, 'classroom/pages/index.html')
