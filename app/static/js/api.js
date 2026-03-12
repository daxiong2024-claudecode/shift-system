/**
 * 统一 API 请求封装
 */

const API = {
  async request(url, options = {}) {
    const defaults = {
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
    };
    const config = { ...defaults, ...options };
    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const res = await fetch(url, config);
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `请求失败 (${res.status})`);
      }
      return data;
    } catch (err) {
      if (err.message.includes('401') || err.message.includes('login')) {
        window.location.href = '/login';
      }
      throw err;
    }
  },

  get: (url, params) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return API.request(url + qs);
  },
  post: (url, body) => API.request(url, { method: 'POST', body }),
  put: (url, body) => API.request(url, { method: 'PUT', body }),
  delete: (url) => API.request(url, { method: 'DELETE' }),
};

// ===== Toast 通知 =====
const Toast = {
  container: null,
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(msg, type = 'info', duration = 3000) {
    this.init();
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    this.container.appendChild(el);
    setTimeout(() => el.remove(), duration);
  },
  success: (msg) => Toast.show(msg, 'success'),
  error: (msg) => Toast.show(msg, 'error'),
  info: (msg) => Toast.show(msg, 'info'),
};

// ===== 当前用户信息 =====
let currentUser = null;
async function loadCurrentUser() {
  try {
    const data = await API.get('/auth/me');
    currentUser = data;
    return data;
  } catch {
    window.location.href = '/login';
  }
}

// ===== 侧边栏导航高亮 =====
function highlightNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item[data-path]').forEach(el => {
    el.classList.toggle('active', el.dataset.path === path);
  });
}

// ===== 渲染用户信息到侧边栏 =====
function renderUserInfo(user) {
  const nameEl = document.getElementById('userName');
  const roleEl = document.getElementById('userRole');
  const avatarEl = document.getElementById('userAvatar');
  if (nameEl) nameEl.textContent = user.name;
  if (roleEl) roleEl.textContent = user.role_label;
  if (avatarEl) avatarEl.textContent = user.name[0];
}

// ===== 登出 =====
async function doLogout() {
  await API.post('/auth/logout');
  window.location.href = '/login';
}

// ===== 日期工具 =====
const DateUtil = {
  today: () => new Date().toISOString().slice(0, 10),
  monthStart: () => {
    const d = new Date();
    d.setDate(1);
    return d.toISOString().slice(0, 10);
  },
  weekdays: ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  format: (dateStr) => {
    const d = new Date(dateStr + 'T00:00:00');
    return `${d.getMonth() + 1}/${d.getDate()}`;
  },
  getDaysInMonth: (year, month) => new Date(year, month, 0).getDate(),
};
