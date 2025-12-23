const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadStatus = document.getElementById('upload-status');
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// --- File Upload Logic ---

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
    }
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        handleFiles(fileInput.files);
    }
});

async function handleFiles(files) {
    for (const file of files) {
        await uploadFile(file);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    uploadStatus.textContent = `Uploading ${file.name}...`;
    uploadStatus.className = 'status-msg loading';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            uploadStatus.textContent = `Indexed: ${result.message}`;
            uploadStatus.className = 'status-msg success';
            setTimeout(() => {
                uploadStatus.textContent = '';
            }, 3000);
        } else {
            const err = await response.json();
            throw new Error(err.message || 'Upload failed');
        }
    } catch (error) {
        console.error(error);
        uploadStatus.textContent = `Error: ${error.message}`;
        uploadStatus.className = 'status-msg error';
    }
}

// --- Chat Logic ---

userInput.addEventListener('input', () => {
    sendBtn.disabled = userInput.value.trim() === '';
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !sendBtn.disabled) {
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    // Add User Message
    addMessage(query, 'user');
    userInput.value = '';
    sendBtn.disabled = true;

    // Loading Indicator
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        
        // Remove loading
        removeMessage(loadingId);
        
        // Add Bot Message
        addMessage(data.answer, 'bot', data.context);

    } catch (error) {
        removeMessage(loadingId);
        addMessage('Sorry, something went wrong. Please check the console.', 'bot');
        console.error(error);
    }
}

function addMessage(text, sender, context = null) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    
    // Icon
    const icon = sender === 'bot' ? 'fas fa-robot' : 'fas fa-user';
    
    let contentHtml = `<p>${text}</p>`;
    
    // Add Sources if available
    if (context && context.length > 0) {
        contentHtml += `<div class="context-source"><strong>Sources:</strong>`;
        context.forEach(ctx => {
            contentHtml += `
                <div class="source-item">
                    <span class="source-score">Match: ${Math.round(ctx.score * 100)}%</span>
                    <p>"${ctx.text}"</p>
                </div>
            `;
        });
        contentHtml += `</div>`;
    }

    div.innerHTML = `
        <div class="avatar"><i class="${icon}"></i></div>
        <div class="message-content">${contentHtml}</div>
    `;
    
    messagesContainer.appendChild(div);
    scrollToBottom();
}

function addLoadingMessage() {
    const id = 'loading-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message bot';
    div.innerHTML = `
        <div class="avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <p><i class="fas fa-circle-notch fa-spin"></i> Thinking...</p>
        </div>
    `;
    messagesContainer.appendChild(div);
    scrollToBottom();
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function clearChat() {
    messagesContainer.innerHTML = `
        <div class="message bot">
            <div class="avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <p>Chat cleared. Ready for new questions!</p>
            </div>
        </div>
    `;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
