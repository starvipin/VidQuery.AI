<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#000000">
  <title>VidQuery.AI</title>

  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23000000'%3E%3Cpath d='M12 3L1 9L4 10.63V17C4 18.66 7.58 20 12 20C16.42 20 20 18.66 20 17V10.63L23 9L12 3ZM12 5.18L18.64 8.82L12 12.45L5.36 8.82L12 5.18ZM18 16.89C18 17.58 15.35 18 12 18C8.65 18 6 17.58 6 16.89V11.72L12 15L18 11.72V16.89Z'/%3E%3C/svg%3E">

  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

    /* --- DARK THEME (Default) --- */
    :root {
      --bg-base: #000000;
      --bg-panel: #0a0a0a;
      --bg-hover: #141414;
      --border-subtle: #1a1a1a;
      --border-focus: #333333;
      --text-main: #ffffff;
      --text-muted: #888888;
      --accent: #ffffff;
      --accent-invert: #000000;
      --noise-opacity: 0.04;
    }

    /* --- LIGHT THEME --- */
    :root[data-theme="light"] {
      --bg-base: #ffffff;
      --bg-panel: #f7f7f8;
      --bg-hover: #f0f0f0;
      --border-subtle: #e5e5e5;
      --border-focus: #cccccc;
      --text-main: #111111;
      --text-muted: #666666;
      --accent: #111111;
      --accent-invert: #ffffff;
      --noise-opacity: 0.02;
    }

    body { 
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
      background: var(--bg-base); 
      color: var(--text-main); 
      height: 100vh; 
      height: 100dvh; 
      overflow: hidden; 
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.4s ease, color 0.4s ease;
    }

    /* Smooth transitions for theme switching */
    .header, .panel, .landing-input-wrapper, .chat-input-container, .message-bubble, .message-avatar, .landing-btn, .video-info {
      transition: background-color 0.4s ease, border-color 0.4s ease, color 0.4s ease;
    }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border-focus); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* Subtle Noise Overlay */
    .noise-overlay {
      position: fixed; inset: 0; z-index: 0; pointer-events: none; 
      opacity: var(--noise-opacity);
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    }

    /* Theme Toggle Button */
    .theme-toggle {
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      width: 32px; height: 32px;
      border-radius: 6px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer;
      transition: background-color 0.2s ease, transform 0.2s ease;
    }
    .theme-toggle:hover {
      background: var(--bg-panel);
    }
    .theme-toggle svg { width: 16px; height: 16px; }
    .sun-icon { display: none; }
    .moon-icon { display: block; }
    
    :root[data-theme="light"] .sun-icon { display: block; }
    :root[data-theme="light"] .moon-icon { display: none; }

    /* -----------------------------------
       LANDING VIEW (Initial Screen)
    ------------------------------------ */
    .landing-view {
      position: relative; z-index: 10;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      height: 100%; width: 100%;
      transition: opacity 0.6s ease, transform 0.6s ease;
    }
    
    .landing-view.hidden {
      opacity: 0; transform: translateY(-20px); pointer-events: none;
    }

    /* Theme toggle absolute position for landing */
    .landing-theme-toggle {
      position: absolute; top: 1.5rem; right: 2rem;
    }

    .brand-hero { text-align: center; margin-bottom: 2.5rem; }
    .brand-hero h1 { font-size: 2.5rem; font-weight: 600; letter-spacing: -0.03em; margin-bottom: 0.5rem; }
    .brand-hero p { color: var(--text-muted); font-size: 0.9375rem; }

    .landing-input-wrapper {
      width: 100%; max-width: 500px;
      display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; 
      background: var(--bg-panel); border: 1px solid var(--border-subtle); 
      border-radius: 8px; 
    }
    .landing-input-wrapper:focus-within { border-color: var(--text-muted); }
    
    .landing-input {
      flex: 1; background: transparent; border: none; outline: none; 
      color: var(--text-main); font-size: 0.9375rem; font-family: 'JetBrains Mono', monospace;
    }
    .landing-input::placeholder { color: var(--text-muted); }
    
    .landing-btn {
      display: flex; align-items: center; justify-content: center; 
      min-width: 100px; padding: 0.6rem 1.2rem; 
      background: var(--accent); color: var(--accent-invert); 
      border: none; border-radius: 4px; font-weight: 500; font-size: 0.875rem; 
      cursor: pointer; 
    }
    .landing-btn:hover { opacity: 0.9; }
    .landing-btn:disabled { opacity: 0.8; cursor: not-allowed; }

    /* AI Thinking Button Animation */
    .ai-thinking-btn { display: flex; align-items: center; gap: 6px; font-weight: 600; }
    .ai-dots { display: flex; gap: 3px; margin-top: 4px; }
    .ai-dot { 
      width: 4px; height: 4px; 
      background-color: var(--accent-invert); 
      border-radius: 50%; 
      animation: aiThink 1.4s infinite ease-in-out both; 
    }
    .ai-dot:nth-child(1) { animation-delay: -0.32s; }
    .ai-dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes aiThink { 
      0%, 80%, 100% { transform: scale(0); opacity: 0.5; } 
      40% { transform: scale(1); opacity: 1; } 
    }

    /* -----------------------------------
       APP VIEW (Chat & Transcript)
    ------------------------------------ */
    .app-view {
      position: absolute; inset: 0; z-index: 5;
      display: flex; flex-direction: column;
      opacity: 0; pointer-events: none; transform: translateY(20px);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }

    .app-view.visible {
      opacity: 1; pointer-events: all; transform: translateY(0);
    }

    /* Minimal Header */
    .header { 
      padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; 
      border-bottom: 1px solid var(--border-subtle); background: var(--bg-base); flex-shrink: 0; 
    }
    .logo-container { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
    .logo-icon { 
      width: 24px; height: 24px; background: var(--text-main); border-radius: 4px; 
      display: flex; align-items: center; justify-content: center; color: var(--bg-base); 
      font-weight: 600; font-size: 14px;
    }
    .logo-text { font-size: 1.125rem; font-weight: 500; letter-spacing: -0.02em; }
    
    .header-actions { display: flex; align-items: center; gap: 1rem; }
    .video-badge { 
      display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; 
      color: var(--text-muted); font-family: 'JetBrains Mono', monospace;
      background: var(--bg-panel); padding: 4px 10px; border-radius: 4px; border: 1px solid var(--border-subtle);
    }

    /* Main Layout - 2 Columns */
    .main-content { 
      flex: 1; display: grid; grid-template-columns: 1fr 380px; 
      overflow: hidden; min-height: 0; 
    }
    @media (max-width: 1024px) { .main-content { grid-template-columns: 1fr; } .transcript-panel { display: none; } }

    .panel { display: flex; flex-direction: column; min-height: 0; height: 100%; background: var(--bg-base); }
    .chat-panel { border-right: 1px solid var(--border-subtle); }

    /* Messages Area */
    .messages-area { 
      flex: 1; overflow-y: auto; padding: 2rem; display: flex; flex-direction: column; 
      gap: 1.5rem; scroll-behavior: smooth; min-height: 0; 
    }

    .message { display: flex; gap: 1rem; animation: fadeIn 0.3s ease-out; width: 100%; }
    .message.user { flex-direction: row-reverse; }
    .message-avatar { 
      width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; 
      justify-content: center; flex-shrink: 0; font-size: 0.75rem; background: var(--bg-panel);
      border: 1px solid var(--border-subtle);
    }
    .message.user .message-avatar { background: var(--text-main); color: var(--bg-base); border: none; }
    .message-content { max-width: 80%; display: flex; flex-direction: column; gap: 0.5rem; }
    .message.user .message-content { align-items: flex-end; }
    
    .message-bubble { font-size: 0.9375rem; line-height: 1.6; color: var(--text-main); }
    .message.user .message-bubble { 
      background: var(--bg-panel); border: 1px solid var(--border-subtle); 
      padding: 0.75rem 1.25rem; border-radius: 8px; border-top-right-radius: 0;
    }
    .message.ai .message-bubble { padding: 0.25rem 0; }
    
    .message-time { font-size: 0.6875rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }

    /* Chat Input */
    .chat-input-section { padding: 1.5rem 2rem; flex-shrink: 0; background: var(--bg-base); }
    .chat-input-container { 
      display: flex; align-items: flex-end; gap: 0.75rem; padding: 0.75rem 1rem; 
      background: var(--bg-panel); border: 1px solid var(--border-subtle); 
      border-radius: 8px; 
    }
    .chat-input-container:focus-within { border-color: var(--text-muted); }
    .chat-input { 
      flex: 1; background: transparent; border: none; outline: none; 
      color: var(--text-main); font-size: 0.9375rem; font-family: inherit; 
      resize: none; max-height: 150px; line-height: 1.5; padding: 4px 0; 
    }
    .chat-input::placeholder { color: var(--text-muted); }
    .send-btn { 
      width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; 
      background: transparent; border: none; color: var(--text-main); cursor: pointer; 
      border-radius: 4px; transition: background 0.2s; flex-shrink: 0;
    }
    .send-btn:hover:not(:disabled) { background: var(--border-subtle); }
    .send-btn:disabled { opacity: 0.3; cursor: not-allowed; }

    /* Transcript Panel */
    .transcript-header { 
      padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-subtle); 
      display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
    }
    .transcript-title h2 { font-size: 0.875rem; font-weight: 500; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #555; display: inline-block; animation: pulse 2s infinite; }
    
    .transcript-content { flex: 1; overflow-y: auto; padding: 1.5rem; min-height: 0; }
    .transcript-empty { 
      display: flex; flex-direction: column; align-items: center; justify-content: center; 
      height: 100%; text-align: center; color: var(--text-muted); font-size: 0.875rem;
    }
    .transcript-text p { 
      font-size: 0.875rem; line-height: 1.8; color: var(--text-muted); 
      margin-bottom: 0.75rem; cursor: pointer; transition: color 0.2s; 
    }
    .transcript-text p:hover { color: var(--text-main); }
    .timestamp { 
      display: inline-block; padding: 2px 6px; margin-right: 8px; 
      background: var(--bg-panel); border: 1px solid var(--border-subtle); 
      border-radius: 4px; font-size: 0.6875rem; color: var(--text-main); 
      font-family: 'JetBrains Mono', monospace; 
    }

    .icon-sm { width: 16px; height: 16px; }

    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body>
  <div class="noise-overlay"></div>

  <!-- 1. LANDING VIEW (Initial Screen) -->
  <div class="landing-view" id="landingView">
    
    <button class="theme-toggle landing-theme-toggle" onclick="toggleTheme()" title="Switch Theme">
      <svg class="sun-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
      <svg class="moon-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
    </button>

    <div class="brand-hero">
      <h1>VidQuery.AI</h1>
      <p>Provide a YouTube URL to extract intelligence.</p>
    </div>
    
    <div class="landing-input-wrapper">
      <svg class="icon-sm" style="color: var(--text-muted);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
      </svg>
      <input type="text" class="landing-input" id="landingInput" placeholder="https://youtube.com/watch?v=...">
      <button class="landing-btn" id="analyzeBtn">Analyze</button>
    </div>
    <div id="landingError" style="color: #ff4444; font-size: 0.875rem; margin-top: 1rem; display: none;"></div>
  </div>

  <!-- 2. APP VIEW (Chat & Transcript) -->
  <div class="app-view" id="appView">
    <!-- Header -->
    <header class="header">
      <div class="logo-container" onclick="window.location.reload()" title="Reset Session">
        <div class="logo-icon">V</div>
        <h1 class="logo-text">VidQuery.AI</h1>
      </div>
      
      <div class="header-actions">
        <div class="video-badge" id="videoTitleBadge">
          <span class="status-dot"></span> Session Active
        </div>
        
        <button class="theme-toggle" onclick="toggleTheme()" title="Switch Theme">
          <svg class="sun-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
          <svg class="moon-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
        </button>
      </div>
    </header>

    <!-- Split Content -->
    <main class="main-content">
      
      <!-- Left: Chat Panel -->
      <div class="panel chat-panel">
        <div class="messages-area" id="messagesArea">
          <!-- Messages will spawn here -->
        </div>

        <div class="chat-input-section">
          <div class="chat-input-container">
            <textarea class="chat-input" id="chatInput" placeholder="Ask anything about the video..." rows="1"></textarea>
            <button class="send-btn" id="sendBtn">
              <svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Transcript Panel -->
      <div class="panel transcript-panel">
        <div class="transcript-header">
          <div class="transcript-title">
            <h2>Transcript Log</h2>
          </div>
        </div>
        <div class="transcript-content" id="transcriptContent">
          <div class="transcript-empty">
            <p>Loading transcript data...</p>
          </div>
        </div>
      </div>

    </main>
  </div>

  <script>
    // --- THEME LOGIC ---
    function initTheme() {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        document.querySelector('meta[name="theme-color"]').setAttribute('content', '#ffffff');
      } else {
        document.documentElement.removeAttribute('data-theme');
        document.querySelector('meta[name="theme-color"]').setAttribute('content', '#000000');
      }
    }
    
    function toggleTheme() {
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';
      if (isLight) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
        document.querySelector('meta[name="theme-color"]').setAttribute('content', '#000000');
      } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        document.querySelector('meta[name="theme-color"]').setAttribute('content', '#ffffff');
      }
    }

    // Initialize Theme immediately
    initTheme();

    // --- DOM Elements ---
    const landingView = document.getElementById('landingView');
    const appView = document.getElementById('appView');
    const landingInput = document.getElementById('landingInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const landingError = document.getElementById('landingError');
    
    const messagesArea = document.getElementById('messagesArea');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const transcriptContent = document.getElementById('transcriptContent');
    const videoTitleBadge = document.getElementById('videoTitleBadge');

    let currentVideoId = null;

    // --- Helpers ---
    function formatTime(date) {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }

    // --- UI Functions ---
    function switchViews() {
      landingView.classList.add('hidden');
      setTimeout(() => {
        landingView.style.display = 'none';
        appView.classList.add('visible');
        chatInput.focus();
      }, 600);
    }

    function addMessage(text, sender, sources = []) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `message ${sender === 'user' ? 'user' : 'ai'}`;
      
      let formattedText = text;
      if (!text.includes('<div class="video-info"')) {
         formattedText = text.replace(/\n/g, '<br>');
      }
      
      const avatarContent = sender === 'user' ? 'U' : 'AI';

      let sourcesHtml = '';
      if (sources && sources.length > 0) {
          sourcesHtml = '<div style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">';
          sources.forEach(src => {
              sourcesHtml += `<span class="timestamp" style="cursor:pointer;" title="Jump to ${src.time}">↳ ${src.time || '00:00'}</span>`;
          });
          sourcesHtml += '</div>';
      }

      msgDiv.innerHTML = `
        <div class="message-avatar">${avatarContent}</div>
        <div class="message-content">
          <div class="message-bubble">${formattedText}${sourcesHtml}</div>
          <div class="message-time">${formatTime(new Date())}</div>
        </div>
      `;
      
      messagesArea.appendChild(msgDiv);
      messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    let typingElement = null;
    function showTyping() {
      if (typingElement) typingElement.remove();
      const typingDiv = document.createElement('div');
      typingDiv.className = 'message ai';
      typingDiv.id = 'typingIndicator';
      typingDiv.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
          <div style="padding: 0.5rem 0; color: var(--text-muted); font-size: 0.875rem;">Processing...</div>
        </div>
      `;
      messagesArea.appendChild(typingDiv);
      messagesArea.scrollTop = messagesArea.scrollHeight;
      typingElement = typingDiv;
    }

    function hideTyping() {
      if (typingElement) {
        typingElement.remove();
        typingElement = null;
      }
    }

    function renderTranscript(transcriptArray) {
      transcriptContent.innerHTML = '';
      if (!transcriptArray || transcriptArray.length === 0) {
          transcriptContent.innerHTML = `<div class="transcript-empty"><p>No captions found for this video.</p></div>`;
          return;
      }

      const textContainer = document.createElement('div');
      textContainer.className = 'transcript-text';

      transcriptArray.forEach(item => {
          const p = document.createElement('p');
          p.innerHTML = `<span class="timestamp">${item.time || '--:--'}</span>${escapeHtml(item.text)}`;
          p.addEventListener('click', () => {
              addMessage(`Context selected at ${item.time} — "${item.text.substring(0, 80)}..."`, 'user');
          });
          textContainer.appendChild(p);
      });
      
      transcriptContent.appendChild(textContainer);
    }

    // --- Main Logic: Analyze Link ---
    analyzeBtn.addEventListener('click', async () => {
        let rawUrl = landingInput.value.trim();
        landingError.style.display = 'none';

        if (!rawUrl) {
            landingError.textContent = "Please provide a valid URL.";
            landingError.style.display = 'block';
            return;
        }
        if (!rawUrl.includes('youtube.com') && !rawUrl.includes('youtu.be')) {
            landingError.textContent = "Only YouTube URLs are supported.";
            landingError.style.display = 'block';
            return;
        }

        analyzeBtn.disabled = true;
        // The new AI Thinking Animation
        analyzeBtn.innerHTML = `
          <div class="ai-thinking-btn">
            Thinking
            <div class="ai-dots">
              <div class="ai-dot"></div>
              <div class="ai-dot"></div>
              <div class="ai-dot"></div>
            </div>
          </div>
        `;
        
        try {
            let videoIdMatch = rawUrl.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/);
            let tempVideoId = videoIdMatch ? videoIdMatch[1] : null;

            const processPromise = fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: rawUrl })
            }).then(res => res.json());

            const noembedPromise = tempVideoId 
                ? fetch(`https://noembed.com/embed?url=https://www.youtube.com/watch?v=${tempVideoId}`).then(res => res.json()).catch(() => ({}))
                : Promise.resolve({});

            const [data, oembedData] = await Promise.all([processPromise, noembedPromise]);

            if (data.success) {
                currentVideoId = data.video_id || tempVideoId;
                
                // Switch Layouts
                switchViews();

                // Setup App View Data
                renderTranscript(data.transcript || []);
                
                let videoTitle = data.title || oembedData.title || "Unknown Video";
                let channelName = data.channel || oembedData.author_name || "Extracted Video";

                // Update Header Badge
                videoTitleBadge.innerHTML = `<span class="status-dot"></span> ${escapeHtml(videoTitle).substring(0,30)}...`;

                // Add Welcome Message in Chat
                const videoCardHtml = `<div class="video-info" style="margin-top: 1rem; background: var(--bg-panel); border: 1px solid var(--border-subtle); display: flex; gap: 12px; padding: 12px; border-radius: 8px;"><img src="https://img.youtube.com/vi/${currentVideoId}/mqdefault.jpg" alt="Thumbnail" style="width: 100px; height: 56px; border-radius: 4px; object-fit: cover; flex-shrink: 0;"><div style="display: flex; flex-direction: column; justify-content: center;"><h3 style="font-size: 0.875rem; font-weight: 500; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; margin-top: 0;">${escapeHtml(videoTitle)}</h3><p style="font-size: 0.75rem; color: var(--text-muted); margin: 0;">${escapeHtml(channelName)}</p></div></div>`;

                setTimeout(() => {
                    addMessage(`Video context loaded successfully. ${data.transcript ? data.transcript.length : 0} captions indexed. ${videoCardHtml} <br><br>What would you like to know?`, "ai");
                }, 800); 

            } else {
                throw new Error(data.error || 'Failed to process video');
            }
        } catch (err) {
            console.warn(err);
            analyzeBtn.innerHTML = 'Analyze';
            analyzeBtn.disabled = false;
            landingError.textContent = "Error: Could not connect to backend.";
            landingError.style.display = 'block';
        }
    });

    // --- Main Logic: Ask Question ---
    sendBtn.addEventListener('click', async () => {
        const question = chatInput.value.trim();
        if (!question) return;
        if (!currentVideoId) return;
        
        addMessage(question, "user");
        chatInput.value = '';
        chatInput.style.height = 'auto';
        sendBtn.disabled = true;
        
        showTyping();
        try {
            const resp = await fetch('/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: currentVideoId, question: question })
            });
            const data = await resp.json();
            
            hideTyping();
            
            if (data.success) {
                let sourcesList = [];
                if (data.sources && Array.isArray(data.sources)) {
                    sourcesList = data.sources.map(s => ({ time: s.time || s.timestamp || "00:00" }));
                } else if (data.timestamps) {
                    sourcesList = data.timestamps.map(t => ({ time: t }));
                }
                addMessage(data.answer, "ai", sourcesList);
            } else {
                addMessage(`Error: ${data.error || "Generation failed."}`, "ai");
            }
        } catch (err) {
            hideTyping();
            addMessage("Network error. Backend unreachable.", "ai");
        } finally {
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });

    // --- Event Listeners for Enter Key & Resizing ---
    landingInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !analyzeBtn.disabled) analyzeBtn.click();
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) sendBtn.click();
        }
    });

    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
    });
  </script>
</body>
</html>