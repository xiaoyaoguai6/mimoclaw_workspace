/* ===== AI交易员 - 完整交互层 ===== */

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

// ===== Tab 切换通用 =====
function initTabGroups() {
  document.querySelectorAll('[data-tab-group]').forEach(group => {
    group.querySelectorAll('[data-tab]').forEach(tab => {
      tab.addEventListener('click', () => {
        group.querySelectorAll('[data-tab]').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        // 触发自定义事件
        group.dispatchEvent(new CustomEvent('tabChange', { detail: { tab: tab.dataset.tab } }));
      });
    });
  });
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

  // 来源筛选
  document.querySelectorAll('.source-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.source-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // 级别筛选
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

// ===== 设置页 =====
function initSettings() {
  // 左侧导航
  document.querySelectorAll('.settings-nav-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      // 显示对应section
      const target = item.dataset.section;
      document.querySelectorAll('.settings-section-block').forEach(s => {
        s.style.display = s.dataset.section === target ? '' : 'none';
      });
    });
  });

  // 资金预设
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const input = document.querySelector('.amount-input');
      if (input && btn.dataset.amount) input.value = btn.dataset.amount;
    });
  });

  // 板块选择
  document.querySelectorAll('.sector-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sector-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // 滑块
  document.querySelectorAll('input[type="range"]').forEach(slider => {
    const display = document.getElementById(slider.dataset.display);
    if (display) {
      slider.addEventListener('input', () => {
        display.textContent = slider.value + '%';
      });
    }
  });

  // 保存按钮
  const saveBtn = document.querySelector('.save-btn');
  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      saveBtn.textContent = '✓ 已保存';
      saveBtn.style.background = 'linear-gradient(135deg, #16a34a, #22c55e)';
      setTimeout(() => {
        saveBtn.innerHTML = '<i class="ri-save-line" style="margin-right:0.375rem"></i>保存并通知 AI 重新校准';
        saveBtn.style.background = '';
      }, 2000);
    });
  }
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

// ===== 持仓页筛选 =====
function initPositions() {
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const filter = chip.dataset.filter;
      document.querySelectorAll('.positions-table tbody tr').forEach(row => {
        if (filter === 'all') { row.style.display = ''; return; }
        row.style.display = row.dataset.pnl === filter ? '' : 'none';
      });
    });
  });

  // 卖出按钮
  document.querySelectorAll('.sell-btn-mini').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      btn.textContent = '确认中...';
      btn.disabled = true;
      setTimeout(() => {
        btn.textContent = '已提交';
        btn.style.background = 'rgba(22,163,74,0.1)';
        btn.style.color = '#16a34a';
        btn.style.borderColor = 'rgba(22,163,74,0.3)';
      }, 800);
    });
  });
}

// ===== 报表页 =====
function initReports() {
  document.querySelectorAll('.period-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.period-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });

  document.querySelectorAll('.return-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.return-tab').forEach(t => t.classList.remove('active'));
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

// ===== AI 对话框 =====
function initAIChat() {
  const trigger = document.querySelector('.ai-chat-btn');
  const dialog = document.querySelector('.ai-chat-dialog');
  const closeBtn = document.querySelector('.ai-chat-close');
  const pauseBtn = document.querySelector('.ai-chat-pause');
  if (!trigger || !dialog) return;

  trigger.addEventListener('click', () => {
    dialog.classList.toggle('show');
    trigger.style.display = dialog.classList.contains('show') ? 'none' : '';
  });
  if (closeBtn) closeBtn.addEventListener('click', () => {
    dialog.classList.remove('show');
    trigger.style.display = '';
  });
  if (pauseBtn) pauseBtn.addEventListener('click', () => {
    const icon = pauseBtn.querySelector('i');
    if (icon?.classList.contains('ri-pause-line')) {
      icon.className = 'ri-play-line';
      pauseBtn.querySelector('span').textContent = '继续';
    } else {
      icon.className = 'ri-pause-line';
      pauseBtn.querySelector('span').textContent = '暂停';
    }
  });

  // 快捷问题
  document.querySelectorAll('.quick-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = dialog.querySelector('textarea');
      if (input) {
        input.value = btn.textContent;
        input.focus();
      }
    });
  });

  // 发送消息
  const sendBtn = dialog.querySelector('.ai-send-btn');
  const textarea = dialog.querySelector('textarea');
  if (sendBtn && textarea) {
    const doSend = () => {
      const text = textarea.value.trim();
      if (!text) return;
      // 添加用户消息
      const userMsg = document.createElement('div');
      userMsg.className = 'ai-msg user';
      userMsg.innerHTML = `<div class="ai-msg-bubble">${text}</div>`;
      const msgList = dialog.querySelector('.ai-chat-messages');
      msgList?.appendChild(userMsg);
      textarea.value = '';
      // 模拟AI回复
      setTimeout(() => {
        const botMsg = document.createElement('div');
        botMsg.className = 'ai-msg bot';
        botMsg.innerHTML = `<div class="ai-msg-avatar"><i class="ri-robot-2-line"></i></div><div class="ai-msg-bubble">收到，正在分析中…</div>`;
        msgList?.appendChild(botMsg);
        msgList?.scrollTo(0, msgList.scrollHeight);
      }, 800);
    };
    sendBtn.addEventListener('click', doSend);
    textarea.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doSend(); }
    });
  }
}

// ===== 客服组件 =====
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
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href')?.split('/').pop();
    if (href === path || (path === 'index.html' && href === 'dashboard.html')) {
      link.classList.add('active');
    }
  });
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
  startTimeUpdate();
  highlightActiveLink();
});
