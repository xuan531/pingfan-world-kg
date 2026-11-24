# 上传到 GitHub

本目录已是可直接初始化的 Git 仓库内容。按下面步骤推送即可。

## 1. 在 GitHub 网页创建仓库

1. 打开 https://github.com/new
2. Repository name 填写：`pingfan-world-kg`（或任意名称）
3. 选择 Public / Private，勾选 **Add a README** 可留空（本地已有 README）
4. 点击 **Create repository**，复制页面给出的仓库地址

## 2. 本地推送

在 `kg_pipeline` 目录下执行：

```bash
cd kg_pipeline

git init
git add .
git commit -m "feat: 平凡的世界知识图谱流水线 (NER/RE/KG)"

git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git branch -M main
git push -u origin main
```

## 3. 认证说明

- **HTTPS 方式**：首次推送会要求输入用户名和密码；密码处需填写 **Personal Access Token（PAT）**，而不是登录密码。
  - 生成 PAT：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token，勾选 `repo` 权限。
- **SSH 方式（推荐）**：配置 SSH key 后把 remote 地址换成 `git@github.com:<用户名>/<仓库名>.git`。

## 4. 安全提醒

- 不要把 `OPENAI_API_KEY`、Neo4j 密码等写进代码或提交到仓库。
- 本项目所有密钥均通过**环境变量**读取，`.env` 已加入 `.gitignore`。
- 推送前可执行 `git status` 确认没有敏感文件被加入。

## 5. 后续更新

```bash
git add .
git commit -m "update: 补充实验结果"
git push
```
