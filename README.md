# 新生报到系统 2.0

一个面向高校新生报到场景的信息采集与管理平台，支持网页版和微信小程序两种访问方式。

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Django](https://img.shields.io/badge/django-6.0.4-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 📋 项目简介

新生报到系统 2.0 是一款面向高校新生报到场景的信息采集与管理平台。系统支持网页版和微信小程序两种访问方式，新生可通过填写姓名、学号、手机号完成报到操作，管理员可通过管理后台查看和管理报到数据。

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📝 学生信息采集 | 收集新生姓名、学号、手机号 |
| 📊 报到记录管理 | 自动记录报到时间，关联学生信息 |
| ✅ 数据验证 | 前端+后端双重验证，确保数据准确性 |
| 🔍 管理后台 | 查看、搜索、筛选报到数据 |
| 🚫 防重复报到 | 学号唯一性约束，防止重复提交 |

### 🆚 版本对比

| 功能 | 1.0 版本 | 2.0 版本 |
|------|---------|---------|
| 报到方式 | 一键报到 | 表单填写（姓名、学号、手机号） |
| 数据模型 | OperationRecord | StudentInfo + RegistrationRecord |
| 数据验证 | 无 | 前端+后端双重验证 |
| 防重复 | 无 | 学号唯一性约束 |
| 管理后台 | 操作记录 | 学生信息 + 报到记录 |

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 6.0.4 + Python 3.13.2 |
| 数据库 | SQLite 3 |
| 网页前端 | HTML5 + CSS3 + JavaScript |
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
pip install django django-cors-headers
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
2. 填写姓名、学号、手机号
3. 点击"提交报到"按钮
4. 查看报到结果

### 微信小程序版

1. 打开微信开发者工具
2. 导入小程序项目（`小程序` 目录）
3. 在"详情" -> "本地设置"中勾选"不校验合法域名"
4. 填写姓名、学号、手机号
5. 点击"提交报到"按钮

### 管理后台

1. 打开浏览器访问：http://127.0.0.1:8000/admin/
2. 输入管理员账号和密码
3. 查看学生信息和报到记录

## 📁 项目结构

```
新生报到系统 2.0/
├── api/                            # API 应用
│   ├── models.py                  # 数据模型（StudentInfo、RegistrationRecord）
│   ├── views.py                   # 视图函数（register、register_with_info、index）
│   ├── urls.py                    # URL 配置
│   ├── admin.py                   # 管理后台配置
│   └── migrations/                # 数据库迁移文件
├── 新生报到系统/                   # 项目配置
│   ├── settings.py                # 项目设置
│   ├── urls.py                    # 全局 URL 配置
│   └── wsgi.py                    # WSGI 配置
├── 网页版/                         # 网页版前端
│   └── index.html                 # 网页版入口
├── 小程序/                         # 微信小程序版
│   ├── app.json                   # 小程序配置
│   └── pages/index/               # 小程序页面
│       ├── index.wxml             # 页面结构
│       ├── index.js               # 页面逻辑
│       └── index.wxss             # 页面样式
├── scripts/                        # 启动脚本
│   ├── 完整安装启动.bat
│   ├── 快速启动.bat
│   └── 诊断启动.bat
├── manage.py                       # Django 管理脚本
├── 需求分析报告2.0.md              # 需求分析文档
├── 技术方案2.0.md                  # 技术方案文档
├── 数据库设计文档2.0.md            # 数据库设计文档
├── 测试报告2.0.md                  # 测试报告
├── 开发Prompt记录.md               # 开发过程记录
├── 使用说明书.md                   # 使用说明书
└── README.md                       # 项目说明文档
```

## 📚 文档清单

| 文档 | 说明 |
|------|------|
| [需求分析报告2.0.md](./需求分析报告2.0.md) | 系统需求分析 |
| [技术方案2.0.md](./技术方案2.0.md) | 技术架构方案 |
| [数据库设计文档2.0.md](./数据库设计文档2.0.md) | 数据库设计说明 |
| [测试报告2.0.md](./测试报告2.0.md) | 系统测试报告（27个用例，100%通过） |
| [开发Prompt记录.md](./开发Prompt记录.md) | 开发过程记录 |
| [使用说明书.md](./使用说明书.md) | 系统使用指南 |

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

## 🗄️ 数据库设计

### 学生信息表（api_studentinfo）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键，自增 |
| name | CharField(50) | 学生姓名 |
| student_id | CharField(20) | 学号，唯一约束 |
| phone | CharField(11) | 手机号 |
| created_at | DateTimeField | 创建时间，自动记录 |

### 报到记录表（api_registrationrecord）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键，自增 |
| student | OneToOneField | 关联学生信息表 |
| register_time | DateTimeField | 报到时间，自动记录 |

## ❓ 常见问题

### Q：运行 `python manage.py runserver` 报错 "No module named django"

A：未安装Django，请运行：
```bash
pip install django django-cors-headers
```

### Q：小程序请求报错 "request:fail url not in domain list"

A：请在微信开发者工具中勾选"不校验合法域名"

### Q：忘记管理员密码

A：可通过以下命令重置：
```bash
python manage.py changepassword 用户名
```

更多问题请查看 [使用说明书](./使用说明书.md)

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-04-27 | 最小可用版本，仅跑通链路 |
| 2.0 | 2026-04-27 | 信息采集版，支持学生信息录入 |

## 📄 许可证

MIT

## 👥 开发团队

| 角色 | 人员 |
|------|------|
| 开发 | 苏鑫茹 |
| 测试 | 苏鑫茹 |

---

**项目地址：** [https://github.com/sxr-star/sxr](https://github.com/sxr-star/sxr)
**分支：** version2
