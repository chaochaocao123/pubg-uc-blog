# PUBG UC攻略 - 自动化文章生成脚本
# 每天自动生成2篇文章并更新网站

import json
import random
from datetime import datetime, timedelta
import os
import re

# 文章模板库
ARTICLE_TEMPLATES = {
    "recharge": [
        {
            "title": "PUBG UC充值{day}问答汇总",
            "excerpt": "汇总玩家最关心的UC充值问题，包括充值安全、到账时间、优惠活动等详细内容，助你安心充值。",
            "keywords": "UC充值问答, PUBG充值FAQ, UC充值安全, PUBG充值问题"
        },
        {
            "title": "{day}UC充值避坑指南",
            "excerpt": "盘点UC充值过程中常见的陷阱和误区，教你如何安全充值UC，避免上当受骗。",
            "keywords": "UC充值避坑, PUBG充值安全, UC充值教程, 防骗指南"
        },
        {
            "title": "新手必看：PUBG UC充值全攻略",
            "excerpt": "专为PUBG新手玩家准备的UC充值教程，从注册到充值，每一步都有详细讲解。",
            "keywords": "PUBG新手充值, UC充值教程, PUBG入门"
        }
    ],
    "tips": [
        {
            "title": "PUBG {day}枪械配件搭配指南",
            "excerpt": "详细讲解各种枪械的最佳配件搭配方案，助你找到最适合自己的武器配置，大幅提升战斗力。",
            "keywords": "PUBG配件, 枪械改装, 武器配件, 吃鸡攻略"
        },
        {
            "title": "{day}PUBG听声辨位技巧教学",
            "excerpt": "深入讲解PUBG中的听声辨位技巧，如何利用脚步声和枪声判断敌人位置，是成为高手的必修课。",
            "keywords": "PUBG听声辨位, 吃鸡技巧, 脚步声, 听声辩位"
        },
        {
            "title": "PUBG {day}压枪技巧详解",
            "excerpt": "从基础到进阶，全面解析PUBG压枪技巧，包括陀螺仪压枪、灵敏度设置等实用内容。",
            "keywords": "PUBG压枪, 吃鸡技巧, 压枪教学, 陀螺仪"
        },
        {
            "title": "PUBG {day}卡点技巧与点位推荐",
            "excerpt": "分享各个地图的卡点技巧和优势点位，教你如何在战斗中占据有利地形，提高生存率。",
            "keywords": "PUBG卡点, 吃鸡点位, 地图攻略, 卡点技巧"
        }
    ],
    "news": [
        {
            "title": "PUBG {day}版本平衡调整解析",
            "excerpt": "深入分析最新版本的游戏平衡调整内容，包括武器属性变化、地图更新等，助你第一时间掌握版本动态。",
            "keywords": "PUBG版本更新, 武器平衡, 游戏调整, 版本解析"
        },
        {
            "title": "{day}PUBG职业赛事战报速递",
            "excerpt": "汇总近期PUBG职业赛事的精彩战况，包括各战队表现、比赛亮点、积分排名等精彩内容。",
            "keywords": "PUBG赛事, 职业比赛, 战报, 电竞"
        },
        {
            "title": "PUBG {day}新皮肤预告抢先看",
            "excerpt": "提前曝光即将上线的新皮肤，包括设计理念、上线时间、价格信息等，皮肤党必看！",
            "keywords": "PUBG皮肤, 新皮肤预告, 游戏资讯"
        }
    ],
    "events": [
        {
            "title": "PUBG {day}限时活动参与指南",
            "excerpt": "详细介绍当前限时活动的参与方式、任务要求和奖励内容，助你轻松完成活动任务，拿满奖励。",
            "keywords": "PUBG活动, 限时活动, 活动攻略, 活动奖励"
        },
        {
            "title": "{day}PUBG通行证任务攻略",
            "excerpt": "全面解析当前赛季通行证的各类任务，提供高效完成任务的技巧和策略，助你快速解锁高级奖励。",
            "keywords": "PUBG通行证, 赛季任务, 攻略技巧"
        },
        {
            "title": "PUBG {day}节日活动汇总",
            "excerpt": "汇总近期各类节日活动内容，包括活动入口、奖励一览、参与方式等，让你不错过任何精彩活动。",
            "keywords": "PUBG节日活动, 活动汇总, 游戏活动"
        }
    ]
}

# 文章内容模板
def generate_article_content(title, category, excerpt, keywords, day_str):
    """生成文章HTML内容"""
    
    recharge_cta = f'''
    <div class="article-cta">
        <h3>💰 UC充值优惠进行中</h3>
        <p>安全快速的UC充值服务，助你畅玩PUBG</p>
        <a href="https://www.z2u.com/r/anhao" target="_blank" rel="noopener">立即充值UC →</a>
    </div>'''
    
    category_names = {
        "recharge": "充值教程",
        "tips": "游戏技巧", 
        "news": "游戏资讯",
        "events": "活动攻略"
    }
    
    tips_list = [
        ['多练习基本功', '注意游戏细节', '保持冷静心态', '注重团队配合'],
        ['观察战局变化', '合理规划走位', '善用掩体保护', '预判敌人动向'],
        ['合理选择装备', '做好物资管理', '注意安全转移', '把握出枪时机']
    ]
    selected_tips = random.choice(tips_list)
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{excerpt}">
  <meta name="keywords" content="{keywords}">
  <meta name="robots" content="index, follow">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{excerpt}">
  <meta property="og:type" content="article">
  <title>{title} | PUBG UC攻略</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <header class="header">
    <nav class="nav">
      <a href="../index.html" class="logo">🎮 PUBG UC攻略</a>
      <ul class="nav-links">
        <li><a href="../index.html">首页</a></li>
        <li><a href="https://www.z2u.com/r/anhao" target="_blank" rel="noopener" class="nav-cta">UC充值</a></li>
      </ul>
    </nav>
  </header>

  <main class="container article-page">
    <article class="article-body">
      <header class="article-header">
        <span class="article-category category-{category}">{category_names.get(category, category)}</span>
        <h1>{title}</h1>
        <p class="meta">📅 {datetime.now().strftime("%Y-%m-%d")} | 👁 0 阅读</p>
      </header>

      <div class="article-content">
        <h2>前言</h2>
        <p>{excerpt}</p>

        <h2>主要内容</h2>
        <p>本文将为大家详细介绍{title}的相关内容，帮助玩家更好地了解和掌握相关知识。</p>
        
        <h3>基础介绍</h3>
        <p>首先让我们来了解一下相关的基础知识，这对于后续的学习和实践非常重要。在PUBG这款游戏中，掌握扎实的基本功是成为高手的第一步。</p>
        
        <h3>实用技巧</h3>
        <ul>
          <li>技巧一：{selected_tips[0]}</li>
          <li>技巧二：{selected_tips[1]}</li>
          <li>技巧三：{selected_tips[2]}</li>
        </ul>

        {recharge_cta}

        <h3>进阶建议</h3>
        <p>当你掌握了基础内容后，可以尝试以下进阶技巧来进一步提升：</p>
        <ul>
          <li>深入研究游戏机制，了解每种武器的特性</li>
          <li>观看高水平玩家直播学习他们的操作意识</li>
          <li>多加练习，熟能生巧是提升实力的必经之路</li>
          <li>善于总结经验教训，每次失败都是成长的机会</li>
        </ul>

        <h2>常见问题</h2>
        <h3>Q：需要多长时间才能熟练掌握？</h3>
        <p>A：这取决于个人的学习能力和练习时间，一般来说，坚持练习1-2周就能看到明显进步。</p>

        <h3>Q：有什么推荐的练习方法？</h3>
        <p>A：建议从基础开始，每天坚持练习，同时多观看教学视频和比赛录像。</p>

        <h2>总结</h2>
        <p>以上就是关于{title}的全部内容。希望通过本文的介绍，能够帮助大家更好地掌握相关知识和技巧。如果还有其他问题，欢迎随时咨询。祝各位玩家大吉大利，今晚吃鸡！</p>
        
        <div class="article-cta">
          <h3>🎮 想要更多游戏内容？</h3>
          <p>关注我们，获取更多PUBG攻略和UC充值优惠信息</p>
          <a href="https://www.z2u.com/r/anhao" target="_blank" rel="noopener">UC充值 →</a>
        </div>
      </div>
    </article>

    <div class="article-nav" style="max-width: 800px; margin: 0 auto 40px;">
      <a href="../index.html" class="back-home">← 返回首页</a>
    </div>
  </main>

  <footer class="footer">
    <div class="container">
      <div class="footer-bottom">
        <p>© {datetime.now().year} PUBG UC攻略 All Rights Reserved</p>
      </div>
    </div>
  </footer>

  <script src="../js/analytics.js"></script>
</body>
</html>'''


def generate_article():
    """生成一篇文章"""
    # 随机选择分类
    category = random.choice(list(ARTICLE_TEMPLATES.keys()))
    
    # 随机选择模板
    templates = ARTICLE_TEMPLATES[category]
    template = random.choice(templates)
    
    # 生成日期字符串
    day_str = datetime.now().strftime("%m月%d日")
    
    # 生成标题
    title = template["title"].format(day=day_str)
    
    # 生成文件名前缀（转换为拼音或英文）
    category_prefix = {
        "recharge": "uc-recharge",
        "tips": "pubg-tips",
        "news": "pubg-news",
        "events": "pubg-events"
    }
    filename_prefix = category_prefix.get(category, category)
    
    return {
        "title": title,
        "excerpt": template["excerpt"],
        "keywords": template["keywords"],
        "category": category,
        "filename_prefix": filename_prefix
    }


def update_articles_json(articles):
    """更新 articles.json 文件"""
    json_path = "data/articles.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 获取下一个ID
    next_id = max([a["id"] for a in data["articles"]], default=0) + 1
    
    # 添加新文章
    icon_map = {
        "recharge": "💰",
        "tips": "🎯",
        "news": "📰",
        "events": "🎁"
    }
    
    for article in articles:
        article_entry = {
            "id": next_id,
            "title": article["title"],
            "excerpt": article["excerpt"],
            "url": article["url"],
            "category": article["category"],
            "icon": icon_map.get(article["category"], "📄"),
            "date": article["date"],
            "views": 0,
            "keywords": article["keywords"]
        }
        data["articles"].insert(0, article_entry)
        next_id += 1
    
    data["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 已更新 data/articles.json")


def update_sitemap(articles):
    """更新 sitemap.xml 文件"""
    sitemap_path = "sitemap.xml"
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 找到 urlset 的结束位置
    end_tag = "</urlset>"
    insert_pos = content.rfind(end_tag)
    
    new_urls = ""
    for article in articles:
        url_entry = f'''
  <url>
    <loc>https://pubg-uc-blog.netlify.app/{article["url"]}</loc>
    <lastmod>{article["date"]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
'''
        new_urls += url_entry
    
    new_content = content[:insert_pos] + new_urls + content[insert_pos:]
    
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"  ✅ 已更新 sitemap.xml")


def main():
    """主函数：生成2篇文章"""
    articles = []
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_url = "https://pubg-uc-blog.netlify.app"
    
    print(f"🚀 开始生成 {date_str} 的文章...")
    
    for i in range(2):
        article = generate_article()
        
        # 生成文件名
        filename = f"{article['filename_prefix']}-{date_str}-{i+1}.html"
        filepath = f"articles/{filename}"
        
        # 生成文章内容
        content = generate_article_content(
            title=article["title"],
            category=article["category"],
            excerpt=article["excerpt"],
            keywords=article["keywords"],
            day_str=date_str
        )
        
        # 保存文章文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"  ✅ 文章{i+1}: {article['title']}")
        print(f"     保存到: {filepath}")
        
        articles.append({
            "title": article["title"],
            "url": filepath,
            "category": article["category"],
            "date": date_str,
            "excerpt": article["excerpt"],
            "keywords": article["keywords"]
        })
    
    # 更新配置文件
    update_articles_json(articles)
    update_sitemap(articles)
    
    print(f"\n✨ 成功生成 {len(articles)} 篇文章!")
    return articles


if __name__ == "__main__":
    main()
