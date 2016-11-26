from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def classify(request):
    data = {"success": False}

    if request.method == "POST":
        if request.FILES.get("image", None) is not None:
            image = request.FILES["image"].read()
            # TODO : Add tensorflow method; for now result = -1
            result = -1
            data.update({"success": True, "result": result})

    return JsonResponse(data)
