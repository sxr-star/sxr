# 新生报到系统

一个简单的新生报到系统，包含 Django 后端和网页版前端。

## 项目简介

本项目实现了一个完整的新生报到流程，用户可以通过网页版或微信小程序进行报到，报到记录会存储在 SQLite 数据库中，并可以通过 Django 管理后台查看。

## 技术栈

- **后端**：Django 6.0.4
- **前端**：HTML、CSS、JavaScript
- **数据库**：SQLite
- **部署**：开发服务器

## 安装方法

### 1. 安装 Python

下载并安装 Python：https://www.python.org/downloads/

### 2. 安装 Django

```bash
pip install django django-cors-headers
```

### 3. 克隆仓库

```bash
git clone https://github.com/sxr-star/sxr.git
cd sxr
```

### 4. 执行数据库迁移

```bash
python manage.py migrate
```

### 5. 创建管理员账号

```bash
python manage.py createsuperuser
```

### 6. 启动服务器

```bash
python manage.py runserver 8000
```

## 使用方法

### 网页版

1. 打开浏览器访问：http://127.0.0.1:8000
2. 点击"点击报到"按钮
3. 查看报到记录

### 微信小程序版

1. 打开微信开发者工具
2. 导入小程序项目
3. 点击"点击报到"按钮
4. 查看报到记录

### 管理后台

1. 打开浏览器访问：http://127.0.0.1:8000/admin
2. 输入管理员账号和密码
3. 查看报到记录

## 项目结构

```
新生报到系统/
├── api/                    # API 应用
│   ├── models.py          # 数据模型
│   ├── views.py           # 视图函数
│   ├── urls.py            # URL 配置
│   └── admin.py           # 管理后台配置
├── 新生报到系统/           # 项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 全局 URL 配置
│   └── wsgi.py            # WSGI 配置
├── 网页版/                 # 网页版前端
│   └── index.html         # 网页版入口
├── 小程序/                 # 微信小程序版
│   ├── app.json           # 小程序配置
│   └── pages/             # 小程序页面
├── manage.py              # Django 管理脚本
└── README.md              # 项目说明文档
```

## 功能特性

- [x] 新生报到功能
- [x] 报到记录存储
- [x] 管理后台查看
- [x] 网页版前端
- [x] 微信小程序版

## 许可证

MIT
