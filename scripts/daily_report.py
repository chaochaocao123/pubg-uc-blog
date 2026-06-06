# PUBG UC攻略 - 每日数据报告脚本
# 每日自动统计网站数据并发送邮件报告

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List

# 配置
VERCEL_API_URL = "https://your-project.vercel.app/api/stats"
EMAIL_REPORT_RECIPIENT = "1324723217@qq.com"

def fetch_analytics_data(days: int = 1) -> Dict:
    """获取分析数据"""
    try:
        response = requests.get(f"{VERCEL_API_URL}?days={days}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API返回错误: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def generate_report(data: Dict) -> str:
    """生成邮件报告内容"""
    
    if "error" in data:
        return f"""
📊 PUBG UC攻略 - 每日数据报告
━━━━━━━━━━━━━━━━━━━━━━
📅 报告日期: {datetime.now().strftime('%Y-%m-%d')}
⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}

⚠️ 数据获取失败
错误信息: {data['error']}

请检查网站是否正常运行。
━━━━━━━━━━━━━━━━━━━━━━
"""
    
    summary = data.get("summary", {})
    daily_data = data.get("data", [])
    
    # 构建报告
    report = f"""
📊 PUBG UC攻略 - 每日数据报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 报告日期: {datetime.now().strftime('%Y-%m-%d')}
⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 核心数据汇总
───────────────────────────────────────
"""
    
    if summary:
        report += f"""
  • 总页面浏览量(PV): {summary.get('totalPV', 0)}
  • 独立访客数(UV): {summary.get('totalUV', 0)}
  • 充值入口点击量: {summary.get('totalBuyClicks', 0)}
  • 日均充值点击: {summary.get('avgBuyClickPerDay', 0)}
"""
    
    report += """
📋 每日详细数据
───────────────────────────────────────
"""
    
    for day_data in daily_data:
        report += f"""
📅 {day_data.get('date', 'N/A')}
  ├ PV: {day_data.get('pv', 0)}
  ├ UV: {day_data.get('uv', 0)}
  ├ 平均阅读时长: {day_data.get('avgDuration', 0)}秒
  ├ 充值点击: {day_data.get('buyClickTotal', 0)}
  └ 热门页面TOP5:
"""
        for i, page in enumerate(day_data.get('topPages', [])[:5], 1):
            report += f"      {i}. {page.get('page', 'N/A')} ({page.get('views', 0)}次)\n"
        
        # 充值点击位置分布
        click_by_pos = day_data.get('buyClickByPosition', {})
        if click_by_pos:
            report += "  └ 点击位置分布:\n"
            for pos, count in click_by_pos.items():
                report += f"      - {pos}: {count}次\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 数据洞察
───────────────────────────────────────
"""
    
    if summary.get('totalPV', 0) > 0:
        ctr = (summary.get('totalBuyClicks', 0) / summary.get('totalPV', 1)) * 100
        report += f"""
  • 充值转化率: {ctr:.2f}%
  • 建议: {'继续保持当前内容策略' if ctr > 1 else '可考虑增加充值入口展示'}
"""
    
    report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 快速链接
  • 网站地址: https://pubg-uc-tips.netlify.app
  • UC充值: https://www.z2u.com/r/anhao

📧 本报告由系统自动生成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return report


def send_email_report(report_content: str) -> bool:
    """发送邮件报告"""
    # 这里需要集成邮件发送功能
    # 可以使用 SendGrid、Mailgun 或其他邮件服务
    print("邮件发送功能需要配置邮件服务...")
    print(report_content)
    return True


def main():
    """主函数"""
    print(f"📊 开始生成 {datetime.now().strftime('%Y-%m-%d')} 数据报告...")
    
    # 获取数据
    data = fetch_analytics_data(days=1)
    
    # 生成报告
    report = generate_report(data)
    
    # 发送邮件
    send_email_report(report)
    
    print("✅ 报告生成完成!")


if __name__ == "__main__":
    main()
