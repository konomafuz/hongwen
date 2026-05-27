document.addEventListener('DOMContentLoaded', () => {
  
  // ── 1. Color Theme Toggle Sync ──
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    // Sync current visual state of disc toggle indicator
    const currentTheme = document.documentElement.getAttribute('data-theme');
    if (currentTheme === 'cyan') {
      themeToggle.classList.add('active');
    }
    
    themeToggle.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme');
      if (activeTheme === 'cyan') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.removeItem('hw-theme');
        themeToggle.classList.remove('active');
      } else {
        document.documentElement.setAttribute('data-theme', 'cyan');
        localStorage.setItem('hw-theme', 'cyan');
        themeToggle.classList.add('active');
      }
    });
  }

  // ── 2. Sidebar Collapse Fold/Unfold ──
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  
  if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      
      // Store state in localStorage
      const isCollapsed = sidebar.classList.contains('collapsed');
      localStorage.setItem('hw-sidebar-collapsed', isCollapsed ? 'true' : 'false');
    });
    
    // Restore sidebar state from previous session
    const savedSidebarState = localStorage.getItem('hw-sidebar-collapsed');
    if (savedSidebarState === 'true') {
      sidebar.classList.add('collapsed');
    }
  }

  // ── 3. Workspace Views Switcher ──
  const viewPanes = document.querySelectorAll('.view-pane');
  const menuItems = document.querySelectorAll('.menu-item');
  
  function switchView(viewName) {
    // Fade out active pane
    viewPanes.forEach(pane => {
      pane.classList.remove('active');
    });
    
    // Switch active pane
    const targetPane = document.getElementById(`view-${viewName}`);
    if (targetPane) {
      targetPane.classList.add('active');
    }
    
    // Update sidebar menu active state
    menuItems.forEach(item => {
      item.classList.remove('active');
      if (item.getAttribute('data-view') === viewName) {
        item.classList.add('active');
      }
    });

    // Auto scroll workspace back to top
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.scrollTop = 0;
    }
  }
  
  // Bind click events on sidebar items
  menuItems.forEach(item => {
    const viewName = item.getAttribute('data-view');
    if (viewName && viewName !== 'alert') {
      item.addEventListener('click', () => {
        switchView(viewName);
      });
    }
  });

  // Bind clicks on Home view action triggers
  const cardNovelWriting = document.getElementById('card-novel-writing');
  if (cardNovelWriting) {
    cardNovelWriting.addEventListener('click', () => {
      switchView('editor');
    });
  }
  
  // Bind click on "继续创作" button on the first card
  const recentWorkBtn = document.querySelector('.work-card:first-child .work-btn');
  if (recentWorkBtn) {
    recentWorkBtn.addEventListener('click', () => {
      switchView('editor');
    });
  }
  
  // Bind click on Back button in Editor mockup
  const editorBackBtn = document.getElementById('editor-back-btn');
  if (editorBackBtn) {
    editorBackBtn.addEventListener('click', () => {
      switchView('home');
    });
  }

  // ── 4. Custom Modal Alerts for Pending Features ──
  const modal = document.getElementById('notification-modal');
  const modalMessage = document.getElementById('modal-message');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalOkBtn = document.getElementById('modal-ok-btn');
  
  function showModal(title) {
    if (modal && modalMessage) {
      modalMessage.textContent = `【${title}】功能模块正在全力开发中，敬请期待！`;
      modal.classList.add('visible');
    }
  }
  
  function hideModal() {
    if (modal) {
      modal.classList.remove('visible');
    }
  }
  
  // Bind clicks on action items requiring custom modal triggers
  document.querySelectorAll('[data-action="alert"]').forEach(element => {
    element.addEventListener('click', (e) => {
      e.stopPropagation();
      const title = element.getAttribute('data-title') || '新功能';
      showModal(title);
    });
  });
  
  if (modalCloseBtn) modalCloseBtn.addEventListener('click', hideModal);
  if (modalOkBtn) modalOkBtn.addEventListener('click', hideModal);
  
  // Close modal when clicking outside card bounds
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        hideModal();
      }
    });
  }
});
