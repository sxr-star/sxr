import json
import os
import random
import re
from datetime import timedelta
from PIL import Image
import hashlib
import cv2
import numpy as np
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import OperationRecord, StudentInfo, RegistrationRecord, VerificationCode


def get_image_hash(image_file):
    """计算图片的感知哈希值，用于比较两张图片是否相似"""
    try:
        img = Image.open(image_file)
        img = img.convert('L').resize((32, 32), Image.LANCZOS)
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        bits = ''.join('1' if p > avg else '0' for p in pixels)
        return int(bits, 2)
    except Exception:
        return None


def hamming_distance(hash1, hash2):
    """计算两个哈希值的汉明距离"""
    if hash1 is None or hash2 is None:
        return 64
    xor = hash1 ^ hash2
    return bin(xor).count('1')


def images_are_similar(file1, file2, threshold=10):
    """判断两张图片是否相似（汉明距离小于阈值则认为相似）"""
    hash1 = get_image_hash(file1)
    hash2 = get_image_hash(file2)
    
    if hash1 is None or hash2 is None:
        return False
    
    distance = hamming_distance(hash1, hash2)
    return distance < threshold


def get_image_md5(image_file):
    """计算图片的MD5哈希值，用于精确判断是否为同一张图片"""
    try:
        image_file.seek(0)
        md5_hash = hashlib.md5()
        for chunk in image_file.chunks():
            md5_hash.update(chunk)
        image_file.seek(0)
        return md5_hash.hexdigest()
    except Exception:
        return None


def images_are_identical(file1, file2):
    """判断两张图片是否完全相同（通过MD5哈希值）"""
    md5_1 = get_image_md5(file1)
    md5_2 = get_image_md5(file2)
    
    if md5_1 is None or md5_2 is None:
        return False
    
    return md5_1 == md5_2


def identify_id_card_side(image_file):
    """
    识别身份证是正面（人像面）还是反面（国徽面）
    返回: 'front' 表示正面，'back' 表示反面，'unknown' 表示无法识别
    
    识别策略：
    1. 正面特征：人脸区域、蓝色文字
    2. 反面特征：国徽图案（红色）、"居民身份证"文字
    """
    try:
        # 读取图片
        image_file.seek(0)
        img_array = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return 'unknown'
        
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 检测蓝色区域（正面特征 - 蓝色文字）
        lower_blue = np.array([100, 40, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_ratio = np.sum(blue_mask > 0) / (img.shape[0] * img.shape[1])
        
        # 检测人脸区域（正面特征）
        # 使用肤色检测
        lower_skin = np.array([0, 15, 100], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # 应用形态学操作去除噪声
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        
        # 查找人脸区域（较大的连通区域）
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        has_face = False
        max_face_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            # 人脸区域应该占图像的3%-25%
            if area > (img.shape[0] * img.shape[1] * 0.03) and area < (img.shape[0] * img.shape[1] * 0.25):
                has_face = True
                max_face_area = max(max_face_area, area)
        
        # 检测红色区域（国徽特征，反面）
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_ratio = np.sum(red_mask > 0) / (img.shape[0] * img.shape[1])
        
        # 综合判断
        # 正面：有人脸区域 或 蓝色文字区域明显
        # 反面：红色国徽区域明显 且 无人脸
        if has_face:
            return 'front'
        elif blue_ratio > 0.02:
            return 'front'
        elif red_ratio > 0.01 and not has_face:
            return 'back'
        else:
            # 默认返回反面（保守策略）
            return 'back'
            
    except Exception as e:
        print(f"身份证正反面识别失败: {e}")
        return 'unknown'


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
    
    # 校验正反面照片是否为同一张图片（先精确匹配，再相似度匹配）
    if images_are_identical(id_card_photo_front, id_card_photo_back):
        return JsonResponse({
            'success': False,
            'message': '身份证正面和反面照片不能为同一张图片，请重新上传'
        })
    
    if images_are_similar(id_card_photo_front, id_card_photo_back):
        return JsonResponse({
            'success': False,
            'message': '身份证正面和反面照片高度相似，请确保上传的是不同的两面'
        })
    
    # 自动识别身份证正反面
    id_card_photo_front.seek(0)
    id_card_photo_back.seek(0)
    
    front_side = identify_id_card_side(id_card_photo_front)
    back_side = identify_id_card_side(id_card_photo_back)
    
    # 重置文件指针
    id_card_photo_front.seek(0)
    id_card_photo_back.seek(0)
    
    # 如果识别成功，检查用户上传的是否正确
    if front_side == 'back' and back_side == 'front':
        # 用户上传反了，交换两张图片
        id_card_photo_front, id_card_photo_back = id_card_photo_back, id_card_photo_front
    elif front_side == 'back' and back_side == 'back':
        return JsonResponse({
            'success': False,
            'message': '未检测到身份证正面照片（带人像的一面），请检查后重新上传'
        })
    elif front_side == 'front' and back_side == 'front':
        return JsonResponse({
            'success': False,
            'message': '未检测到身份证反面照片（带国徽的一面），请检查后重新上传'
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
