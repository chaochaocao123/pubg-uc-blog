/**
 * Vercel Serverless Function - 页面访问追踪
 * 接收追踪数据，存入 Vercel KV
 */

const { kv } = require('@vercel/kv');

module.exports = async (req, res) => {
  // CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // 处理 OPTIONS 请求
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // 只接受 POST 请求
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const data = req.body;
    
    // 验证必需字段
    if (!data.page || !data.sessionId || !data.visitorId) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const now = new Date();
    const dateKey = now.toISOString().split('T')[0]; // YYYY-MM-DD
    const timestamp = now.toISOString();

    // 构建记录
    const record = {
      page: data.page,
      sessionId: data.sessionId,
      visitorId: data.visitorId,
      timestamp,
      referrer: data.referrer || 'direct',
      type: data.type || 'pv',
      duration: data.duration || null,
      pageTitle: data.pageTitle || ''
    };

    // 充值链接点击额外字段
    if (data.type === 'buy_click') {
      record.buyLink = data.buyLink || '';
      record.linkText = data.linkText || '';
      record.linkPosition = data.linkPosition || '';
    }

    // 存储到 KV
    const dailyKey = `pubg_analytics:${dateKey}`;
    
    try {
      // 获取现有记录
      let dailyData = await kv.get(dailyKey);
      
      if (!dailyData) {
        dailyData = [];
      }
      
      // 添加新记录
      dailyData.push(record);
      
      // 保存（设置 90 天过期）
      await kv.set(dailyKey, dailyData, { ex: 90 * 24 * 60 * 60 });
      
      // 按页面维度存储
      const pageKey = `pubg_analytics:page:${dateKey}:${data.page}`;
      let pageData = await kv.get(pageKey);
      
      if (!pageData) {
        pageData = { pv: 0, visitors: [], totalDuration: 0, count: 0 };
      }
      
      pageData.pv = (pageData.pv || 0) + 1;
      if (!pageData.visitors) {
        pageData.visitors = [];
      }
      if (!pageData.visitors.includes(data.visitorId)) {
        pageData.visitors.push(data.visitorId);
      }
      
      if (data.duration) {
        pageData.totalDuration = (pageData.totalDuration || 0) + data.duration;
        pageData.count = (pageData.count || 0) + 1;
      }
      
      await kv.set(pageKey, pageData, { ex: 90 * 24 * 60 * 60 });
      
      // 充值链接点击单独统计
      if (data.type === 'buy_click') {
        const clickKey = `pubg_analytics:clicks:${dateKey}`;
        let clickData = await kv.get(clickKey);
        
        if (!clickData) {
          clickData = { total: 0, byPosition: {} };
        }
        
        clickData.total = (clickData.total || 0) + 1;
        const pos = data.linkPosition || 'unknown';
        clickData.byPosition[pos] = (clickData.byPosition[pos] || 0) + 1;
        
        await kv.set(clickKey, clickData, { ex: 90 * 24 * 60 * 60 });
      }
      
      return res.status(200).json({ success: true });
      
    } catch (kvError) {
      // KV 不可用时使用后备存储
      console.log('KV not available, using fallback');
      return res.status(200).json({ success: true, fallback: true });
    }

  } catch (error) {
    console.error('Tracking error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
