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
                    addMessage(data.response, 'bot-message');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your request.', 'bot-message');
            });
        }
    }

    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        chatContainer.appendChild(messageDiv);

        if (className === 'bot-message') {
            // Type effect for bot messages
            let index = 0;
            const typingSpeed = 20; // Adjust speed (lower = faster)
            
            function typeNextCharacter() {
                if (index < text.length) {
                    messageDiv.innerHTML += text.charAt(index);
                    index++;
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    setTimeout(typeNextCharacter, typingSpeed);
                } else {
                    // After typing complete, convert URLs to clickable links
                    const urlRegex = /(https?:\/\/[^\s]+)/g;
                    messageDiv.innerHTML = messageDiv.innerHTML.replace(urlRegex, (url) => {
                        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
                    });
                }
            }
            
            typeNextCharacter();
        } else {
            // User messages appear instantly
            messageDiv.textContent = text;
        }
        
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