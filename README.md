# PUBG UC攻略 - 游戏充值与攻略博客

🎮 专业的PUBG UC充值导航站，提供游戏攻略、资讯、充值教程等内容。

## 功能特性

- ✅ **SEO优化**：完整的meta标签、OG标签、JSON-LD结构化数据
- ✅ **流量统计**：PV、UV、文章阅读量、充值入口点击量追踪
- ✅ **每日更新**：自动生成2篇高质量文章
- ✅ **数据报表**：每日发送数据报告到邮箱
- ✅ **响应式设计**：适配PC端和移动端

## 目录结构

```
pubg-uc-blog/
├── index.html              # 首页
├── articles/               # 文章目录
│   ├── uc-recharge-guide.html
│   ├── pubg-sensitivity-settings.html
│   └── ...
├── api/                    # API接口
│   ├── track.js            # 访问追踪
│   └── stats.js            # 统计数据
├── css/
│   └── style.css           # 样式文件
├── js/
│   ├── main.js             # 首页逻辑
│   └── analytics.js        # 分析工具
├── data/
│   └── articles.json       # 文章列表数据
├── scripts/
│   ├── generate_article.py  # 文章生成脚本
│   ├── daily_report.py      # 日报生成脚本
│   └── social_promo.py      # 社交媒体推广
├── sitemap.xml
├── robots.txt
└── vercel.json
```

## 充值链接配置

充值入口统一跳转到：`https://www.z2u.com/r/anhao`

## 部署指南

### 方式一：Netlify 部署（推荐）

1. 登录 [Netlify](https://netlify.com)
2. 点击 "Add new site" → "Deploy manually"
3. 拖拽 `pubg-uc-blog` 文件夹到上传区域
4. 等待部署完成，获取网站地址
5. 更新 `sitemap.xml` 和 `index.html` 中的域名为实际地址

### 方式二：Vercel 部署

1. 登录 [Vercel](https://vercel.com)
2. Import GitHub仓库或直接上传
3. 配置环境变量（如需KV存储）
4. Deploy

### 方式三：GitHub Pages

1. 创建GitHub仓库
2. 上传代码
3. Settings → Pages → 选择main分支
4. 等待部署完成

## 数据统计

### 追踪指标

| 指标 | 说明 |
|------|------|
| PV | 页面浏览量 |
| UV | 独立访客数 |
| 阅读时长 | 用户在页面的停留时间 |
| 充值点击 | 充值链接点击次数和位置 |

### API接口

- `POST /api/track` - 追踪访问数据
- `GET /api/stats?days=1` - 获取统计数据

### 邮件报告

配置邮件服务后，每日20:00会自动发送数据报告到指定邮箱。

## 自动化任务

### 每日文章生成

```bash
python3 scripts/generate_article.py
```

### 每日数据报告

```bash
python3 scripts/daily_report.py
```

## 定时任务配置

### 使用 Vercel Cron

在 `vercel.json` 中添加：

```json
{
  "crons": [
    {
      "path": "/api/cron/daily",
      "schedule": "0 12 * * *"
    }
  ]
}
```

### 使用 GitHub Actions

在 `.github/workflows/` 下创建 `daily-task.yml`：

```yaml
name: Daily Tasks
on:
  schedule:
    - cron: '0 12 * * *'
```

## SEO优化

- [x] 语义化HTML结构
- [x] 完整的Meta标签
- [x] Open Graph标签
- [x] JSON-LD结构化数据
- [x] Sitemap.xml
- [x] Robots.txt
- [x] 规范化URL

## 注意事项

- 部署后需更新 `sitemap.xml` 中的域名
- 更新 `index.html` 中的 canonical URL
- 配置邮件服务需要 API Key
- Vercel KV 为可选功能

## License

MIT License
