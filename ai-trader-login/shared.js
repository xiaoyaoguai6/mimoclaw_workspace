/**
 * AI交易员 - 共享交互层 (完整版)
 * 集成: 侧边栏/下拉菜单/AI对话(真实API)/客服/数据联动
 */

// ===== 侧边栏 =====
function toggleSidebar() {
  document.querySelector('.app-sidebar')?.classList.toggle('open');
}
document.addEventListener('click', e => {
  const sb = document.querySelector('.app-sidebar');
  const btn = document.querySelector('.mobile-menu-btn');
  if (sb?.classList.contains('open') && !sb.contains(e.target) && !btn?.contains(e.target)) sb.classList.remove('open');
});

// ===== 用户下拉菜单 =====
function initUserDropdown() {
  const trigger = document.querySelector('.user-info');
  const dropdown = document.querySelector('.user-dropdown');
  if (!trigger || !dropdown) return;
  trigger.addEventListener('click', e => {
    e.stopPropagation();
    dropdown.classList.toggle('show');
  });
  document.addEventListener('click', () => dropdown.classList.remove('show'));
}

// ===== 风险提示 =====
function toggleRiskBanner(btn) {
  const body = btn.closest('.risk-banner')?.querySelector('.risk-body');
  const arrow = btn.querySelector('.arrow');
  if (!body) return;
  const hidden = body.style.display === 'none';
  body.style.display = hidden ? '' : 'none';
  if (arrow) arrow.style.transform = hidden ? 'rotate(0deg)' : 'rotate(180deg)';
}

// ===== Toast 通知 =====
function showToast(msg, duration = 2500) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

// ===== Tab 切换通用 =====
function initTabGroups() {
  document.querySelectorAll('[data-tab-group]').forEach(group => {
    group.querySelectorAll('[data-tab]').forEach(tab => {
      tab.addEventListener('click', () => {
        group.querySelectorAll('[data-tab]').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        group.dispatchEvent(new CustomEvent('tabChange', { detail: { tab: tab.dataset.tab } }));
      });
    });
  });
}

// ===== 时间更新 =====
function startTimeUpdate() {
  const update = () => {
    const el = document.getElementById('headerTime');
    if (el) el.textContent = new Date().toLocaleTimeString('zh-CN', { hour12: false });
  };
  update();
  setInterval(update, 1000);
}

// ===== 高亮当前页面 =====
function highlightActiveLink() {
  const path = (location.pathname.split('/').pop() || 'index.html').split('?')[0];
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href')?.split('/').pop();
    if (href === path || (path === 'index.html' && href === 'dashboard.html')) {
      link.classList.add('active');
    }
  });
}

// ===== AI 对话框 (接入 mimov2.5pro) =====
function initAIChat() {
  const trigger = document.querySelector('.ai-chat-btn');
  const dialog = document.querySelector('.ai-chat-dialog');
  const closeBtn = document.querySelector('.ai-chat-close');
  const pauseBtn = document.querySelector('.ai-chat-pause');
  if (!trigger || !dialog) return;

  // 对话历史
  let chatHistory = [
    { role: 'system', content: AI_SYSTEM_PROMPTS.trader }
  ];

  trigger.addEventListener('click', () => {
    dialog.classList.toggle('show');
    trigger.style.display = dialog.classList.contains('show') ? 'none' : '';
    if (dialog.classList.contains('show')) {
      const textarea = dialog.querySelector('textarea');
      if (textarea) textarea.focus();
    }
  });
  if (closeBtn) closeBtn.addEventListener('click', () => {
    dialog.classList.remove('show');
    trigger.style.display = '';
  });
  if (pauseBtn) pauseBtn.addEventListener('click', () => {
    const icon = pauseBtn.querySelector('i');
    if (icon?.classList.contains('ri-pause-line')) {
      icon.className = 'ri-play-line';
    } else {
      icon.className = 'ri-pause-line';
    }
  });

  // 快捷问题
  document.querySelectorAll('.quick-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = dialog.querySelector('textarea');
      if (input) {
        input.value = btn.textContent;
        input.focus();
        autoResize(input);
      }
    });
  });

  // 发送消息
  const sendBtn = dialog.querySelector('.ai-send-btn');
  const textarea = dialog.querySelector('textarea');

  function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 80) + 'px';
  }

  if (textarea) {
    textarea.addEventListener('input', () => autoResize(textarea));
  }

  const doSend = async () => {
    const text = textarea?.value?.trim();
    if (!text) return;

    const msgList = dialog.querySelector('.ai-chat-messages');
    if (!msgList) return;

    // 添加用户消息
    const userMsg = document.createElement('div');
    userMsg.className = 'ai-msg user';
    userMsg.innerHTML = `<div class="ai-msg-bubble">${escapeHtml(text)}</div>`;
    msgList.appendChild(userMsg);
    textarea.value = '';
    autoResize(textarea);
    msgList.scrollTo(0, msgList.scrollHeight);

    // 添加 AI 占位
    const botMsg = document.createElement('div');
    botMsg.className = 'ai-msg bot';
    botMsg.innerHTML = `<div class="ai-msg-avatar"><i class="ri-robot-2-line"></i></div><div class="ai-msg-bubble"><span class="typing-dots">思考中</span></div>`;
    msgList.appendChild(botMsg);
    msgList.scrollTo(0, msgList.scrollHeight);

    // 准备上下文
    const acc = DataStore.getAccount();
    const contextMsg = `当前账户信息：
总资产: ¥${acc.totalAsset?.toLocaleString('zh-CN', {minimumFractionDigits:2})}
可用资金: ¥${acc.available?.toLocaleString('zh-CN', {minimumFractionDigits:2})}
持仓: ${acc.positions.map(p => `${p.name}(${p.code}) ${p.qty}股 成本¥${p.avgCost} 现价¥${p.currentPrice}`).join('; ') || '空仓'}
总盈亏: ¥${acc.totalPnl?.toLocaleString('zh-CN', {minimumFractionDigits:2})} (${acc.totalPnlPct?.toFixed(2)}%)`;

    chatHistory.push({ role: 'system', content: contextMsg });
    chatHistory.push({ role: 'user', content: text });

    // 保持历史不超过20条
    if (chatHistory.length > 22) {
      chatHistory = [chatHistory[0], ...chatHistory.slice(-20)];
    }

    // 流式调用 AI
    const bubble = botMsg.querySelector('.ai-msg-bubble');
    let fullText = '';

    await callAIStream(chatHistory,
      (chunk) => {
        fullText += chunk;
        bubble.innerHTML = formatAIReply(fullText);
        msgList.scrollTo(0, msgList.scrollHeight);
      },
      () => {
        if (!fullText) bubble.innerHTML = '[无回复]';
        chatHistory.push({ role: 'assistant', content: fullText });
        msgList.scrollTo(0, msgList.scrollHeight);
      }
    );
  };

  if (sendBtn) sendBtn.addEventListener('click', doSend);
  if (textarea) textarea.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doSend(); }
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatAIReply(text) {
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

// ===== 客服组件 (接入 AI) =====
function initCustomerService() {
  const minimizeBtn = document.querySelector('.cs-minimize');
  const messages = document.querySelector('.cs-messages');
  const inputArea = document.querySelector('.cs-input-area');

  if (minimizeBtn) {
    minimizeBtn.addEventListener('click', () => {
      const hidden = messages?.style.display === 'none';
      if (messages) messages.style.display = hidden ? '' : 'none';
      if (inputArea) inputArea.style.display = hidden ? '' : 'none';
    });
  }

  // 客服对话接入 AI
  const csInput = inputArea?.querySelector('textarea');
  const csSendBtn = inputArea?.querySelector('.send-btn');
  let csHistory = [{ role: 'system', content: AI_SYSTEM_PROMPTS.customerService }];

  if (csInput) {
    csInput.addEventListener('input', () => {
      if (csSendBtn) csSendBtn.disabled = !csInput.value.trim();
      csInput.style.height = 'auto';
      csInput.style.height = Math.min(csInput.scrollHeight, 80) + 'px';
    });
  }

  const doCsSend = async () => {
    const text = csInput?.value?.trim();
    if (!text || !messages) return;

    // 用户消息
    const userDiv = document.createElement('div');
    userDiv.className = 'cs-msg user';
    const now = new Date().toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit' });
    userDiv.innerHTML = `<div><div class="bubble">${escapeHtml(text)}</div><div class="time">${now}</div></div>`;
    messages.appendChild(userDiv);
    csInput.value = '';
    if (csSendBtn) csSendBtn.disabled = true;
    messages.scrollTo(0, messages.scrollHeight);

    // AI 占位
    const botDiv = document.createElement('div');
    botDiv.className = 'cs-msg bot';
    botDiv.innerHTML = `<div class="bot-avatar"><i class="ri-customer-service-2-line"></i></div><div><div class="bubble">正在回复...</div><div class="time">${now}</div></div>`;
    messages.appendChild(botDiv);
    messages.scrollTo(0, messages.scrollHeight);

    csHistory.push({ role: 'user', content: text });
    if (csHistory.length > 12) csHistory = [csHistory[0], ...csHistory.slice(-10)];

    const bubble = botDiv.querySelector('.bubble');
    let fullText = '';

    await callAIStream(csHistory,
      (chunk) => { fullText += chunk; bubble.innerHTML = formatAIReply(fullText); messages.scrollTo(0, messages.scrollHeight); },
      () => { if (!fullText) bubble.innerHTML = '暂无回复'; csHistory.push({ role: 'assistant', content: fullText }); }
    );
  };

  if (csSendBtn) csSendBtn.addEventListener('click', doCsSend);
  if (csInput) csInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doCsSend(); }
  });
}

// ===== 持仓页筛选 =====
function initPositions() {
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
    });
  });

  document.querySelectorAll('.sell-btn-mini').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const row = btn.closest('tr');
      const code = row?.querySelector('.stock-code')?.textContent;
      if (!code) return;
      btn.textContent = '确认中...';
      btn.disabled = true;
      setTimeout(() => {
        const result = DataStore.removePosition(code, 999999);
        if (result) {
          showToast(`卖出成功，盈亏 ¥${result.pnl.toFixed(2)}`);
          btn.textContent = '已卖出';
          btn.style.background = 'rgba(22,163,74,0.1)';
          btn.style.color = '#16a34a';
          btn.style.borderColor = 'rgba(22,163,74,0.3)';
        }
      }, 500);
    });
  });
}

// ===== 模拟交易页 =====
function initSimtrade() {
  // 买卖切换
  document.querySelectorAll('.trade-type-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.trade-type-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const type = tab.dataset.type;
      const btn = document.getElementById('submitBtn');
      if (btn) {
        btn.className = type === 'buy' ? 'submit-trade buy-btn' : 'submit-trade sell-btn';
        btn.textContent = type === 'buy' ? '买入' : '卖出';
      }
    });
  });

  // 快捷数量
  document.querySelectorAll('.qty-shortcut').forEach(btn => {
    btn.addEventListener('click', () => {
      const qtyInput = document.getElementById('qtyInput');
      if (qtyInput && btn.dataset.qty) {
        qtyInput.value = btn.dataset.qty;
        updateEstAmount();
      }
    });
  });

  // 预估金额计算
  const qtyInput = document.getElementById('qtyInput');
  const priceInput = document.getElementById('priceInput');
  if (qtyInput) qtyInput.addEventListener('input', updateEstAmount);
  if (priceInput) priceInput.addEventListener('input', updateEstAmount);

  // 提交
  const submitBtn = document.getElementById('submitBtn');
  if (submitBtn) {
    submitBtn.addEventListener('click', () => {
      const orig = submitBtn.textContent;
      submitBtn.textContent = '提交中...';
      submitBtn.disabled = true;
      setTimeout(() => {
        submitBtn.textContent = '✓ 已提交';
        setTimeout(() => {
          submitBtn.textContent = orig;
          submitBtn.disabled = false;
        }, 1500);
      }, 800);
    });
  }
}

function updateEstAmount() {
  const price = parseFloat(document.getElementById('priceInput')?.value) || 0;
  const qty = parseInt(document.getElementById('qtyInput')?.value) || 0;
  const el = document.getElementById('estAmount');
  if (el) el.textContent = '¥' + (price * qty).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ===== 设置页 =====
function initSettings() {
  document.querySelectorAll('.settings-nav-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      const target = item.dataset.section;
      document.querySelectorAll('.settings-section-block').forEach(s => {
        s.style.display = s.dataset.section === target ? '' : 'none';
      });
    });
  });

  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const input = document.querySelector('.amount-input');
      if (input && btn.dataset.amount) input.value = btn.dataset.amount;
    });
  });

  document.querySelectorAll('.sector-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sector-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  document.querySelectorAll('input[type="range"]').forEach(slider => {
    const display = document.getElementById(slider.dataset.display);
    if (display) {
      slider.addEventListener('input', () => {
        display.textContent = slider.value + '%';
      });
    }
  });

  const saveBtn = document.querySelector('.save-btn');
  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      saveBtn.textContent = '✓ 已保存';
      saveBtn.style.background = 'linear-gradient(135deg, #16a34a, #22c55e)';
      showToast('设置已保存，AI 正在重新校准策略...');
      setTimeout(() => {
        saveBtn.innerHTML = '<i class="ri-save-line" style="margin-right:0.375rem"></i>保存并通知 AI 重新校准';
        saveBtn.style.background = '';
      }, 2000);
    });
  }
}

// ===== 报表页 =====
function initReports() {
  document.querySelectorAll('.period-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.period-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });

  const exportBtn = document.querySelector('.export-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      exportBtn.innerHTML = '<i class="ri-loader-4-line" style="animation:spin 1s linear infinite"></i> 生成中...';
      setTimeout(() => {
        exportBtn.innerHTML = '<i class="ri-check-line"></i> 已就绪';
        setTimeout(() => {
          exportBtn.innerHTML = '<i class="ri-download-cloud-line"></i> 导出PDF';
        }, 2000);
      }, 1500);
    });
  }
}

// ===== 新闻页 Tab =====
function initNewsTabs() {
  const mainTabs = document.querySelectorAll('.news-main-tab');
  const hotSection = document.getElementById('hotNewsSection');
  const monitorSection = document.getElementById('monitorSection');
  mainTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      mainTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      if (tab.dataset.section === 'hot') {
        if (hotSection) hotSection.style.display = '';
        if (monitorSection) monitorSection.style.display = 'none';
      } else {
        if (hotSection) hotSection.style.display = 'none';
        if (monitorSection) monitorSection.style.display = '';
      }
    });
  });

  document.querySelectorAll('.source-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.source-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  document.querySelectorAll('.level-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.level-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const level = btn.dataset.level;
      document.querySelectorAll('.news-item').forEach(item => {
        if (level === 'all') { item.style.display = ''; return; }
        item.style.display = item.dataset.level === level ? '' : 'none';
      });
    });
  });
}

// ===== 股票代码搜索 =====
function initStockSearch() {
  const searchInputs = document.querySelectorAll('.stock-search-input');
  searchInputs.forEach(input => {
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      const list = input.closest('.watchlist-panel, .stock-list-panel')?.querySelectorAll('.wl-item, .stock-item');
      list?.forEach(item => {
        const name = item.querySelector('.wl-name, .si-name')?.textContent?.toLowerCase() || '';
        const code = item.querySelector('.wl-code, .si-code')?.textContent?.toLowerCase() || '';
        item.style.display = (!q || name.includes(q) || code.includes(q)) ? '' : 'none';
      });
    });
  });
}

// ===== 格式化工具 =====
function fmt(n, decimals = 2) {
  if (n == null || isNaN(n)) return '—';
  return n.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}
function fmtPct(n) {
  if (n == null || isNaN(n)) return '—';
  const sign = n > 0 ? '+' : '';
  return sign + n.toFixed(2) + '%';
}
function fmtMoney(n) {
  if (n == null || isNaN(n)) return '—';
  return '¥' + fmt(n);
}

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
  initUserDropdown();
  initTabGroups();
  initNewsTabs();
  initSettings();
  initSimtrade();
  initPositions();
  initReports();
  initAIChat();
  initCustomerService();
  initStockSearch();
  startTimeUpdate();
  highlightActiveLink();
});
