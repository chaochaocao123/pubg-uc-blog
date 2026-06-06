# GA4 配置文件

## 🚀 快速配置

### 第 1 步：编辑 `scripts/daily_report.py`

把第 14 行的：
```python
GA4_PROPERTY_ID = "替换为您的GA4属性ID"
```

替换为真实的 GA4 属性 ID（**纯数字**，不是 `G-XXXXXXXX` 形式的衡量 ID）。

📝 **如何找到 GA4 属性 ID：**
1. 打开 [Google Analytics](https://analytics.google.com/)
2. 左下角 **管理员** → **媒体资源** 列 → **媒体资源设置**
3. 复制右上角 **"媒体资源 ID"** 字段（纯数字，如 `371234567`）

### 第 2 步：放置 Service Account 凭据

将 Google Cloud 下载的 Service Account JSON 文件重命名为 `ga4-credentials.json`，放到：
```
pubg-uc-blog/scripts/ga4-credentials.json
```

⚠️ **重要：此文件已加入 `.gitignore`，不会被提交到 GitHub，请放心使用。**

### 第 3 步：安装依赖

```bash
pip install google-analytics-data
```

### 第 4 步：授权验证

确认 Service Account 邮箱已被添加到 GA4 媒体资源的 **账号访问管理** 中，权限为 **查看者**。

Service Account 邮箱格式：`xxx@xxx.iam.gserviceaccount.com`（在 JSON 文件的 `client_email` 字段）。

---

## 🧪 测试

```bash
cd pubg-uc-blog
python3 scripts/daily_report.py
```

**预期输出：**
- 成功：显示 PV/UV/充值点击 等真实数据
- 失败：显示具体错误原因（通常是 GA4_PROPERTY_ID 没填或权限没开）

---

## 🔐 安全说明

- ✅ `ga4-credentials.json` 已在 `.gitignore` 中
- ✅ 不会被推送到 GitHub
- ✅ Service Account 仅有 **只读** 权限（Viewer）
- ❌ 请勿将 JSON 文件内容分享给任何人
