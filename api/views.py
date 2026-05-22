import json
import os
import random
import re
import base64
from io import BytesIO
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
from .models import OperationRecord, StudentInfo, RegistrationRecord, VerificationCode, Dormitory


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


def base64_to_image(base64_string, filename='image.jpg'):
    """将base64编码的图片转换为InMemoryUploadedFile"""
    try:
        # 解码base64
        image_data = base64.b64decode(base64_string)
        # 创建BytesIO对象
        image_io = BytesIO(image_data)
        # 获取文件大小
        file_size = len(image_data)
        # 获取文件类型
        if base64_string.startswith('/9j/'):
            content_type = 'image/jpeg'
            if not filename.lower().endswith('.jpg'):
                filename = filename.rsplit('.', 1)[0] + '.jpg'
        elif base64_string.startswith('iVBOR'):
            content_type = 'image/png'
            if not filename.lower().endswith('.png'):
                filename = filename.rsplit('.', 1)[0] + '.png'
        else:
            content_type = 'image/jpeg'

        # 创建InMemoryUploadedFile
        image_file = InMemoryUploadedFile(
            image_io,
            None,
            filename,
            content_type,
            file_size,
            None
        )
        return image_file
    except Exception as e:
        print(f"base64转换失败: {e}")
        return None


@csrf_exempt
def register_with_info_v3(request):
    """
    信息提交与身份证上传接口（3.0新增，4.0支持小程序分次上传）
    需要登录状态，从Session获取手机号，接收姓名、学号和身份证照片

    小程序分次上传流程：
    1. 第一次上传：正面照片 + 姓名 + 学号
    2. 第二次上传：反面照片 + 姓名 + 学号
    两次请求使用相同的姓名和学号，后端通过Session临时存储第一张照片

    网页版同时上传：
    - id_card_photo_front：正面照片
    - id_card_photo_back：反面照片
    - name：姓名
    - student_id：学号
    """
    # 检查登录状态（支持Session和请求头两种方式）
    is_logged_in = request.session.get('is_logged_in', False)
    phone = request.session.get('verified_phone', '')

    # 如果Session中没有登录信息，尝试从请求头获取
    if not is_logged_in or not phone:
        phone_from_header = request.META.get('HTTP_X_VERIFIED_PHONE', '')
        if phone_from_header:
            # 验证手机号是否已经通过验证码验证（检查最近的验证码记录）
            recent_code = VerificationCode.objects.filter(
                phone=phone_from_header,
                is_used=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).first()
            if recent_code:
                phone = phone_from_header
                is_logged_in = True

    if not is_logged_in or not phone:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401)

    # 获取数据（支持JSON和表单两种格式）
    try:
        data = json.loads(request.body) if request.body else {}
    except:
        data = {}

    # 获取文本字段（优先从JSON，然后从POST）
    name = data.get('name', '').strip() or request.POST.get('name', '').strip()
    student_id = data.get('student_id', '').strip() or request.POST.get('student_id', '').strip()

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

    # 获取上传的身份证照片
    id_card_photo_front = request.FILES.get('id_card_photo_front')
    id_card_photo_back = request.FILES.get('id_card_photo_back')

    # 如果FILES中没有，尝试从base64获取（备用）
    if not id_card_photo_front:
        front_base64 = data.get('id_card_photo_front_base64') or request.POST.get('id_card_photo_front_base64')
        if front_base64:
            id_card_photo_front = base64_to_image(front_base64, 'id_card_front.jpg')

    if not id_card_photo_back:
        back_base64 = data.get('id_card_photo_back_base64') or request.POST.get('id_card_photo_back_base64')
        if back_base64:
            id_card_photo_back = base64_to_image(back_base64, 'id_card_back.jpg')

    # 获取Session中临时存储的正面照片
    temp_front_data = request.session.get('temp_id_card_front')
    temp_front_name = request.session.get('temp_id_card_front_name')
    temp_front_student_id = request.session.get('temp_id_card_front_student_id')

    # 判断上传类型
    if id_card_photo_front and id_card_photo_back:
        # 网页版：同时上传两张照片
        pass  # 继续处理
    elif id_card_photo_front and not id_card_photo_back:
        # 小程序第一次上传：只有正面照片
        if temp_front_data:
            # 如果已经有暂存的正面照片，检查是否是同一个人
            if temp_front_student_id != student_id:
                # 学号不一致，清除旧的暂存数据
                request.session.pop('temp_id_card_front', None)
                request.session.pop('temp_id_card_front_name', None)
                request.session.pop('temp_id_card_front_student_id', None)
            else:
                # 学号一致，检查是否已经上传过反面照片
                if request.session.get('temp_id_card_back_uploaded'):
                    # 已经上传过反面，清理Session
                    request.session.pop('temp_id_card_front', None)
                    request.session.pop('temp_id_card_front_name', None)
                    request.session.pop('temp_id_card_front_student_id', None)
                    request.session.pop('temp_id_card_back_uploaded', None)
                    return JsonResponse({
                        'success': False,
                        'message': '该学生已报到，请勿重复提交'
                    })

        # 读取正面照片的二进制数据并存储到Session
        id_card_photo_front.seek(0)
        front_data = id_card_photo_front.read()
        id_card_photo_front.seek(0)

        request.session['temp_id_card_front'] = base64.b64encode(front_data).decode('utf-8')
        request.session['temp_id_card_front_name'] = name
        request.session['temp_id_card_front_student_id'] = student_id

        response = JsonResponse({
            'success': True,
            'message': '请继续上传身份证反面照片',
            'waiting_for_back': True
        })
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response

    elif not id_card_photo_front and id_card_photo_back:
        # 小程序第二次上传：只有反面照片
        if not temp_front_data:
            return JsonResponse({
                'success': False,
                'message': '请先上传身份证正面照片'
            })

        if temp_front_student_id != student_id:
            return JsonResponse({
                'success': False,
                'message': '学号不一致，请重新上传正面照片'
            })

        # 从Session恢复正面照片
        front_decoded = base64.b64decode(temp_front_data)
        front_io = BytesIO(front_decoded)
        id_card_photo_front = InMemoryUploadedFile(
            front_io,
            'id_card_photo_front',
            'id_card_front.jpg',
            'image/jpeg',
            len(front_decoded),
            None
        )

        # 标记已上传反面
        request.session['temp_id_card_back_uploaded'] = True
    else:
        return JsonResponse({
            'success': False,
            'message': '请上传身份证照片'
        })

    # 检查是否有照片
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

    if hasattr(id_card_photo_front, 'content_type') and id_card_photo_front.content_type not in allowed_types:
        return JsonResponse({
            'success': False,
            'message': '身份证正面照片格式不支持，请上传 JPG 或 PNG 格式'
        })

    if hasattr(id_card_photo_back, 'content_type') and id_card_photo_back.content_type not in allowed_types:
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
        
        # 清理Session中临时存储的照片数据
        request.session.pop('temp_id_card_front', None)
        request.session.pop('temp_id_card_front_name', None)
        request.session.pop('temp_id_card_front_student_id', None)
        request.session.pop('temp_id_card_back_uploaded', None)
        
        response = JsonResponse({
            'success': True,
            'message': '报到成功',
            'data': {
                'name': name,
                'student_id': student_id,
                'phone': phone,
                'register_time': student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except IntegrityError:
        response = JsonResponse({
            'success': False,
            'message': '学号已存在，请勿重复报到'
        })
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response


def review_status(request):
    """
    审核状态查询接口（4.0新增）
    新生登录后查看自己的审核状态、驳回原因和宿舍号
    """
    is_logged_in = request.session.get('is_logged_in', False)
    phone = request.session.get('verified_phone', '')
    
    if not is_logged_in or not phone:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401)
    
    student = StudentInfo.objects.filter(phone=phone).first()
    
    if not student:
        return JsonResponse({
            'success': False,
            'message': '未找到报到记录，请先提交报到信息'
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'review_status': student.review_status,
            'review_status_display': student.get_review_status_display(),
            'reject_reason': student.reject_reason,
            'dormitory_number': student.dormitory_number
        }
    })


@csrf_exempt
@require_POST
def admin_review(request):
    """
    管理员审核接口（4.0新增）
    管理员审核学生报到信息，可选择通过或驳回
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': '权限不足，仅管理员可操作'
        }, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400)
    
    student_id = data.get('student_id', '').strip()
    action = data.get('action', '').strip()
    reject_reason = data.get('reject_reason', '').strip()
    dormitory_number = data.get('dormitory_number', '').strip()
    
    if not student_id:
        return JsonResponse({
            'success': False,
            'message': '学号不能为空'
        })
    
    if action not in ['approve', 'reject']:
        return JsonResponse({
            'success': False,
            'message': '操作类型错误，应为approve或reject'
        })
    
    student = StudentInfo.objects.filter(student_id=student_id).first()
    
    if not student:
        return JsonResponse({
            'success': False,
            'message': '未找到该学号的学生记录'
        })
    
    if action == 'approve':
        student.review_status = 'approved'
        if dormitory_number:
            student.dormitory_number = dormitory_number
        student.reject_reason = None
    elif action == 'reject':
        if not reject_reason:
            return JsonResponse({
                'success': False,
                'message': '审核驳回时必须填写驳回原因'
            })
        student.review_status = 'rejected'
        student.reject_reason = reject_reason
        student.dormitory_number = None
    
    student.save()
    
    status_display = student.get_review_status_display()
    return JsonResponse({
        'success': True,
        'message': f'审核成功，状态已更新为{status_display}'
    })


def admin_statistics(request):
    """
    统计数据接口（4.0新增）
    管理员查看报到数据统计看板
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': '权限不足，仅管理员可查看'
        }, status=403)
    
    total = StudentInfo.objects.count()
    pending = StudentInfo.objects.filter(review_status='pending').count()
    approved = StudentInfo.objects.filter(review_status='approved').count()
    rejected = StudentInfo.objects.filter(review_status='rejected').count()
    
    pass_rate = round((approved / total * 100), 2) if total > 0 else 0
    
    return JsonResponse({
        'success': True,
        'data': {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'pass_rate': f'{pass_rate}%'
        }
    })


def dormitory_info(request):
    """
    宿舍信息查询接口
    审核通过的学生查看自己的宿舍信息和室友列表
    """
    is_logged_in = request.session.get('is_logged_in', False)
    phone = request.session.get('verified_phone', '')
    
    if not is_logged_in or not phone:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=401)
    
    student = StudentInfo.objects.filter(phone=phone).first()
    
    if not student:
        return JsonResponse({
            'success': False,
            'message': '未找到报到记录'
        })
    
    if student.review_status != 'approved':
        return JsonResponse({
            'success': False,
            'message': '审核未通过，无法查看宿舍信息'
        })
    
    if not student.dormitory_number:
        return JsonResponse({
            'success': False,
            'message': '暂未分配宿舍，请耐心等待'
        })
    
    # 查询宿舍信息
    dormitory = Dormitory.objects.filter(dormitory_number=student.dormitory_number).first()
    
    # 查询室友列表（同宿舍的其他已审核通过学生）
    roommates = StudentInfo.objects.filter(
        dormitory_number=student.dormitory_number,
        review_status='approved'
    ).exclude(id=student.id).values('name', 'student_id', 'phone')
    
    dormitory_data = {
        'dormitory_number': student.dormitory_number,
        'building': dormitory.building if dormitory else '-',
        'floor': dormitory.floor if dormitory else '-',
        'room_number': dormitory.room_number if dormitory else '-',
        'capacity': dormitory.capacity if dormitory else 4,
        'description': dormitory.description if dormitory else '',
        'current_occupancy': len(roommates) + 1,
        'available_beds': (dormitory.capacity if dormitory else 4) - len(roommates) - 1
    }
    
    return JsonResponse({
        'success': True,
        'data': {
            'student_name': student.name,
            'student_id': student.student_id,
            'dormitory': dormitory_data,
            'roommates': list(roommates)
        }
    })


@csrf_exempt
@require_POST
def admin_dormitory_assign(request):
    """
    管理员分配宿舍接口
    管理员为学生分配宿舍号
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': '权限不足，仅管理员可操作'
        }, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400)
    
    student_id = data.get('student_id', '').strip()
    dormitory_number = data.get('dormitory_number', '').strip()
    
    if not student_id or not dormitory_number:
        return JsonResponse({
            'success': False,
            'message': '学号和宿舍号不能为空'
        })
    
    student = StudentInfo.objects.filter(student_id=student_id).first()
    
    if not student:
        return JsonResponse({
            'success': False,
            'message': '未找到该学号的学生记录'
        })
    
    if student.review_status != 'approved':
        return JsonResponse({
            'success': False,
            'message': '该学生审核未通过，无法分配宿舍'
        })
    
    # 检查宿舍是否存在，不存在则创建
    dormitory = Dormitory.objects.filter(dormitory_number=dormitory_number).first()
    if not dormitory:
        # 自动创建宿舍记录
        Dormitory.objects.create(
            dormitory_number=dormitory_number,
            building=dormitory_number[:2] if len(dormitory_number) >= 2 else dormitory_number,
            floor=int(dormitory_number[2:3]) if len(dormitory_number) >= 3 else 1,
            room_number=dormitory_number
        )
    
    student.dormitory_number = dormitory_number
    student.save()
    
    return JsonResponse({
        'success': True,
        'message': f'已成功为学生 {student.name} 分配宿舍 {dormitory_number}'
    })


def admin_dormitory_list(request):
    """
    管理员查看宿舍列表接口
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': '权限不足，仅管理员可查看'
        }, status=403)
    
    dormitories = Dormitory.objects.all()
    
    data = []
    for dorm in dormitories:
        data.append({
            'dormitory_number': dorm.dormitory_number,
            'building': dorm.building,
            'floor': dorm.floor,
            'room_number': dorm.room_number,
            'capacity': dorm.capacity,
            'current_occupancy': dorm.get_current_occupancy(),
            'available_beds': dorm.get_available_beds(),
            'is_full': dorm.get_is_full()
        })
    
    return JsonResponse({
        'success': True,
        'data': data
    })
