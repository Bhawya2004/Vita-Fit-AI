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
        
        // Support both English and Hindi automatically
        recognition.lang = 'en-IN'; // English (India) to better support both English and Hindi
        
        recognition.onstart = () => {
            voiceInputBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            voiceInputBtn.classList.add('recording');
            messageInput.placeholder = "Listening...";
            
            // Add a visual indicator in the chat
            const listeningIndicator = document.createElement('div');
            listeningIndicator.id = 'listening-indicator';
            listeningIndicator.className = 'message bot-message analyzing-message';
            listeningIndicator.textContent = 'Listening... (speak in English or Hindi)';
            chatContainer.appendChild(listeningIndicator);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        };
        
        recognition.onend = () => {
            voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceInputBtn.classList.remove('recording');
            messageInput.placeholder = "Ask me about fitness...";
            
            // Remove the listening indicator
            const listeningIndicator = document.getElementById('listening-indicator');
            if (listeningIndicator) {
                chatContainer.removeChild(listeningIndicator);
            }
        };
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            if (finalTranscript) {
                messageInput.value = finalTranscript;
                // Optionally auto-send the message
                // sendMessage();
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceInputBtn.classList.remove('recording');
            
            // Remove the listening indicator
            const listeningIndicator = document.getElementById('listening-indicator');
            if (listeningIndicator) {
                chatContainer.removeChild(listeningIndicator);
            }
            
            // Show error message
            addMessage('Sorry, I couldn\'t hear you. Please try again.', 'bot');
        };
        
        // Add click event for voice button
        voiceInputBtn.addEventListener('click', () => {
            if (voiceInputBtn.classList.contains('recording')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        // Browser doesn't support speech recognition
        voiceInputBtn.style.display = 'none';
        console.log('Speech recognition not supported in this browser');
    }
    
    // Image upload functionality
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
                
                // Add analyzing message
                addMessage('Analyzing your image...', 'bot');
                
                // Send the image to the server
                sendImageToServer(currentImage);
                
                // Reset the file input
                imageInput.value = '';
            };
            reader.readAsDataURL(file);
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
                // Add bot response to chat
                addMessage(data.response, 'bot');
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your request.', 'bot');
            });
        }
    }
    
    function sendImageToServer(imageData) {
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        })
        .then(response => response.json())
        .then(data => {
            // Remove the "Analyzing" message
            const analyzingMessage = document.querySelector('.analyzing-message');
            if (analyzingMessage) {
                chatContainer.removeChild(analyzingMessage);
            }
            
            // Add bot response to chat
            addMessage(data.response, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Sorry, there was an error analyzing your image.', 'bot');
        });
    }
    
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
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        document.getElementById('theme-switch').checked = true;
    }
    
    // Save theme preference when changed
    document.getElementById('theme-switch').addEventListener('change', function() {
        if (this.checked) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });
});