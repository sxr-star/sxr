from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import OperationRecord
import os


def index(request):
    """
    网页版首页
    """
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '网页版', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return HttpResponse(f.read())


@csrf_exempt
@require_POST
def register(request):
    """
    数据接收接口
    接收来自小程序的请求，在数据库操作记录表中新增一行数据
    """
    OperationRecord.objects.create(remark='新生报到操作')
    
    return JsonResponse({'success': True, 'message': '报到成功'})
