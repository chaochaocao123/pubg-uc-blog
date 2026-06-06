/**
 * 数据分析工具 - 页面访问追踪
 */

const RECHARGE_URL = 'https://www.z2u.com/r/anhao';
let visitorId = null;
let sessionId = null;
let pageStartTime = null;

// 生成唯一标识
function generateId() {
  return 'v_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// 获取或创建访客ID
function getVisitorId() {
  if (!visitorId) {
    visitorId = localStorage.getItem('pubg_uc_visitor_id');
    if (!visitorId) {
      visitorId = generateId();
      localStorage.setItem('pubg_uc_visitor_id', visitorId);
    }
  }
  return visitorId;
}

// 获取或创建会话ID
function getSessionId() {
  if (!sessionId) {
    sessionId = sessionStorage.getItem('pubg_uc_session_id');
    if (!sessionId) {
      sessionId = generateId();
      sessionStorage.setItem('pubg_uc_session_id', sessionId);
    }
  }
  return sessionId;
}

// 追踪页面访问
async function trackPageView(page, pageTitle) {
  // 发送到GA4（自动通过config的page_view事件）
  sendGA4Event('page_view', {
    page_path: page,
    page_title: pageTitle || document.title,
    page_location: window.location.href
  });

  const data = {
    page: page,
    pageTitle: pageTitle || document.title,
    visitorId: getVisitorId(),
    sessionId: getSessionId(),
    referrer: document.referrer || 'direct',
    type: 'pv'
  };

  await sendTrackingData(data);
}

// 追踪充值链接点击
async function trackBuyClick(position, linkText) {
  // 发送到GA4
  sendGA4Event('recharge_click', {
    link_position: position || 'unknown',
    link_text: linkText || 'UC充值',
    link_url: RECHARGE_URL,
    page_path: window.location.pathname,
    page_title: document.title
  });

  const data = {
    page: window.location.pathname,
    pageTitle: document.title,
    visitorId: getVisitorId(),
    sessionId: getSessionId(),
    type: 'buy_click',
    buyLink: RECHARGE_URL,
    linkText: linkText || 'UC充值',
    linkPosition: position || 'unknown'
  };

  await sendTrackingData(data);
}

// 追踪阅读时长
async function trackReadTime(duration) {
  // 发送到GA4
  sendGA4Event('read_time', {
    duration_seconds: duration,
    page_path: window.location.pathname,
    page_title: document.title
  });

  const data = {
    page: window.location.pathname,
    pageTitle: document.title,
    visitorId: getVisitorId(),
    sessionId: getSessionId(),
    type: 'read_time',
    duration: duration
  };

  await sendTrackingData(data);
}

// 发送追踪数据
async function sendTrackingData(data) {
  try {
    // 发送到自建API（保留兼容）
    const params = new URLSearchParams(data);
    await fetch('/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  } catch (error) {
    // 静默失败，不影响用户体验
  }
}

// 发送到 Google Analytics 4
function sendGA4Event(eventName, params) {
  if (typeof gtag === 'function') {
    gtag('event', eventName, params);
  }
}

// 初始化追踪
function initTracking() {
  // 页面加载时追踪
  pageStartTime = Date.now();
  trackPageView(window.location.pathname, document.title);
  
  // 页面离开时追踪阅读时长
  window.addEventListener('beforeunload', () => {
    const duration = Math.round((Date.now() - pageStartTime) / 1000);
    if (duration > 5) {
      trackReadTime(duration);
    }
  });
  
  // 追踪所有充值链接点击
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href*="z2u.com"]');
    if (link) {
      let position = 'unknown';
      
      // 判断位置
      if (link.classList.contains('hero-cta')) {
        position = 'hero';
      } else if (link.classList.contains('recharge-btn')) {
        position = 'sidebar';
      } else if (link.classList.contains('nav-cta')) {
        position = 'nav';
      } else if (link.closest('.recharge-banner')) {
        position = 'banner';
      } else if (link.closest('.article-cta')) {
        position = 'article_bottom';
      } else if (link.closest('.footer')) {
        position = 'footer';
      }
      
      trackBuyClick(position, link.textContent.trim());
    }
  });
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTracking);
} else {
  initTracking();
}
