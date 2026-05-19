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
        // Ab ye Asli Error dikhayega jo backend se aayegi
        landingError.textContent = err.message || "Error: Could not connect to backend.";
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