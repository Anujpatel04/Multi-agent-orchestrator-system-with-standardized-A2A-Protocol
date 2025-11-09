let communicationLog = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadAgentsStatus();
    loadAgentsData();
    // Refresh less frequently and only when page is visible
    setInterval(() => {
        if (!document.hidden) {
            loadAgentsStatus();
            loadAgentsData();
        }
    }, 10000); // Refresh every 10 seconds instead of 5
});

// Load agents status
async function loadAgentsStatus() {
    try {
        const response = await fetch('/api/agents/status');
        const data = await response.json();
        
        updateStatusBadge('orchestrator-status', data.orchestrator.status);
        updateStatusBadge('agent1-status', data.agent1.status);
        updateStatusBadge('agent2-status', data.agent2.status);
        
        // Update status in agent details cards
        updateStatusBadge('agent1-status-display', data.agent1.status);
        updateStatusBadge('agent2-status-display', data.agent2.status);
    } catch (error) {
        console.error('Error loading agents status:', error);
    }
}

// Load agents data smoothly without page jumps
async function loadAgentsData() {
    try {
        const response = await fetch('/api/agents/data');
        const data = await response.json();
        
        // Store scroll positions before updating
        const agent1List = document.getElementById('agent1-list');
        const agent2List = document.getElementById('agent2-list');
        const agent1Scroll = agent1List ? agent1List.scrollTop : 0;
        const agent2Scroll = agent2List ? agent2List.scrollTop : 0;
        
        // Update counts only if changed
        const agent1CountEl = document.getElementById('agent1-schedules');
        const agent2CountEl = document.getElementById('agent2-schedules');
        
        if (agent1CountEl && agent1CountEl.textContent !== String(data.agent1.total_schedules)) {
            agent1CountEl.textContent = data.agent1.total_schedules;
        }
        
        if (agent2CountEl && agent2CountEl.textContent !== String(data.agent2.total_schedules)) {
            agent2CountEl.textContent = data.agent2.total_schedules;
        }
        
        // Update schedule lists (function handles smooth updates internally)
        updateScheduleList('agent1-list', data.agent1.schedules);
        updateScheduleList('agent2-list', data.agent2.schedules);
        
        // Restore scroll positions after a brief delay to allow DOM to update
        setTimeout(() => {
            if (agent1List && agent1Scroll > 0) {
                agent1List.scrollTop = agent1Scroll;
            }
            if (agent2List && agent2Scroll > 0) {
                agent2List.scrollTop = agent2Scroll;
            }
        }, 50);
    } catch (error) {
        console.error('Error loading agents data:', error);
    }
}

// Switch between agents - No longer needed as both are visible horizontally
function switchAgent(agentId) {
    // Function kept for compatibility but both agents are now always visible
    return;
}

// Store previous schedule data to prevent unnecessary updates
let previousScheduleData = {
    'agent1-list': null,
    'agent2-list': null
};

// Update schedule list smoothly without page jumps
function updateScheduleList(listId, schedules) {
    const listElement = document.getElementById(listId);
    if (!listElement) return;
    
    // Create a hash of current schedules to check if data changed
    const scheduleHash = JSON.stringify(schedules.map(s => ({ id: s.id, content: s.content })));
    
    // Only update if data actually changed
    if (previousScheduleData[listId] === scheduleHash) {
        return; // No changes, skip update
    }
    
    previousScheduleData[listId] = scheduleHash;
    
    // Store scroll position if user is viewing this list
    const wasScrolled = listElement.scrollTop > 0;
    const scrollPosition = listElement.scrollTop;
    
    // Clear without animation to prevent jumps
    listElement.innerHTML = '';
    
    if (schedules.length === 0) {
        listElement.innerHTML = '<p style="color: var(--text-light); font-size: 13px;">No schedules stored</p>';
        return;
    }
    
    // Add items without initial animation for smooth updates
    schedules.slice(0, 5).forEach((schedule, index) => {
        const item = document.createElement('div');
        item.className = 'schedule-item';
        item.style.opacity = '1';
        item.style.transform = 'translateX(0)';
        item.innerHTML = `
            <strong>ID:</strong> ${schedule.id.substring(0, 8)}...<br>
            ${schedule.content.substring(0, 80)}${schedule.content.length > 80 ? '...' : ''}
        `;
        listElement.appendChild(item);
    });
    
    // Restore scroll position if user was viewing
    if (wasScrolled && listElement.scrollHeight > scrollPosition) {
        listElement.scrollTop = scrollPosition;
    }
}

// Update status badge with animation
function updateStatusBadge(elementId, status) {
    const badge = document.getElementById(elementId);
    if (!badge) return;
    
    const isReady = status === 'ready';
    const newText = isReady ? 'Ready' : 'Not Ready';
    const newColor = isReady ? 'var(--success)' : 'var(--error)';
    
    // Only animate if status changed
    if (badge.textContent !== newText) {
        badge.style.transform = 'scale(0.9)';
        badge.style.opacity = '0.7';
        
        setTimeout(() => {
            badge.textContent = newText;
            badge.style.background = newColor;
            badge.style.transition = 'all 0.3s ease';
            badge.style.transform = 'scale(1)';
            badge.style.opacity = '1';
        }, 150);
    }
}

// Conversation history
let conversationHistory = [];

// Send query and add to chat thread
async function sendQuery() {
    const queryInput = document.getElementById('user-query');
    const query = queryInput.value.trim();
    const queryType = document.getElementById('query-type').value;
    
    if (!query) {
        return;
    }
    
    // Clear input
    queryInput.value = '';
    queryInput.style.height = 'auto';
    
    // Add user message to chat
    addMessageToChat('user', query, queryType);
    
    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: query,
        type: queryType,
        timestamp: new Date()
    });
    
    // Add query to communication log
    addLogEntry('user', 'orchestrator', query, 'query');
    
    // Show loading message
    const loadingId = addMessageToChat('agent', 'Thinking...', queryType, true);
    
    // Show loading state
    const sendButton = document.getElementById('send-query');
    sendButton.disabled = true;
    sendButton.style.opacity = '0.6';
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                type: queryType,
                conversation_history: conversationHistory.slice(-10) // Send last 10 messages for context
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) {
            loadingMsg.remove();
        }
        
        // Add communication log entries
        result.communication_log.forEach(entry => {
            addLogEntry(entry.from, entry.to, entry.message, entry.type);
        });
        
        // Get and format response text for a friendlier UX
        const rawResponse = result.result.aggregated_response || result.result.response || 'No response';
        const responseText = formatAgentResponse(rawResponse);

        // Add agent response to chat
        const messageId = addMessageToChat('agent', responseText, queryType);

        // Render dynamic suggestions from LLM
        const suggestions = result.suggestions || [];
        renderDynamicFollowUps(messageId, suggestions);
        
        // Add to conversation history
        conversationHistory.push({
            role: 'assistant',
            content: responseText,
            type: queryType,
            timestamp: new Date()
        });
        
        // Keep only last 20 messages in history
        if (conversationHistory.length > 20) {
            conversationHistory = conversationHistory.slice(-20);
        }
        
    } catch (error) {
        console.error('Error sending query:', error);
        
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) {
            loadingMsg.remove();
        }
        
        // Show error message
        addMessageToChat('agent', `Error: ${error.message}`, queryType);
        addLogEntry('system', 'user', `Error: ${error.message}`, 'error');
    } finally {
        sendButton.disabled = false;
        sendButton.style.opacity = '1';
    }
}

// Add message to chat thread
function addMessageToChat(sender, message, queryType, isLoading = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `chat-message chat-${sender}`;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const avatar = sender === 'user' ? '👤' : sender === 'agent' ? '🤖' : '🔧';
    const senderName = sender === 'user' ? 'You' : sender === 'agent' ? 'Orchestrator' : 'System';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">${senderName}</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-text">${isLoading ? '<em>' + message + '</em>' : message.replace(/\n/g, '<br>')}</div>
            ${sender === 'agent' ? '<div class="followups" id="followups-'+messageId+'"></div>' : ''}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Remove system welcome message if it exists
    const systemMsg = chatMessages.querySelector('.chat-system');
    if (systemMsg && sender !== 'system') {
        systemMsg.remove();
    }
    
    return messageId;
}

// Format orchestrator responses into concise, readable paragraphs and bullets
function formatAgentResponse(text) {
    if (!text) return '';
    let t = String(text).trim();
    // Normalize whitespace
    t = t.replace(/\r/g, '').replace(/\t/g, ' ').replace(/\n{3,}/g, '\n\n');
    // Convert simple hyphen lists to bullets
    t = t.replace(/\n-\s+/g, '\n• ');
    // Capitalize first letter if sentence-like
    if (/^[a-z]/.test(t)) t = t.charAt(0).toUpperCase() + t.slice(1);
    // Keep it concise
    if (t.length > 1500) t = t.slice(0, 1500) + '...';
    return t;
}

// Render dynamic follow-up suggestions generated by LLM
function renderDynamicFollowUps(messageId, suggestions) {
    try {
        if (!suggestions || !Array.isArray(suggestions) || suggestions.length === 0) {
            // Fallback to default suggestions if LLM didn't provide any
            suggestions = [
                'Find common free time this week',
                'Show detailed schedule for tomorrow',
                'Compare both users\' availability'
            ];
        }

        const chatMessages = document.getElementById('chat-messages');
        const agentMsg = document.getElementById(messageId);
        if (!agentMsg) return;
        
        const followupsContainer = agentMsg.querySelector('.followups');
        if (!followupsContainer) return;

        // Create suggestion chips
        followupsContainer.innerHTML = suggestions.slice(0, 3).map(s => {
            const escaped = s.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            return `<button class="followup-chip" onclick="quickAsk('${escaped}')" title="Click to ask: ${escaped}">${s}</button>`;
        }).join('');
        
        // Add fade-in animation
        followupsContainer.style.opacity = '0';
        setTimeout(() => {
            followupsContainer.style.transition = 'opacity 0.3s ease-in';
            followupsContainer.style.opacity = '1';
        }, 100);
    } catch (e) {
        console.warn('Dynamic follow-ups render error:', e);
    }
}

// Quickly send a predefined follow-up
function quickAsk(text) {
    const input = document.getElementById('user-query');
    if (!input) return;
    input.value = text;
    sendQuery();
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to start a new conversation?')) {
        conversationHistory = [];
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="chat-message chat-system">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-sender">System</span>
                        <span class="message-time">Just now</span>
                    </div>
                    <div class="message-text">Hello! I'm your Orchestrator Agent. I can help you query schedules, find common free time, and coordinate between different users. How can I assist you today?</div>
                </div>
            </div>
        `;
    }
}

// Communication log management
let autoScrollEnabled = true;

function addLogEntry(from, to, message, type) {
    const logContainer = document.getElementById('communication-log');
    if (!logContainer) return;
    
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    
    // Format message - truncate if too long
    const maxMessageLength = 300;
    const displayMessage = message.length > maxMessageLength 
        ? message.substring(0, maxMessageLength) + '...' 
        : message;
    
    // Format names
    const formatName = (name) => {
        return name
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    };
    
    entry.innerHTML = `
        <div class="log-timestamp">${timestamp}</div>
        <div class="log-content">
            <span class="log-from">${formatName(from)}</span>
            <span class="log-arrow">→</span>
            <span class="log-to">${formatName(to)}</span>
            <span class="log-message">${displayMessage}</span>
        </div>
    `;
    
    // Remove initial system message if it exists
    const initialMessage = logContainer.querySelector('.log-info');
    if (initialMessage && logContainer.children.length === 1) {
        initialMessage.remove();
    }
    
    // Add new entry at the top
    logContainer.insertBefore(entry, logContainer.firstChild);
    
    // Auto-scroll to top if enabled
    if (autoScrollEnabled) {
        logContainer.scrollTop = 0;
    }
    
    // Keep only last 100 entries
    while (logContainer.children.length > 100) {
        logContainer.removeChild(logContainer.lastChild);
    }
    
    // Add fade-in animation
    entry.style.opacity = '0';
    entry.style.transform = 'translateX(-20px)';
    setTimeout(() => {
        entry.style.transition = 'all 0.4s ease-out';
        entry.style.opacity = '1';
        entry.style.transform = 'translateX(0)';
    }, 10);
}

function clearLog() {
    const logContainer = document.getElementById('communication-log');
    if (!logContainer) return;
    
    if (confirm('Are you sure you want to clear the communication log?')) {
        logContainer.innerHTML = `
            <div class="log-entry log-info">
                <div class="log-timestamp">System</div>
                <div class="log-content">
                    <span class="log-from">System</span>
                    <span class="log-arrow">→</span>
                    <span class="log-to">All</span>
                    <span class="log-message">Communication log cleared.</span>
                </div>
            </div>
        `;
    }
}

function toggleAutoScroll() {
    autoScrollEnabled = !autoScrollEnabled;
    const btn = document.getElementById('autoscroll-btn');
    if (btn) {
        btn.style.background = autoScrollEnabled ? 'var(--primary)' : 'var(--bg)';
        btn.style.color = autoScrollEnabled ? 'white' : 'var(--text)';
        btn.title = autoScrollEnabled ? 'Disable Auto-scroll' : 'Enable Auto-scroll';
    }
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('user-query');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        // Allow Enter to send, Shift+Enter for new line
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQuery();
            }
        });
    }
});


