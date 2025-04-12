from django.http import HttpResponse, HttpRequest

# Create your views here.


def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>Welcome to Orchard</h1>")
