import json
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from .models import OperationRecord, StudentInfo, RegistrationRecord


@csrf_exempt
@require_POST
def register(request):
    """
    数据接收接口（1.0版本保留）
    接收来自小程序的请求，在数据库操作记录表中新增一行数据
    """
    OperationRecord.objects.create(remark='新生报到操作')
    
    return JsonResponse({'success': True, 'message': '报到成功'})


@csrf_exempt
@require_POST
def register_with_info(request):
    """
    提交个人信息 + 报到接口（2.0新增）
    接收前端发送的表单数据（姓名、学号、手机号），先验证字段是否完整，
    再将数据写入学生信息表，最后在报到记录表中生成一条关联的记录
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400)
    
    name = data.get('name', '').strip()
    student_id = data.get('student_id', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name:
        return JsonResponse({
            'success': False,
            'message': '姓名不能为空'
        })
    
    if not student_id:
        return JsonResponse({
            'success': False,
            'message': '学号不能为空'
        })
    
    if not phone:
        return JsonResponse({
            'success': False,
            'message': '手机号不能为空'
        })
    
    if len(phone) != 11 or not phone.isdigit():
        return JsonResponse({
            'success': False,
            'message': '手机号格式不正确'
        })
    
    try:
        student = StudentInfo.objects.create(
            name=name,
            student_id=student_id,
            phone=phone
        )
        
        RegistrationRecord.objects.create(student=student)
        
        return JsonResponse({
            'success': True,
            'message': '报到成功',
            'data': {
                'name': name,
                'student_id': student_id,
                'phone': phone,
                'register_time': student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': '学号已存在，请勿重复报到'
        })


def index(request):
    """
    网页版首页视图
    返回网页版 index.html 文件内容
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(base_dir, '网页版', 'index.html')
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse('网页版文件未找到', status=404, content_type='text/plain; charset=utf-8')
