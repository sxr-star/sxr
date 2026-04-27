# 新生报到项目 - 完整开发 Prompt 记录

## 项目概述

**项目名称**：新生报到系统（只跑通版）
**技术栈**：Django 6.0.4 + SQLite + HTML/CSS/JavaScript + 微信小程序
**核心功能**：实现从前端（网页版/小程序）到后端数据库的完整数据通道

---

## Prompt 1：项目初始化

### 用户需求
根据项目文档，建立一个最小可行的新生报到系统，包含：
- 网页版前端按钮
- Django 后端接口
- SQLite 数据库存储
- Django Admin 管理后台

### 实现步骤
1. 安装 Python 到 D 盘
2. 安装 Django 和 django-cors-headers
3. 创建 Django 项目结构
4. 定义 OperationRecord 模型
5. 执行数据库迁移
6. 创建管理员账号
7. 启动开发服务器

---

## Prompt 2：网页版前端开发

### 用户需求
创建网页版前端，替代微信小程序

### 实现内容
- 创建 `网页版/index.html`
- 包含报到按钮和状态显示
- 使用 fetch API 发送 POST 请求到后端
- 添加 CSS 样式美化界面

---

## Prompt 3：微信小程序版开发

### 用户需求
创建微信小程序版前端

### 实现内容
- 创建 `小程序/app.json`
- 创建 `小程序/pages/index/index.wxml`（页面结构）
- 创建 `小程序/pages/index/index.wxss`（样式）
- 创建 `小程序/pages/index/index.js`（逻辑）
- 使用 wx.request 发送 POST 请求到后端

---

## Prompt 4：跨域问题解决

### 问题描述
网页版和小程序版请求后端时出现跨域错误（OPTIONS 请求 405）

### 解决方案
1. 安装 `django-cors-headers`
2. 在 `settings.py` 中添加 `corsheaders` 到 INSTALLED_APPS
3. 在 MIDDLEWARE 最前面添加 `corsheaders.middleware.CorsMiddleware`
4. 设置 `CORS_ALLOW_ALL_ORIGINS = True`

---

## Prompt 5：数据库迁移问题

### 问题描述
请求接口时报错：`no such table: api_operationrecord`

### 解决方案
1. 运行 `python manage.py makemigrations api`
2. 运行 `python manage.py migrate`

---

## Prompt 6：Git 版本控制

### 用户需求
将代码提交到 GitHub 仓库

### 实现步骤
1. 初始化 Git 仓库：`git init`
2. 添加所有文件：`git add .`
3. 提交代码：`git commit -m "完成新生报到系统"`
4. 添加远程仓库：`git remote add origin https://github.com/sxr-star/sxr.git`
5. 推送代码：`git push -u origin main`

### 创建版本分支
1. 创建新分支：`git checkout -b version2`
2. 推送分支：`git push origin version2`

### 创建一键推送脚本
创建 `Git推送.bat` 脚本，方便后续快速推送代码

---

## Prompt 7：README.md 文档

### 用户需求
创建项目说明文档

### 实现内容
- 项目简介
- 技术栈说明
- 安装方法
- 使用说明
- 项目结构
- 功能特性
- 许可证信息

---

## Prompt 8：网页版 404 问题修复

### 问题描述
访问 `http://127.0.0.1:8000/` 显示 404 错误

### 解决方案
1. 在 `api/views.py` 中添加首页视图函数 `index()`
2. 在 `新生报到系统/urls.py` 中添加根路径路由
3. 重启服务器

---

## Prompt 9：README.md 网址更正

### 问题描述
README.md 中的网址使用了错误的 IP 地址 `172.25.58.4`

### 解决方案
将所有网址更正为 `127.0.0.1`

---

## 常用命令汇总

### 服务器相关
```bash
# 启动服务器
python manage.py runserver 8000

# 执行数据库迁移
python manage.py migrate
python manage.py makemigrations api

# 创建管理员账号
python manage.py createsuperuser
```

### Git 相关
```bash
# 查看状态
git status

# 添加文件
git add .

# 提交代码
git commit -m "提交信息"

# 推送代码
git push origin main

# 创建新分支
git checkout -b version2

# 推送分支
git push origin version2

# 切换分支
git checkout main
```

### 一键推送脚本
双击运行 `Git推送.bat` 即可快速推送代码

---

## 项目文件结构

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
├── README.md              # 项目说明文档
├── Git推送.bat            # 一键推送脚本
├── 完整安装启动.bat        # 完整安装启动脚本
├── 快速启动.bat           # 快速启动脚本
└── 诊断启动.bat           # 诊断启动脚本
```

---

## 访问地址

- **网页版报到页面**：http://127.0.0.1:8000/
- **管理后台**：http://127.0.0.1:8000/admin
- **API 接口**：http://127.0.0.1:8000/api/register/

---

## GitHub 仓库

- **仓库地址**：https://github.com/sxr-star/sxr
- **主分支**：main
- **开发分支**：version2
