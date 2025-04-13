from django.http import HttpRequest, HttpResponse

# Create your views here.


def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>Welcome to Orchard</h1>")
