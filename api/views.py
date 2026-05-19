import json
import os
import random
import re
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.utils import timezone
from .models import OperationRecord, StudentInfo, RegistrationRecord, VerificationCode


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


@csrf_exempt
@require_POST
def send_code(request):
    """
    发送验证码接口（3.0新增）
    接收手机号，生成4位随机验证码，存储到数据库，并在控制台打印
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400)
    
    phone = data.get('phone', '').strip()
    
    # 校验手机号格式
    if not phone:
        return JsonResponse({
            'success': False,
            'message': '手机号不能为空'
        })
    
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return JsonResponse({
            'success': False,
            'message': '手机号格式不正确'
        })
    
    # 检查60秒内是否已经发送过验证码
    sixty_seconds_ago = timezone.now() - timedelta(seconds=60)
    recent_code = VerificationCode.objects.filter(
        phone=phone,
        created_at__gte=sixty_seconds_ago
    ).first()
    
    if recent_code:
        return JsonResponse({
            'success': False,
            'message': '验证码发送过于频繁，请60秒后再试'
        })
    
    # 生成4位随机验证码
    code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    
    # 设置过期时间（5分钟后）
    expires_at = timezone.now() + timedelta(minutes=5)
    
    # 保存到数据库
    VerificationCode.objects.create(
        phone=phone,
        code=code,
        expires_at=expires_at
    )
    
    # 在控制台打印验证码（开发阶段）
    print(f"\n{'='*50}")
    print(f"手机号: {phone}")
    print(f"验证码: {code}")
    print(f"过期时间: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    return JsonResponse({
        'success': True,
        'message': '验证码已发送'
    })


@csrf_exempt
@require_POST
def verify_code(request):
    """
    验证码校验与登录接口（3.0新增）
    校验验证码是否正确，验证通过后建立Session登录状态
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400)
    
    phone = data.get('phone', '').strip()
    code = data.get('code', '').strip()
    
    if not phone or not code:
        return JsonResponse({
            'success': False,
            'message': '手机号和验证码不能为空'
        })
    
    # 查询最新一条未使用的验证码记录
    verification = VerificationCode.objects.filter(
        phone=phone,
        is_used=False,
        expires_at__gt=timezone.now()
    ).order_by('-created_at').first()
    
    if not verification:
        return JsonResponse({
            'success': False,
            'message': '验证码已过期或不存在'
        })
    
    if verification.code != code:
        return JsonResponse({
            'success': False,
            'message': '验证码错误'
        })
    
    # 标记验证码为已使用
    verification.is_used = True
    verification.save()
    
    # 建立Session登录状态
    request.session['verified_phone'] = phone
    request.session['is_logged_in'] = True
    
    return JsonResponse({
        'success': True,
        'message': '登录成功',
        'data': {
            'phone': phone
        }
    })


@csrf_exempt
def check_login(request):
    """
    检查登录状态接口（3.0新增）
    返回当前用户的登录状态
    """
    is_logged_in = request.session.get('is_logged_in', False)
    phone = request.session.get('verified_phone', '')
    
    if is_logged_in and phone:
        return JsonResponse({
            'success': True,
            'is_logged_in': True,
            'phone': phone
        })
    else:
        return JsonResponse({
            'success': True,
            'is_logged_in': False,
            'phone': ''
        })


@csrf_exempt
def logout(request):
    """
    退出登录接口（3.0新增）
    清除Session登录状态
    """
    request.session.flush()
    return JsonResponse({
        'success': True,
        'message': '已退出登录'
    })


@csrf_exempt
@require_POST
def register_with_info_v3(request):
    """
    信息提交与身份证上传接口（3.0新增）
    需要登录状态，从Session获取手机号，接收姓名、学号和身份证照片
    """
    # 检查登录状态
    is_logged_in = request.session.get('is_logged_in', False)
    phone = request.session.get('verified_phone', '')
    
    if not is_logged_in or not phone:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401)
    
    # 获取文本字段
    name = request.POST.get('name', '').strip()
    student_id = request.POST.get('student_id', '').strip()
    
    # 校验文本字段
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
    
    # 获取上传的身份证照片（正反面）
    id_card_photo_front = request.FILES.get('id_card_photo_front')
    id_card_photo_back = request.FILES.get('id_card_photo_back')
    
    if not id_card_photo_front:
        return JsonResponse({
            'success': False,
            'message': '请上传身份证正面照片'
        })
    
    if not id_card_photo_back:
        return JsonResponse({
            'success': False,
            'message': '请上传身份证反面照片'
        })
    
    # 校验图片格式
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    
    if id_card_photo_front.content_type not in allowed_types:
        return JsonResponse({
            'success': False,
            'message': '身份证正面照片格式不支持，请上传 JPG 或 PNG 格式'
        })
    
    if id_card_photo_back.content_type not in allowed_types:
        return JsonResponse({
            'success': False,
            'message': '身份证反面照片格式不支持，请上传 JPG 或 PNG 格式'
        })
    
    # 校验图片大小（5MB = 5 * 1024 * 1024 bytes）
    max_size = 5 * 1024 * 1024
    if id_card_photo_front.size > max_size:
        return JsonResponse({
            'success': False,
            'message': '身份证正面照片大小不能超过5MB'
        })
    
    if id_card_photo_back.size > max_size:
        return JsonResponse({
            'success': False,
            'message': '身份证反面照片大小不能超过5MB'
        })
    
    try:
        # 创建学生信息记录
        student = StudentInfo.objects.create(
            name=name,
            student_id=student_id,
            phone=phone,
            id_card_photo_front=id_card_photo_front,
            id_card_photo_back=id_card_photo_back
        )
        
        # 创建报到记录
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
