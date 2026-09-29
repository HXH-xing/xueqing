# 智能学情分析平台 — 云端部署指南

本指南让你把这个应用部署到一台**24 小时在线的服务器**,实现「本机关机、其他电脑照样能打开」。

---

## 一、本次改造做了什么

| 改动 | 说明 |
|------|------|
| 密钥/配置走环境变量 | DeepSeek 密钥、JWT 密钥、数据库地址都不再硬编码,统一通过 `SECRET_KEY` / `DEEPSEEK_API_KEY` / `DATABASE_URL` 注入 |
| 前后端同源部署 | 前端构建产物 `dist/` 由后端直接托管,一个服务 = 一个端口 = 一个域名,免去跨域、免去单独托管前端 |
| 补齐部署文件 | `requirements.txt`、`Dockerfile`、`docker-compose.yml`、`.env.example` |

后端文件是 `4.py`(历史遗留命名),启动时用 `uvicorn 4:app` 引用它,下面所有命令都已写对,照抄即可。

---

## 二、上线前必做(重要)

1. **换 DeepSeek 密钥**。原密钥 `sk-0f1f...` 曾随代码明文暴露,建议到 [DeepSeek 开放平台](https://platform.deepseek.com) **吊销旧密钥、重新生成**一个,再通过环境变量注入。
2. **换 JWT 密钥 `SECRET_KEY`**。改成随机长字符串(随便敲一串 30 位以上的字母数字),否则登录令牌可被伪造。
3. **数据持久化**。数据库是 SQLite 文件,放在 `./data` 目录。Docker 部署记得挂卷(见下);免费平台注意文件系统是否持久。

---

## 三、方式一:Docker 部署(最推荐)

适用:任何装了 Docker 的云服务器(阿里云/腾讯云轻量应用服务器、各种 VPS)。约 ¥30–60/月。

1. 把整个项目目录上传到服务器(或 `git clone`)。
2. 编辑 `docker-compose.yml`,把 `SECRET_KEY` 和 `DEEPSEEK_API_KEY` 改成真实值。
3. 一键启动:
   ```bash
   docker compose up -d --build
   ```
4. 打开 `http://服务器IP:8000` 即可访问。想不带端口号,把 compose 里 `"8000:8000"` 改成 `"80:8000"`。

数据存在 `./data`(已挂载为卷),容器重启、镜像更新都不丢数据。

---

## 四、方式二:免费平台 Render(一步步)

免费,但有**冷启动**(闲置后首次访问等几十秒)和**文件不持久**的缺点,适合演示、不适合正式长期用。

1. 把项目上传到 GitHub(仓库里不要带 `.env` 和 `data/`)。
2. 注册 [Render](https://render.com) → **New → Web Service** → 连接你的 GitHub 仓库。
3. Render 会自动识别仓库里的 `Dockerfile`(选 Docker 运行时)。
4. 在 **Environment Variables** 里添加:
   - `SECRET_KEY` = 一串随机字符串
   - `DEEPSEEK_API_KEY` = 你的真实密钥
   - 端口 Render 会自动注入 `PORT`,不用管。
5. 点 **Create Web Service**,等待构建完成,拿到形如 `https://xxx.onrender.com` 的公网链接。

> ⚠️ Render 免费版文件系统是临时的,SQLite 数据在重启后会丢失。要长期用,建议:
> - 改用 Render 的 PostgreSQL(免费),并把 `DATABASE_URL` 设成 Postgres 连接串(`pip install psycopg2-binary` 后由 SQLAlchemy 自动支持);
> - 或升级到带持久盘的付费套餐。

---

## 五、方式三:裸机部署(无 Docker)

适用:云服务器不想装 Docker,直接用 Python 跑。

```bash
# 1. 装依赖(建议 Python 3.11)
pip install -r requirements.txt

# 2. 构建前端(留空 VITE_API_BASE → 走相对路径)
npm install && npm run build

# 3. 注入环境变量并启动
export SECRET_KEY="你的随机密钥"
export DEEPSEEK_API_KEY="你的真实密钥"
uvicorn 4:app --host 0.0.0.0 --port 8000
```

想让 `uvicorn` 常驻后台,可用 `nohup`、`systemd` 或 `supervisor`。生产建议前面再接一层 nginx 做 HTTPS。

---

## 六、常见问题

- **打开页面但登录报错** → 后端没起来或 `SECRET_KEY` 改了但旧 token 失效,重新登录即可;看后端日志。
- **AI 对话/智能出题不可用** → `DEEPSEEK_API_KEY` 没配或已失效。
- **重启后数据没了** → 免费平台文件系统不持久(见方式二),或 Docker 没挂 `./data` 卷。
- **端口不通** → 云服务器安全组/防火墙放行对应端口(8000 或 80)。

---

## 七、目录结构(部署相关)

```
.
├── 4.py                 # FastAPI 后端(含 SQLite,托管 dist)
├── App.vue              # 前端单文件组件
├── src/main.js          # 前端入口
├── index.html           # 前端模板
├── vite.config.js       # Vite 配置
├── package.json         # 前端依赖
├── requirements.txt     # 后端依赖
├── Dockerfile           # 多阶段构建(前端 build → 后端运行)
├── docker-compose.yml   # Docker 一键部署
├── .env.example         # 环境变量样例
└── DEPLOY.md            # 本文档
```
