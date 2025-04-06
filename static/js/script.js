document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');
    const imageUploadBtn = document.getElementById('image-upload-btn');
    const imageInput = document.getElementById('image-input');
    const voiceInputBtn = document.getElementById('voice-input-btn');
    
    let currentImage = null;
    let recognition = null;
    
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-IN';
        
        // Speech recognition event handlers...
    }
    
    // Apply typing animation to the initial welcome message
    function animateInitialMessage() {
        // Find the first bot message (welcome message)
        const welcomeMessage = document.querySelector('.bot-message');
        
        if (welcomeMessage) {
            // Store the original text and immediately clear it to prevent flashing
            const originalText = welcomeMessage.textContent;
            welcomeMessage.textContent = '';
            
            // Add a small delay before starting the animation
            setTimeout(() => {
                let i = 0;
                const typingSpeed = 30; // milliseconds per character
                
                function typeNextChar() {
                    if (i < originalText.length) {
                        welcomeMessage.textContent += originalText.charAt(i);
                        i++;
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                        setTimeout(typeNextChar, typingSpeed);
                    }
                }
                
                typeNextChar();
            }, 100);
        }
    }
    
    // Hide the initial message and run the animation after DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        const welcomeMessage = document.querySelector('.bot-message');
        if (welcomeMessage) {
            welcomeMessage.style.visibility = 'hidden';
            setTimeout(() => {
                welcomeMessage.style.visibility = 'visible';
                animateInitialMessage();
            }, 300);
        }
    });
    
    // Send message when button is clicked
    sendButton.addEventListener('click', sendMessage);
    
    // Send message when Enter key is pressed
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input field
            messageInput.value = '';
            
            // Add a temporary typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message bot-message typing-indicator';
            typingIndicator.innerHTML = '<span>.</span><span>.</span><span>.</span>';
            chatContainer.appendChild(typingIndicator);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // Send message to server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                chatContainer.removeChild(typingIndicator);
                
                // Add bot response with typing effect
                const botMessage = document.createElement('div');
                botMessage.className = 'message bot-message';
                chatContainer.appendChild(botMessage);
                
                // Simulate typing effect
                const response = data.response;
                let i = 0;
                const typingSpeed = 30; // milliseconds per character
                
                function typeNextChar() {
                    if (i < response.length) {
                        botMessage.innerHTML += response.charAt(i);
                        i++;
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                        setTimeout(typeNextChar, typingSpeed);
                    }
                }
                
                typeNextChar();
            })
            .catch(error => {
                console.error('Error:', error);
                // Remove typing indicator
                chatContainer.removeChild(typingIndicator);
                addMessage('Sorry, there was an error processing your request.', 'bot');
            });
        }
    }
    
    // Image upload handling
    imageUploadBtn.addEventListener('click', () => {
        imageInput.click();
    });
    
    imageInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                currentImage = e.target.result;
                
                // Show image preview
                const previewContainer = document.createElement('div');
                previewContainer.className = 'message user-message';
                
                const imagePreview = document.createElement('img');
                imagePreview.src = currentImage;
                imagePreview.className = 'image-preview';
                
                previewContainer.appendChild(imagePreview);
                chatContainer.appendChild(previewContainer);
                
                // Add typing indicator
                const typingIndicator = document.createElement('div');
                typingIndicator.className = 'message bot-message typing-indicator';
                typingIndicator.innerHTML = '<span>.</span><span>.</span><span>.</span>';
                chatContainer.appendChild(typingIndicator);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                // Send the image to the server
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image: currentImage })
                })
                .then(response => response.json())
                .then(data => {
                    // Remove typing indicator
                    chatContainer.removeChild(typingIndicator);
                    
                    // Add bot response with typing effect
                    const botMessage = document.createElement('div');
                    botMessage.className = 'message bot-message';
                    chatContainer.appendChild(botMessage);
                    
                    // Simulate typing effect
                    const response = data.response;
                    let i = 0;
                    const typingSpeed = 30; // milliseconds per character
                    
                    function typeNextChar() {
                        if (i < response.length) {
                            botMessage.innerHTML += response.charAt(i);
                            i++;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                            setTimeout(typeNextChar, typingSpeed);
                        }
                    }
                    
                    typeNextChar();
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Remove typing indicator
                    chatContainer.removeChild(typingIndicator);
                    addMessage('Sorry, there was an error analyzing your image.', 'bot');
                });
                
                // Reset the file input
                imageInput.value = '';
            };
            reader.readAsDataURL(file);
        }
    });
    
    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        // Process markdown-like links in the text
        const processedText = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        
        messageElement.innerHTML = processedText;
        chatContainer.appendChild(messageElement);
        
        // Scroll to the bottom of the chat
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Theme toggle functionality
    window.toggleTheme = function() {
        const body = document.body;
        if (body.getAttribute('data-theme') === 'dark') {
            body.removeAttribute('data-theme');
        } else {
            body.setAttribute('data-theme', 'dark');
        }
    };
});