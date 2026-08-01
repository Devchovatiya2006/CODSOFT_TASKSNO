let history = [];

// ── Send via quick prompt button ──────────────────────────────────────────────
function send(text) {
  document.getElementById('input').value = text;
  sendMessage();
}

// ── Main send function ────────────────────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('input');
  const text = input.value.trim();
  if (!text) return;

  appendMsg(text, 'user');
  input.value = '';
  showTyping(true);

  // Realistic delay
  await new Promise(r => setTimeout(r, 500 + Math.random() * 700));

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    showTyping(false);
    appendMsg(data.response, 'bot', data);
    updateDiag(data);
    updateMemory(data);
  } catch (err) {
    showTyping(false);
    appendMsg('⚠️ Could not reach the server. Make sure Flask is running.', 'bot');
  }
}

// ── Append a message bubble ───────────────────────────────────────────────────
function appendMsg(text, sender, meta = null) {
  const box = document.getElementById('messages');

  // Hide welcome card on first message
  const welcome = box.querySelector('.welcome');
  if (welcome) welcome.remove();

  const row = document.createElement('div');
  row.className = `msg-row ${sender}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.innerHTML = sender === 'user'
    ? '<i class="fa-solid fa-user"></i>'
    : '<i class="fa-solid fa-robot"></i>';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  // Render markdown-like bold, code, newlines
  const html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');

  bubble.innerHTML = `<p>${html}</p>`;

  if (sender === 'bot' && meta) {
    const m = document.createElement('div');
    m.className = 'msg-meta';
    m.innerHTML = `<span>${meta.intent || 'fallback'}</span><span>${Math.round((meta.confidence || 0) * 100)}% match</span>`;
    bubble.appendChild(m);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;

  history.push({ sender, text, time: new Date().toISOString() });
}

// ── Diagnostics bar ───────────────────────────────────────────────────────────
function updateDiag(data) {
  document.getElementById('d-intent').textContent = data.intent || 'fallback';
  document.getElementById('d-conf').textContent = Math.round((data.confidence || 0) * 100) + '%';
  document.getElementById('d-pattern').textContent = data.pattern || 'none (fallback)';
}

// ── Memory sidebar ────────────────────────────────────────────────────────────
function updateMemory(data) {
  // We infer memory from intent
  const display = document.getElementById('memory-display');
  if (data.intent === 'set_name') {
    // Extract name from response
    const match = data.response.match(/meet you,\s*([A-Za-z]+)/i) || data.response.match(/know you,\s*([A-Za-z]+)/i) || data.response.match(/as\s+([A-Za-z]+)/i);
    if (match) {
      display.innerHTML = `<div class="mem-tag"><span class="mk">user_name</span><span class="mv">${match[1]}</span></div>`;
    }
  }
  if (data.intent === 'fallback_name' || (data.intent === 'get_name' && data.response.includes("don't know"))) {
    display.innerHTML = `<span class="muted">No memory stored yet.</span>`;
  }
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function showTyping(show) {
  document.getElementById('typing').style.display = show ? 'flex' : 'none';
}

// ── Reset memory ──────────────────────────────────────────────────────────────
async function resetMemory() {
  await fetch('/api/reset', { method: 'POST' });
  document.getElementById('memory-display').innerHTML = '<span class="muted">No memory stored yet.</span>';
  appendMsg('🧹 Memory has been cleared!', 'bot');
}

// ── Clear chat ────────────────────────────────────────────────────────────────
function clearChat() {
  const box = document.getElementById('messages');
  box.innerHTML = `
    <div class="welcome">
      <div class="welcome-icon"><i class="fa-solid fa-robot"></i></div>
      <h3>Welcome to RuleBot! 🤖</h3>
      <p>I understand natural language using pattern matching and predefined rules.<br/>Type anything or use the quick prompts on the left!</p>
    </div>`;
  history = [];
  document.getElementById('d-intent').textContent = '—';
  document.getElementById('d-conf').textContent = '—';
  document.getElementById('d-pattern').textContent = '—';
}

// ── Export chat ───────────────────────────────────────────────────────────────
function exportChat() {
  if (!history.length) { alert('No conversation to export yet.'); return; }
  const blob = new Blob([JSON.stringify(history, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `rulebot_chat_${Date.now()}.json`;
  a.click();
}
