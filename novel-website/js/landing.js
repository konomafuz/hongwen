document.addEventListener('DOMContentLoaded', () => {
  // 生成萤火虫粒子
  const heroSection = document.getElementById('hero');
  if (heroSection) {
    for (let i = 0; i < 15; i++) {
      const firefly = document.createElement('div');
      firefly.classList.add('firefly');
      // 随机位置和动画延迟
      const top = Math.random() * 100;
      const left = Math.random() * 100;
      const delay = Math.random() * 5;
      const duration = 4 + Math.random() * 4;
      
      firefly.style.top = `${top}%`;
      firefly.style.left = `${left}%`;
      firefly.style.width = `${Math.random() * 4 + 2}px`;
      firefly.style.height = firefly.style.width;
      firefly.style.animationDuration = `${duration}s`;
      firefly.style.animationDelay = `${delay}s`;
      
      heroSection.appendChild(firefly);
    }
  }

  // Scroll Reveal 逻辑
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.scroll-reveal').forEach(el => {
    observer.observe(el);
  });

  // CLI 终端打字机动画逻辑
  const terminalBody = document.getElementById('cli-body');
  if (terminalBody) {
    const commands = [
      { type: 'cmd', text: 'init' },
      { type: 'out', text: '[ 1/2 ] 正在生成大纲与设定，系统深度初始化中...', delay: 1200 },
      { type: 'success', text: '>> 核心人物设定与主线大纲已成功导出。', delay: 800 },
      { type: 'out', text: '[ 2/2 ] 正在根据大纲构建匹配的作品标签与简介文档...', delay: 1200 },
      { type: 'success', text: '>> 三版简介与推荐标签已完成保存。', delay: 800 },
      { type: 'success', text: '>> 项目初始化完毕，可输入 write 开始创作。', delay: 800 },
      
      { type: 'cmd', text: 'write' },
      { type: 'out', text: '[ 1/3 ] 正在检索当前大纲设定，自动加载智能语感数据库...', delay: 1200 },
      { type: 'out', text: '[ 2/3 ] 正在开始生成第一章正文，智能联想续写中 (约2000字)...', delay: 1500 },
      { type: 'success', text: '>> 第一章正文初稿已生成完毕。', delay: 800 },
      { type: 'out', text: '[ 3/3 ] 正在进行内容深度自审，排除AI化机械语调，精细打磨细节...', delay: 1200 },
      { type: 'success', text: '>> 智能降AI味及文风润色完成，句子通顺度显著提升。', delay: 1000 },
      { type: 'success', text: '>> 第一章定稿成功，格式已整理就绪。', delay: 800 }
    ];

    const bannerText = `    ██╗  ██╗ ██████╗ ███╗   ██╗ ██████╗ ██╗    ██╗███████╗███╗   ██╗
    ██║  ██║██╔═══██╗████╗  ██║██╔════╝ ██║    ██║██╔════╝████╗  ██║
    ███████║██║   ██║██╔██╗ ██║██║  ███╗██║ █╗ ██║█████╗  ██╔██╗ ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║██║███╗██║██╔══╝  ██║╚██╗██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝╚███╔███╔╝███████╗██║ ╚████║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═══╝`;

    // 辅助函数：创建并添加样式化的 Prompt
    function createPromptElement() {
      const prompt = document.createElement('span');
      prompt.classList.add('terminal-prompt');
      prompt.textContent = 'hw ❯ ';
      return prompt;
    }

    async function typeWriter() {
      // 清空控制台
      terminalBody.innerHTML = '';
      
      // 1. 插入 Logo Banner
      const bannerPre = document.createElement('pre');
      bannerPre.classList.add('terminal-banner');
      bannerPre.textContent = bannerText;
      terminalBody.appendChild(bannerPre);
      
      // 2. 欢迎信息
      const welcomeLine1 = document.createElement('div');
      welcomeLine1.classList.add('terminal-line');
      welcomeLine1.style.color = 'var(--hw-primary)';
      welcomeLine1.textContent = '红文织梦智能 AI 写作系统 [版本 0.2.0]';
      terminalBody.appendChild(welcomeLine1);
      
      const welcomeLine2 = document.createElement('div');
      welcomeLine2.classList.add('terminal-line');
      welcomeLine2.style.color = 'rgba(255, 255, 255, 0.5)';
      welcomeLine2.style.marginBottom = '20px';
      welcomeLine2.textContent = '系统加载完毕，已连接灵感工坊。正在构建沉浸式心流环境...';
      terminalBody.appendChild(welcomeLine2);

      terminalBody.scrollTop = terminalBody.scrollHeight;
      await new Promise(r => setTimeout(r, 1000));
      
      for (const step of commands) {
        const line = document.createElement('div');
        line.classList.add('terminal-line');
        
        if (step.type === 'cmd') {
          const prompt = createPromptElement();
          
          const cmdContainer = document.createElement('span');
          cmdContainer.style.display = 'inline-flex';
          cmdContainer.style.alignItems = 'center';
          
          const cmdSpan = document.createElement('span');
          cmdSpan.classList.add('terminal-cmd');
          
          const cursor = document.createElement('span');
          cursor.classList.add('terminal-cursor');
          
          cmdContainer.appendChild(cmdSpan);
          cmdContainer.appendChild(cursor);
          
          line.appendChild(prompt);
          line.appendChild(cmdContainer);
          terminalBody.appendChild(line);
          terminalBody.scrollTop = terminalBody.scrollHeight;
          
          // 逐字打印命令 (放慢速度至 120ms)
          for (let i = 0; i < step.text.length; i++) {
            await new Promise(r => setTimeout(r, 120));
            cmdSpan.textContent += step.text[i];
            terminalBody.scrollTop = terminalBody.scrollHeight;
          }
          await new Promise(r => setTimeout(r, 1000));
          cursor.remove(); // 移除游标
        } else {
          const outSpan = document.createElement('span');
          outSpan.classList.add('terminal-output');
          if (step.type === 'success') outSpan.classList.add('success');
          if (step.type === 'highlight') outSpan.classList.add('highlight');
          outSpan.textContent = step.text;
          line.appendChild(outSpan);
          terminalBody.appendChild(line);
          terminalBody.scrollTop = terminalBody.scrollHeight;
          await new Promise(r => setTimeout(r, step.delay));
        }
      }
      
      // 最后留一个闪烁的游标
      const finalLine = document.createElement('div');
      finalLine.classList.add('terminal-line');
      finalLine.appendChild(createPromptElement());
      
      const finalCursor = document.createElement('span');
      finalCursor.classList.add('terminal-cursor');
      finalLine.appendChild(finalCursor);
      
      terminalBody.appendChild(finalLine);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }
    
    // 延迟 1 秒后开始演示
    setTimeout(typeWriter, 1000);
  }

  // 选项卡切换逻辑
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');
  
  if (tabButtons.length > 0) {
    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        // 切换 active 按钮
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // 切换 active 面板
        const tabId = btn.getAttribute('data-tab');
        tabPanes.forEach(pane => {
          pane.classList.remove('active');
          if (pane.id === `tab-${tabId}`) {
            pane.classList.add('active');
          }
        });
      });
    });
  }

  // 页面背景网格随鼠标移动效果
  const bgGrid = document.querySelector('.bg-ai-nodes');
  if (bgGrid) {
    document.addEventListener('mousemove', (e) => {
      const x = (window.innerWidth / 2 - e.clientX) * 0.03;
      const y = (window.innerHeight / 2 - e.clientY) * 0.03;
      bgGrid.style.transform = `translate(${x}px, ${y}px)`;
    });
  }

  // 色彩主题切换逻辑
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    // 检查本地存储中是否有保存的主题
    const savedTheme = localStorage.getItem('hw-theme');
    if (savedTheme === 'cyan') {
      document.documentElement.setAttribute('data-theme', 'cyan');
    }
    
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      if (currentTheme === 'cyan') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.removeItem('hw-theme');
      } else {
        document.documentElement.setAttribute('data-theme', 'cyan');
        localStorage.setItem('hw-theme', 'cyan');
      }
    });
  }
});
