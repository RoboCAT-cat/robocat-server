from django.shortcuts import render

# Create your views here.
def client_view(request, req_path=''):
    return render(request, 'client/index.html')
