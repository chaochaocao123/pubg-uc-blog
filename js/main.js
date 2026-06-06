/**
 * 首页主逻辑
 */

// 加载文章数据
async function loadArticles() {
  try {
    const response = await fetch('data/articles.json');
    const data = await response.json();
    
    // 更新统计
    document.getElementById('articleCount').textContent = data.articles.length;
    
    // 更新分类计数
    const counts = { recharge: 0, tips: 0, news: 0, events: 0 };
    data.articles.forEach(article => {
      if (counts.hasOwnProperty(article.category)) {
        counts[article.category]++;
      }
    });
    
    document.getElementById('rechargeCount').textContent = counts.recharge;
    document.getElementById('tipsCount').textContent = counts.tips;
    document.getElementById('newsCount').textContent = counts.news;
    document.getElementById('eventsCount').textContent = counts.events;
    
    // 渲染文章列表
    renderArticles(data.articles);
    
    // 渲染热门文章
    renderPopularArticles(data.articles.slice(0, 3));
    
  } catch (error) {
    console.error('加载文章失败:', error);
    document.getElementById('articlesGrid').innerHTML = '<div class="loading">加载失败，请刷新重试</div>';
  }
}

// 渲染文章列表
function renderArticles(articles, category = 'all') {
  const grid = document.getElementById('articlesGrid');
  
  const filtered = category === 'all' 
    ? articles 
    : articles.filter(a => a.category === category);
  
  if (filtered.length === 0) {
    grid.innerHTML = '<div class="loading">该分类暂无文章</div>';
    return;
  }
  
  grid.innerHTML = filtered.map(article => `
    <article class="article-card">
      <a href="${article.url}">
        <div class="article-image">${article.icon}</div>
        <div class="article-content">
          <span class="article-category category-${article.category}">${getCategoryName(article.category)}</span>
          <h3 class="article-title">${article.title}</h3>
          <p class="article-excerpt">${article.excerpt}</p>
          <div class="article-meta">
            <span class="article-date">📅 ${article.date}</span>
            <span class="article-views">👁 ${article.views || 0} 阅读</span>
          </div>
        </div>
      </a>
    </article>
  `).join('');
}

// 渲染热门文章
function renderPopularArticles(articles) {
  const list = document.getElementById('popularList');
  list.innerHTML = articles.map((article, index) => `
    <li>
      <a href="${article.url}">
        <span class="popular-num">${index + 1}</span>
        <span class="popular-title">${article.title}</span>
      </a>
    </li>
  `).join('');
}

// 获取分类名称
function getCategoryName(category) {
  const names = {
    recharge: '充值教程',
    tips: '游戏技巧',
    news: '游戏资讯',
    events: '活动攻略'
  };
  return names[category] || category;
}

// 分类筛选
function initFilterTabs() {
  const tabs = document.getElementById('filterTabs');
  tabs.addEventListener('click', async (e) => {
    if (e.target.classList.contains('filter-tab')) {
      // 更新激活状态
      tabs.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
      e.target.classList.add('active');
      
      const category = e.target.dataset.category;
      
      // 重新获取数据并筛选
      try {
        const response = await fetch('data/articles.json');
        const data = await response.json();
        renderArticles(data.articles, category);
      } catch (error) {
        console.error('筛选失败:', error);
      }
    }
  });
}

// 移动端菜单
function initMobileMenu() {
  const btn = document.getElementById('mobileMenuBtn');
  const nav = document.querySelector('.nav-links');
  
  btn.addEventListener('click', () => {
    nav.classList.toggle('show');
  });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  loadArticles();
  initFilterTabs();
  initMobileMenu();
});
