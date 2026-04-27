from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import OperationRecord


@csrf_exempt
@require_POST
def register(request):
    """
    数据接收接口
    接收来自小程序的请求，在数据库操作记录表中新增一行数据
    """
    OperationRecord.objects.create(remark='新生报到操作')
    
    return JsonResponse({'success': True, 'message': '报到成功'})
