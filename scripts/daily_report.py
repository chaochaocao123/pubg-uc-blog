#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUBG UC攻略 - 每日数据报告脚本（GA4 Data API版）
从Google Analytics 4 Data API拉取真实数据，生成每日报告并发送邮件
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

# ==================== 配置 ====================
GA4_PROPERTY_ID = "540383612"  # PUBG UC博客媒体资源ID
GA4_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "ga4-credentials.json")
EMAIL_RECIPIENT = "1324723217@qq.com"
SITE_URL = "https://pubg-uc-blog.netlify.app/"
RECHARGE_URL = "https://www.z2u.com/r/anhao"

# ==================== GA4 Data API ====================
def init_ga4_client():
    """初始化GA4 Data API客户端"""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange, Metric, Dimension, RunReportRequest
        )
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            GA4_CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        client = BetaAnalyticsDataClient(credentials=credentials)
        return client, DateRange, Metric, Dimension, RunReportRequest
    except ImportError:
        return None, None, None, None, None
    except Exception as e:
        print(f"GA4客户端初始化失败: {e}")
        return None, None, None, None, None


def run_report(client, DateRange, Metric, Dimension, RunReportRequest,
               dimensions: List[str], metrics: List[str],
               start_date: str, end_date: str, limit: int = 100) -> List:
    """运行GA4报告查询"""
    try:
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=limit
        )
        response = client.run_report(request)
        return response
    except Exception as e:
        print(f"GA4查询失败: {e}")
        return None


def fetch_ga4_data() -> Dict:
    """从GA4获取真实数据"""
    client, DateRange, Metric, Dimension, RunReportRequest = init_ga4_client()

    if client is None:
        return {
            "error": "GA4客户端未初始化，请检查:\n"
                     "1) 是否安装了 google-analytics-data 库 (pip install google-analytics-data)\n"
                     "2) ga4-credentials.json 是否存在\n"
                     "3) GA4_PROPERTY_ID 是否正确配置"
        }

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    result = {
        "yesterday_pv": 0,
        "yesterday_uv": 0,
        "week_pv": 0,
        "week_uv": 0,
        "month_pv": 0,
        "month_uv": 0,
        "recharge_clicks": 0,
        "recharge_by_position": {},
        "top_pages": [],
        "read_time_avg": 0,
        "data_source": "Google Analytics 4 (真实数据)"
    }

    # 1. 昨日PV/UV
    resp = run_report(client, DateRange, Metric, Dimension, RunReportRequest,
                      dimensions=[], metrics=["screenPageViews", "totalUsers"],
                      start_date=yesterday, end_date=yesterday)
    if resp and resp.rows:
        row = resp.rows[0]
        result["yesterday_pv"] = int(row.metric_values[0].value)
        result["yesterday_uv"] = int(row.metric_values[1].value)

    # 2. 本周PV/UV
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    resp = run_report(client, DateRange, Metric, Dimension, RunReportRequest,
                      dimensions=[], metrics=["screenPageViews", "totalUsers"],
                      start_date=week_ago, end_date=today)
    if resp and resp.rows:
        row = resp.rows[0]
        result["week_pv"] = int(row.metric_values[0].value)
        result["week_uv"] = int(row.metric_values[1].value)

    # 3. 本月PV/UV
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    resp = run_report(client, DateRange, Metric, Dimension, RunReportRequest,
                      dimensions=[], metrics=["screenPageViews", "totalUsers"],
                      start_date=month_ago, end_date=today)
    if resp and resp.rows:
        row = resp.rows[0]
        result["month_pv"] = int(row.metric_values[0].value)
        result["month_uv"] = int(row.metric_values[1].value)

    # 4. 充值入口点击（recharge_click事件）按位置分布
    resp = run_report(client, DateRange, Metric, Dimension, RunReportRequest,
                      dimensions=["customEvent:link_position"],
                      metrics=["eventCount"],
                      start_date=yesterday, end_date=yesterday,
                      limit=20)
    if resp and resp.rows:
        total_clicks = 0
        for row in resp.rows:
            pos = row.dimension_values[0].value
            count = int(row.metric_values[0].value)
            result["recharge_by_position"][pos] = count
            total_clicks += count
        result["recharge_clicks"] = total_clicks

    # 5. 昨日热门页面TOP10
    resp = run_report(client, DateRange, Metric, Dimension, RunReportRequest,
                      dimensions=["pagePath", "pageTitle"],
                      metrics=["screenPageViews"],
                      start_date=yesterday, end_date=yesterday,
                      limit=10)
    if resp and resp.rows:
        for row in resp.rows:
            result["top_pages"].append({
                "path": row.dimension_values[0].value,
                "title": row.dimension_values[1].value,
                "views": int(row.metric_values[0].value)
            })

    # 6. 昨日平均阅读时长（基于 read_time 事件）
    resp = run_report(client, DateRange, Metric, Dimension, RunReportRequest,
                      dimensions=[],
                      metrics=["averageSessionDuration"],
                      start_date=yesterday, end_date=yesterday)
    if resp and resp.rows:
        result["read_time_avg"] = round(float(resp.rows[0].metric_values[0].value), 1)

    return result


# ==================== 报告生成 ====================
def generate_report(data: Dict) -> str:
    """生成邮件报告内容"""

    if "error" in data:
        return f"""
📊 PUBG UC攻略 - 每日数据报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 报告日期: {datetime.now().strftime('%Y-%m-%d')}
⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}

⚠️ GA4数据获取失败
{data['error']}

💡 提示: GA4 报告通常有 24-48 小时数据延迟，昨天之前的数据应该是完整的。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    report = f"""
📊 PUBG UC攻略 - 每日数据报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 报告日期: {datetime.now().strftime('%Y-%m-%d')}
📆 数据范围: {yesterday}（昨日）
⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}
📡 数据来源: {data.get('data_source', 'GA4')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 核心指标
───────────────────────────────────────
  • 昨日 PV:        {data['yesterday_pv']:,}
  • 昨日 UV:        {data['yesterday_uv']:,}
  • 充值入口点击:    {data['recharge_clicks']} 次
  • 平均会话时长:    {data['read_time_avg']} 秒
"""

    # 计算转化率
    if data['yesterday_pv'] > 0:
        ctr = (data['recharge_clicks'] / data['yesterday_pv']) * 100
        report += f"  • 充值点击率:    {ctr:.2f}%\n"

    report += f"""
📊 多周期对比
───────────────────────────────────────
  • 昨日 PV/UV:   {data['yesterday_pv']:,} / {data['yesterday_uv']:,}
  • 近7天 PV/UV:  {data['week_pv']:,} / {data['week_uv']:,}
  • 近30天 PV/UV: {data['month_pv']:,} / {data['month_uv']:,}
"""

    # 充值入口位置分布
    if data['recharge_by_position']:
        report += """
🎯 充值入口点击位置分布（昨日）
───────────────────────────────────────
"""
        sorted_pos = sorted(data['recharge_by_position'].items(),
                           key=lambda x: -x[1])
        pos_name_map = {
            "hero": "首屏主CTA",
            "nav": "导航栏",
            "sidebar": "侧边栏",
            "banner": "横幅广告位",
            "article_bottom": "文章底部",
            "footer": "页脚"
        }
        for pos, count in sorted_pos:
            cn_name = pos_name_map.get(pos, pos)
            bar = "█" * min(count, 30)
            report += f"  {cn_name:12s} {count:>4d}次  {bar}\n"

    # 热门页面
    if data['top_pages']:
        report += """
🔥 热门页面TOP10（昨日）
───────────────────────────────────────
"""
        for i, page in enumerate(data['top_pages'], 1):
            title = page['title'][:40] + "..." if len(page['title']) > 40 else page['title']
            report += f"  {i:2d}. {title}\n"
            report += f"      {page['path']}  ({page['views']:,}次)\n"

    # 洞察建议
    report += """
💡 数据洞察与建议
───────────────────────────────────────
"""
    insights = []
    if data['recharge_clicks'] == 0 and data['yesterday_pv'] > 0:
        insights.append("• 暂无充值点击数据（昨日新部署追踪代码属正常）")
    if data['yesterday_pv'] > 0 and data['recharge_clicks'] > 0:
        ctr = (data['recharge_clicks'] / data['yesterday_pv']) * 100
        if ctr < 1:
            insights.append(f"• 充值点击率 {ctr:.2f}% 偏低，可考虑增加侧边栏和文章底部入口")
        elif ctr > 3:
            insights.append(f"• 充值点击率 {ctr:.2f}% 表现良好，继续保持")
    if not data['top_pages']:
        insights.append("• 昨日无访问数据（首次部署追踪代码后属正常）")
    if not insights:
        insights.append("• 数据正常，持续观察中")

    for ins in insights:
        report += f"  {ins}\n"

    report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 快速链接
  • 网站: {SITE_URL}
  • UC充值: {RECHARGE_URL}
  • GA4后台: https://analytics.google.com/

📧 本报告由系统自动基于 Google Analytics 4 真实数据生成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return report


# ==================== 邮件发送 ====================
def send_email_report(report_content: str) -> bool:
    """发送邮件报告（通过 email_request 工具，外部触发）"""
    # 这个函数不直接发邮件
    # 日历任务执行器会在脚本跑完后调用 email_request 发邮件
    print(report_content)
    return True


# ==================== 主函数 ====================
def main():
    """主函数"""
    print(f"📊 开始生成 {datetime.now().strftime('%Y-%m-%d')} 数据报告...")

    # 1. 获取GA4数据
    data = fetch_ga4_data()

    if "error" in data:
        print(f"⚠️ 警告: {data['error']}")
        print("建议检查：")
        print("1) pip install google-analytics-data")
        print("2) 确认 GA4_PROPERTY_ID 已替换为真实的属性ID")
        print("3) 确认服务账号已被授权访问GA4媒体资源")

    # 2. 生成报告
    report = generate_report(data)

    # 3. 输出报告
    send_email_report(report)

    print("✅ 报告生成完成!")
    return report


if __name__ == "__main__":
    main()
