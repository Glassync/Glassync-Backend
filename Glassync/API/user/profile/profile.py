from django.http import JsonResponse


def get(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)


def update(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)


def delete(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)
