from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "Online Bakery Shop API Running"
    })