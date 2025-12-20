from django.http import JsonResponse
from .models import Task,Status
from django.views.decorators.csrf import csrf_exempt
import json

def task_list(request):
    tasks = Task.objects.all()
    data = []
    for task in tasks:
        data.append({
            'id': task.id,
            'title': task.title,
            'status': task.get_status_display(),  # 可读状态
        })
    return JsonResponse(data, safe=False)
@csrf_exempt
def create(request):
    if(request.method=="POST"):
        try:
            data=json.loads(request.body)
            print(f"Received data: {data}")
            name=data.get('name')
            status=data.get('status',Status.UNSTARTED)
            # 创建任务
            task = Task.objects.create(
                name=name,
                status=status
            )
            return JsonResponse({
                'id': task.id,
                'name': task.name,
                'status': task.get_status_display(),
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=403)