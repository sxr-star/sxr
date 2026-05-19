# 新生报到系统 3.0

一个面向高校新生报到场景的信息采集与管理平台，支持手机号验证码登录和身份证照片上传。

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Django](https://img.shields.io/badge/django-4.2-orange)
![OpenCV](https://img.shields.io/badge/opencv-4.x-yellow)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 📋 项目简介

新生报到系统 3.0 是一款面向高校新生报到场景的信息采集与管理平台。系统在 2.0 版本基础上增加了手机号验证码登录和身份证照片上传功能。新生需先通过手机号验证身份，然后填写个人信息并上传身份证正反面照片完成报到。系统支持网页版和微信小程序两种访问方式。

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📱 手机号验证码登录 | 发送验证码到手机，验证后登录系统 |
| 📝 学生信息采集 | 收集新生姓名、学号、手机号 |
| 📷 身份证照片上传 | 上传身份证正反面照片，自动识别正反面 |
| 🔍 重复照片检测 | 检测是否上传同一张照片（MD5 + 感知哈希） |
| 📊 报到记录管理 | 自动记录报到时间，关联学生信息 |
| ✅ 数据验证 | 前端+后端双重验证，确保数据准确性 |
| 🖥️ 管理后台 | 查看、搜索、筛选报到数据，查看身份证照片 |
| 🚫 防重复报到 | 学号唯一性约束，防止重复提交 |

### 🆚 版本对比

| 功能 | 1.0 版本 | 2.0 版本 | 3.0 版本 |
|------|---------|---------|---------|
| 报到方式 | 一键报到 | 表单填写 | 验证码登录 + 表单填写 |
| 身份证照片 | 无 | 无 | ✅ 正反面上传 + 自动识别 |
| 数据模型 | OperationRecord | StudentInfo + RegistrationRecord | + VerificationCode |
| 数据验证 | 无 | 前端+后端 | + 照片检测 + 正反面识别 |
| 防重复 | 无 | 学号唯一 | + 照片去重 |
| 管理后台 | 操作记录 | 学生信息 + 报到记录 | + 身份证照片查看 |

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 4.2 + Python 3.10+ |
| 数据库 | SQLite 3 |
| 图像处理 | OpenCV + NumPy + Pillow |
| 网页前端 | HTML5 + CSS3 + JavaScript + CryptoJS |
| 小程序 | 微信小程序原生开发 |
| 版本控制 | Git + GitHub |

## 📦 安装部署

### 方式一：一键安装（推荐）

双击运行 `完整安装启动.bat`

### 方式二：手动安装

**1. 克隆仓库**

```bash
git clone -b version2 https://github.com/sxr-star/sxr.git
cd sxr
```

**2. 安装依赖**

```bash
pip install django django-cors-headers opencv-python numpy pillow
```

**3. 初始化数据库**

```bash
python manage.py migrate
```

**4. 创建管理员账号**

```bash
python manage.py createsuperuser
```

**5. 启动服务器**

```bash
python manage.py runserver 8000
```

## 🚀 使用方法

### 网页版

1. 打开浏览器访问：http://127.0.0.1:8000/
2. **验证码登录**：输入手机号，点击"获取验证码"（开发阶段在控制台查看）
3. 填写姓名、学号
4. **上传身份证照片**：分别上传身份证正面（人像面）和反面（国徽面）照片
5. 点击"提交报到"按钮
6. 查看报到结果

### 微信小程序版

1. 打开微信开发者工具
2. 导入小程序项目（`小程序` 目录）
3. 在"详情" -> "本地设置"中勾选"不校验合法域名"
4. **验证码登录**：输入手机号，点击"获取验证码"
5. 填写姓名、学号
6. **上传身份证照片**：分别上传身份证正面和反面照片
7. 点击"提交报到"按钮

### 管理后台

1. 打开浏览器访问：http://127.0.0.1:8000/admin/
2. 输入管理员账号和密码
3. 查看学生信息、报到记录和身份证照片

## 📁 项目结构

```
新生报到系统 3.0/
├── api/                            # API 应用
│   ├── models.py                  # 数据模型（StudentInfo、RegistrationRecord、VerificationCode）
│   ├── views.py                   # 视图函数（发送验证码、验证登录、信息采集+身份证上传）
│   ├── urls.py                    # URL 配置
│   ├── admin.py                   # 管理后台配置
│   └── migrations/                # 数据库迁移文件
├── 新生报到系统/                   # 项目配置
│   ├── settings.py                # 项目设置（含媒体文件配置）
│   ├── urls.py                    # 全局 URL 配置
│   └── wsgi.py                    # WSGI 配置
├── media/                         # 媒体文件目录（身份证照片存储）
│   └── id_cards/                  # 身份证照片
├── 网页版/                         # 网页版前端
│   └── index.html                 # 网页版入口（含验证码登录、身份证上传）
├── 小程序/                         # 微信小程序版
│   ├── app.json                   # 小程序配置
│   └── pages/index/               # 小程序页面
│       ├── index.wxml             # 页面结构
│       ├── index.js               # 页面逻辑（含验证码登录、身份证上传）
│       └── index.wxss             # 页面样式
├── scripts/                        # 启动脚本
│   ├── 完整安装启动.bat
│   ├── 快速启动.bat
│   └── 诊断启动.bat
├── manage.py                       # Django 管理脚本
├── 需求分析报告3.0.md              # 需求分析文档
├── 技术方案3.0.md                  # 技术方案文档
├── 数据库设计文档3.0.md            # 数据库设计文档
├── 测试报告3.0.md                  # 测试报告（44个用例，100%通过）
├── 开发Prompt记录.md               # 开发过程记录
├── 使用说明书.md                   # 使用说明书（3.0版本）
└── README.md                       # 项目说明文档
```

## 📚 文档清单

| 文档 | 说明 |
|------|------|
| [需求分析报告3.0.md](./需求分析报告3.0.md) | 系统需求分析 |
| [技术方案3.0.md](./技术方案3.0.md) | 技术架构方案 |
| [数据库设计文档3.0.md](./数据库设计文档3.0.md) | 数据库设计说明 |
| [测试报告3.0.md](./测试报告3.0.md) | 系统测试报告（44个用例，100%通过） |
| [开发Prompt记录.md](./开发Prompt记录.md) | 开发过程记录 |
| [使用说明书.md](./使用说明书.md) | 系统使用指南（3.0版本） |

## 🔌 API 接口

### 报到接口（1.0版本保留）

```
POST /api/register/
```

**请求体：** 无

**响应：**
```json
{
  "success": true,
  "message": "报到成功"
}
```

### 信息采集报到接口（2.0新增）

```
POST /api/register_with_info/
```

**请求体：**
```json
{
  "name": "张三",
  "student_id": "2024001001",
  "phone": "13800138000"
}
```

**响应（成功）：**
```json
{
  "success": true,
  "message": "报到成功",
  "data": {
    "name": "张三",
    "student_id": "2024001001",
    "phone": "13800138000",
    "register_time": "2026-04-27 10:30:00"
  }
}
```

**响应（失败）：**
```json
{
  "success": false,
  "message": "学号已存在，请勿重复报到"
}
```

### 发送验证码接口（3.0新增）

```
POST /api/send_code/
```

**请求体：**
```json
{
  "phone": "13800138000"
}
```

**响应（成功）：**
```json
{
  "success": true,
  "message": "验证码已发送"
}
```

### 验证码校验与登录接口（3.0新增）

```
POST /api/verify_code/
```

**请求体：**
```json
{
  "phone": "13800138000",
  "code": "1234"
}
```

**响应（成功）：**
```json
{
  "success": true,
  "message": "验证成功，已登录"
}
```

**响应（失败）：**
```json
{
  "success": false,
  "message": "验证码错误或已过期"
}
```

### 信息采集+身份证上传接口（3.0新增）

```
POST /api/register_with_info_v3/
```

**请求体：** FormData（含文件）

| 字段 | 类型 | 说明 |
|------|------|------|
| name | String | 学生姓名 |
| student_id | String | 学号 |
| id_card_photo_front | File | 身份证正面照片 |
| id_card_photo_back | File | 身份证反面照片 |

**响应（成功）：**
```json
{
  "success": true,
  "message": "报到成功",
  "data": {
    "name": "张三",
    "student_id": "2024001001",
    "phone": "13800138000",
    "register_time": "2026-04-27 10:30:00"
  }
}
```

**响应（失败）：**
```json
{
  "success": false,
  "message": "未检测到身份证反面照片（带国徽的一面），请检查后重新上传"
}
```

## 🗄️ 数据库设计

### 学生信息表（api_studentinfo）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键，自增 |
| name | CharField(50) | 学生姓名 |
| student_id | CharField(20) | 学号，唯一约束 |
| phone | CharField(11) | 手机号 |
| id_card_photo_front | ImageField | 身份证正面照片路径 |
| id_card_photo_back | ImageField | 身份证反面照片路径 |
| created_at | DateTimeField | 创建时间，自动记录 |

### 报到记录表（api_registrationrecord）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键，自增 |
| student | OneToOneField | 关联学生信息表 |
| register_time | DateTimeField | 报到时间，自动记录 |

### 验证码表（api_verificationcode）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键，自增 |
| phone | CharField(11) | 手机号 |
| code | CharField(4) | 验证码 |
| created_at | DateTimeField | 创建时间，自动记录 |

## ❓ 常见问题

### Q：运行 `python manage.py runserver` 报错 "No module named django"

A：未安装Django，请运行：
```bash
pip install django django-cors-headers opencv-python numpy pillow
```

### Q：小程序请求报错 "request:fail url not in domain list"

A：请在微信开发者工具中勾选"不校验合法域名"

### Q：忘记管理员密码

A：可通过以下命令重置：
```bash
python manage.py changepassword 用户名
```

### Q：上传身份证照片失败

A：请确保：
- 照片格式为 .jpg 或 .png
- 每张照片大小不超过 5MB
- 上传的是身份证的正反两面（非同一张照片）

### Q：验证码收不到

A：开发阶段验证码在服务器控制台打印，生产环境需接入短信服务

更多问题请查看 [使用说明书](./使用说明书.md)

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-04-27 | 最小可用版本，仅跑通链路 |
| 2.0 | 2026-04-27 | 信息采集版，支持学生信息录入 |
| 3.0 | 2026-05-19 | 身份认证版，支持手机号验证码登录和身份证正反面照片上传 |

## 📄 许可证

MIT

## 👥 开发团队

| 角色 | 人员 |
|------|------|
| 开发 | 苏鑫茹 |
| 测试 | 苏鑫茹 |

---

**项目地址：** [https://github.com/sxr-star/sxr](https://github.com/sxr-star/sxr)
**分支：** version3
