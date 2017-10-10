from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request=request, template_name="main_interface.html")


@csrf_exempt
def search_index(request):

    query = request.GET.get("query_string")

    if not query:
        return HttpResponse(status=500, content="No Query found.")

    print(query)

    return HttpResponse(status=200, content="Testing")
