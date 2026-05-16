document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const topicInput = document.getElementById('topic');
    const roundsInput = document.getElementById('rounds');
    const transcriptDiv = document.getElementById('transcript');
    const spinner = document.getElementById('spinner');
    const setupForm = document.getElementById('setupForm');

    startBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        const rounds = parseInt(roundsInput.value);

        if (!topic) {
            alert('Please enter a debate topic.');
            return;
        }

        // Reset UI
        transcriptDiv.innerHTML = '';
        startBtn.disabled = true;
        spinner.style.display = 'block';

        try {
            const response = await fetch('/debate/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic, rounds })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to start debate');
            }

            const data = await response.json();
            displayTranscript(data.messages);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
        } finally {
            startBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });

    function displayTranscript(messages) {
        messages.forEach((msg, index) => {
            const card = document.createElement('div');
            card.className = `message-card ${msg.agent.toLowerCase()}`;
            card.style.animationDelay = `${index * 0.2}s`;

            const timestamp = new Date(msg.timestamp).toLocaleTimeString();
            
            card.innerHTML = `
                <div class="meta">Round ${msg.round} • ${timestamp}</div>
                <div class="agent-name">
                    ${msg.agent}
                    <span class="stance-badge stance-${msg.stance.toLowerCase()}">${msg.stance}</span>
                </div>
                <div class="message-content">${msg.message}</div>
            `;

            transcriptDiv.appendChild(card);
        });
    }
});
