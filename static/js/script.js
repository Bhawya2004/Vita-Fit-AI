document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            addMessage(message, 'user-message');
            messageInput.value = '';
            
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    addMessage('Sorry, there was an error processing your request.', 'bot-message');
                } else {
                    // Convert YouTube links to clickable links
                    const formattedResponse = formatMessage(data.response);
                    addMessage(formattedResponse, 'bot-message', true);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your request.', 'bot-message');
            });
        }
    }

    function formatMessage(text) {
        // Regular expression to match YouTube URLs
        const youtubeRegex = /(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(watch\?v=)?([a-zA-Z0-9_-]+)(\S*)/g;
        
        // Regular expression to match any URL
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        
        // Replace YouTube URLs with clickable links
        text = text.replace(youtubeRegex, '<a href="$&" target="_blank" rel="noopener noreferrer">Click here to watch the video</a>');
        
        // Replace other URLs with clickable links
        text = text.replace(urlRegex, function(url) {
            if (!url.match(youtubeRegex)) {
                return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
            }
            return url;
        });
        
        return text;
    }

    function addMessage(text, className, isHTML = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        if (isHTML) {
            messageDiv.innerHTML = text;
        } else {
            messageDiv.textContent = text;
        }
        
        // Add click event listeners to all links
        if (isHTML) {
            const links = messageDiv.getElementsByTagName('a');
            Array.from(links).forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.open(link.href, '_blank');
                });
            });
        }
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

// Theme toggle functionality
function toggleTheme() {
    const body = document.body;
    const checkbox = document.getElementById('theme-switch');
    
    if (checkbox.checked) {
        body.setAttribute('data-theme', 'dark');
    } else {
        body.removeAttribute('data-theme');
    }
    
    // Save preference
    localStorage.setItem('theme', checkbox.checked ? 'dark' : 'light');
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    const checkbox = document.getElementById('theme-switch');
    
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        checkbox.checked = true;
    }
}); 