/**
 * Vercel Serverless Function - 统计数据查询
 * 返回 PV、UV、文章阅读量、充值入口点击量等数据
 */

const { kv } = require('@vercel/kv');

module.exports = async (req, res) => {
  // CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // 处理 OPTIONS 请求
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // 只接受 GET 请求
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { days = '1' } = req.query;
    const dayCount = parseInt(days) || 1;
    
    const results = {
      period: `最近${dayCount}天`,
      data: []
    };

    // 获取最近N天的数据
    for (let i = 0; i < dayCount; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateKey = date.toISOString().split('T')[0];
      
      const dailyKey = `pubg_analytics:${dateKey}`;
      const clickKey = `pubg_analytics:clicks:${dateKey}`;
      
      let dailyData = null;
      let clickData = null;
      
      try {
        dailyData = await kv.get(dailyKey);
        clickData = await kv.get(clickKey);
      } catch (kvError) {
        // KV 不可用
      }
      
      // 计算统计数据
      const visitors = new Set();
      let totalPV = 0;
      let totalDuration = 0;
      let readCount = 0;
      
      if (dailyData && Array.isArray(dailyData)) {
        dailyData.forEach(record => {
          if (record.type === 'pv') {
            totalPV++;
            visitors.add(record.visitorId);
          } else if (record.type === 'read_time') {
            totalDuration += record.duration || 0;
            readCount++;
          }
        });
      }
      
      // 按页面统计阅读量
      const pageViews = {};
      if (dailyData && Array.isArray(dailyData)) {
        dailyData.forEach(record => {
          if (record.type === 'pv' && record.page) {
            if (!pageViews[record.page]) {
              pageViews[record.page] = 0;
            }
            pageViews[record.page]++;
          }
        });
      }
      
      results.data.push({
        date: dateKey,
        pv: totalPV,
        uv: visitors.size,
        avgDuration: readCount > 0 ? Math.round(totalDuration / readCount) : 0,
        buyClickTotal: clickData?.total || 0,
        buyClickByPosition: clickData?.byPosition || {},
        topPages: Object.entries(pageViews)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([page, views]) => ({ page, views }))
      });
    }

    // 计算汇总
    results.summary = {
      totalPV: results.data.reduce((sum, d) => sum + d.pv, 0),
      totalUV: new Set(
        results.data.flatMap(d => 
          results.data.find(x => x.date === d.date)?.data || []
        ).map(r => r.visitorId)
      ).size,
      totalBuyClicks: results.data.reduce((sum, d) => sum + d.buyClickTotal, 0),
      avgBuyClickPerDay: dayCount > 0 
        ? (results.data.reduce((sum, d) => sum + d.buyClickTotal, 0) / dayCount).toFixed(2)
        : 0
    };

    return res.status(200).json(results);

  } catch (error) {
    console.error('Stats error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
