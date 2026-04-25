// Configuration
const API_URL = 'http://127.0.0.1:8000/chat';

// State
let conversationHistory = [];
let userPreferences = {
  budget_max: null,
  gender: null,
  currency: 'INR'
};
let chatSessions = [];
let currentSessionId = null;

// DOM Elements
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const messagesList = document.getElementById('messagesList');
const messagesContainer = document.getElementById('messagesContainer');
const welcomeScreen = document.getElementById('welcomeScreen');
const productsSection = document.getElementById('productsSection');
const productsGrid = document.getElementById('productsGrid');
const productCount = document.getElementById('productCount');
const followupChips = document.getElementById('followupChips');
const settingsPanel = document.getElementById('settingsPanel');
const settingsToggle = document.getElementById('settingsToggle');
const closeSettings = document.getElementById('closeSettings');
const saveSettings = document.getElementById('saveSettings');
const budgetInput = document.getElementById('budgetInput');
const genderSelect = document.getElementById('genderSelect');
const budgetBadge = document.getElementById('budgetBadge');
const budgetDisplay = document.getElementById('budgetDisplay');
const newChatBtn = document.getElementById('newChatBtn');
const historyList = document.getElementById('historyList');

// Initialize
loadPreferences();
loadChatHistory();
updateBudgetBadge();

// Event Listeners
chatInput.addEventListener('input', () => {
  sendBtn.disabled = !chatInput.value.trim();
  autoResize(chatInput);
});

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (chatInput.value.trim()) {
      sendMessage();
    }
  }
});

sendBtn.addEventListener('click', sendMessage);

settingsToggle.addEventListener('click', () => {
  settingsPanel.classList.toggle('hidden');
});

closeSettings.addEventListener('click', () => {
  settingsPanel.classList.add('hidden');
});

saveSettings.addEventListener('click', () => {
  const budget = budgetInput.value ? parseFloat(budgetInput.value) : null;
  const gender = genderSelect.value || null;
  
  userPreferences = {
    budget_max: budget,
    gender: gender,
    currency: 'INR'
  };
  
  savePreferences();
  updateBudgetBadge();
  settingsPanel.classList.add('hidden');
  
  showNotification('Preferences saved!');
});

newChatBtn.addEventListener('click', startNewChat);

// Suggestion chips
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const query = chip.getAttribute('data-query');
    chatInput.value = query;
    sendBtn.disabled = false;
    sendMessage();
  });
});

// Functions
function autoResize(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function updateBudgetBadge() {
  if (userPreferences.budget_max) {
    budgetDisplay.textContent = userPreferences.budget_max.toLocaleString();
    budgetBadge.classList.remove('hidden');
  } else {
    budgetBadge.classList.add('hidden');
  }
}

function savePreferences() {
  localStorage.setItem('shop_ai_preferences', JSON.stringify(userPreferences));
}

function loadPreferences() {
  const saved = localStorage.getItem('shop_ai_preferences');
  if (saved) {
    userPreferences = JSON.parse(saved);
    budgetInput.value = userPreferences.budget_max || '';
    genderSelect.value = userPreferences.gender || '';
  }
}

function saveChatHistory() {
  localStorage.setItem('shop_ai_sessions', JSON.stringify(chatSessions));
}

function loadChatHistory() {
  const saved = localStorage.getItem('shop_ai_sessions');
  if (saved) {
    chatSessions = JSON.parse(saved);
    renderHistoryList();
  }
}

function renderHistoryList() {
  if (chatSessions.length === 0) {
    historyList.innerHTML = '<div class="empty-history">No chat history yet</div>';
    return;
  }
  
  historyList.innerHTML = chatSessions
    .slice(-10)
    .reverse()
    .map(session => `
      <div class="history-item" data-id="${session.id}">
        ${session.title}
      </div>
    `)
    .join('');
  
  // Add click handlers
  document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', () => {
      const id = item.getAttribute('data-id');
      loadSession(id);
    });
  });
}

function loadSession(id) {
  const session = chatSessions.find(s => s.id === id);
  if (session) {
    // For now, just show a notification
    showNotification(`Loading session: ${session.title}`);
  }
}

function startNewChat() {
  conversationHistory = [];
  currentSessionId = null;
  messagesList.innerHTML = '';
  messagesList.classList.add('hidden');
  welcomeScreen.classList.remove('hidden');
  productsSection.classList.add('hidden');
  followupChips.classList.add('hidden');
  chatInput.value = '';
  sendBtn.disabled = true;
}

async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;
  
  // Hide welcome screen
  welcomeScreen.classList.add('hidden');
  messagesList.classList.remove('hidden');
  
  // Add user message
  addMessage('user', message);
  conversationHistory.push({ role: 'user', content: message });
  
  // Clear input
  chatInput.value = '';
  sendBtn.disabled = true;
  autoResize(chatInput);
  
  // Show typing indicator
  const typingId = addTypingIndicator();
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        history: conversationHistory.slice(-10), // Last 5 exchanges
        preferences: userPreferences
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Remove typing indicator
    removeTypingIndicator(typingId);
    
    // Add assistant message
    addMessage('assistant', data.reply || 'Here are some suggestions for you.');
    conversationHistory.push({ 
      role: 'assistant', 
      content: data.reply || 'Here are some suggestions for you.' 
    });
    
    // Display products
    if (data.products && data.products.length > 0) {
      displayProducts(data.products);
    } else {
      productsSection.classList.add('hidden');
    }
    
    // Display follow-up questions
    if (data.follow_up_questions && data.follow_up_questions.length > 0) {
      displayFollowUpQuestions(data.follow_up_questions);
    } else {
      followupChips.classList.add('hidden');
    }
    
    // Save to history
    saveToHistory(message, data);
    
  } catch (error) {
    console.error('Error:', error);
    removeTypingIndicator(typingId);
    addMessage('assistant', 'Sorry, something went wrong. Please try again.');
  }
  
  scrollToBottom();
}

function addMessage(role, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message-row ${role}`;
  
  const avatar = document.createElement('div');
  avatar.className = `avatar ${role}`;
  avatar.textContent = role === 'user' ? '👤' : '🤖';
  
  const bubble = document.createElement('div');
  bubble.className = `bubble ${role}`;
  bubble.textContent = content;
  
  messageDiv.appendChild(avatar);
  messageDiv.appendChild(bubble);
  
  messagesList.appendChild(messageDiv);
}

function addTypingIndicator() {
  const id = 'typing-' + Date.now();
  const messageDiv = document.createElement('div');
  messageDiv.id = id;
  messageDiv.className = 'message-row assistant';
  
  const avatar = document.createElement('div');
  avatar.className = 'avatar ai';
  avatar.textContent = '🤖';
  
  const indicator = document.createElement('div');
  indicator.className = 'typing-indicator';
  indicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  
  messageDiv.appendChild(avatar);
  messageDiv.appendChild(indicator);
  
  messagesList.appendChild(messageDiv);
  scrollToBottom();
  
  return id;
}

function removeTypingIndicator(id) {
  const element = document.getElementById(id);
  if (element) {
    element.remove();
  }
}

function displayProducts(products) {
  productsGrid.innerHTML = '';
  productCount.textContent = products.length;
  
  products.forEach(product => {
    const card = createProductCard(product);
    productsGrid.appendChild(card);
  });
  
  productsSection.classList.remove('hidden');
}

function createProductCard(product) {
  const card = document.createElement('div');
  card.className = 'product-card';
  
  const hasImage = product.image && product.image.trim() !== '';
  
  card.innerHTML = `
    <div class="card-image-wrap">
      ${hasImage 
        ? `<img src="${product.image}" alt="${product.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
           <div class="img-placeholder" style="display:none;">
             <span class="icon">📦</span>
             <span>No image</span>
           </div>`
        : `<div class="img-placeholder">
             <span class="icon">📦</span>
             <span>No image</span>
           </div>`
      }
    </div>
    <div class="card-body">
      <div class="card-name">${product.name || 'Product'}</div>
      <div class="card-platform">${product.platform || 'Online'}</div>
      <div class="card-reason">${product.reason || 'Great product for you'}</div>
      <div class="card-footer">
        <div class="card-price">${product.price || '₹0'}</div>
        ${product.score ? `<div class="card-rating">⭐ ${(product.score * 5).toFixed(1)}</div>` : ''}
      </div>
      <a href="${product.link || '#'}" target="_blank" rel="noopener" class="view-btn">
        View on ${product.platform || 'Site'}
      </a>
    </div>
  `;
  
  return card;
}

function displayFollowUpQuestions(questions) {
  followupChips.innerHTML = '';
  
  questions.forEach(question => {
    const chip = document.createElement('div');
    chip.className = 'followup-chip';
    chip.textContent = question;
    chip.addEventListener('click', () => {
      chatInput.value = question;
      sendBtn.disabled = false;
      sendMessage();
    });
    followupChips.appendChild(chip);
  });
  
  followupChips.classList.remove('hidden');
}

function saveToHistory(query, response) {
  if (!currentSessionId) {
    currentSessionId = 'session-' + Date.now();
    const title = query.slice(0, 30) + (query.length > 30 ? '...' : '');
    chatSessions.push({
      id: currentSessionId,
      title: title,
      timestamp: Date.now(),
      query: query,
      productCount: response.products ? response.products.length : 0
    });
    saveChatHistory();
    renderHistoryList();
  }
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showNotification(message) {
  // Simple notification - you can enhance this
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--accent);
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  `;
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
}
