// AI Security Lab - Main App Script

console.log('AI Security Lab loaded.');

document.addEventListener('DOMContentLoaded', () => {
  // --- Health Check ---
  const healthBtn = document.getElementById('healthCheckBtn');
  const responseContainer = document.getElementById('responseContainer');
  const responseContent = document.getElementById('responseContent');

  if (healthBtn && responseContainer && responseContent) {
    healthBtn.addEventListener('click', async () => {
      healthBtn.disabled = true;
      healthBtn.textContent = 'Checking…';
      responseContainer.classList.remove('hidden', 'success', 'error');

      try {
        const res = await fetch('/api/health');
        const data = await res.json();
        responseContent.textContent = JSON.stringify(data, null, 2);
        responseContainer.classList.add(res.ok ? 'success' : 'error');
      } catch (err) {
        responseContent.textContent = JSON.stringify({ error: err.message }, null, 2);
        responseContainer.classList.add('error');
      } finally {
        healthBtn.disabled = false;
        healthBtn.textContent = 'Check API Health';
        responseContainer.classList.remove('hidden');
      }
    });
  }

  // --- Mock Chat ---
  const chatPrompt = document.getElementById('chatPrompt');
  const chatSendBtn = document.getElementById('chatSendBtn');
  const chatResponseContainer = document.getElementById('chatResponseContainer');
  const chatResponse = document.getElementById('chatResponse');

  if (chatPrompt && chatSendBtn && chatResponseContainer && chatResponse) {
    chatSendBtn.addEventListener('click', async () => {
      chatSendBtn.disabled = true;
      chatSendBtn.textContent = 'Sending…';
      chatResponseContainer.classList.add('hidden');
      chatResponseContainer.classList.remove('success', 'error', 'blocked');

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: chatPrompt.value }),
        });

        const data = await res.json();
        chatResponse.textContent = JSON.stringify(data, null, 2);

        if (data.status === 'ok') {
          chatResponseContainer.classList.add('success');
        } else if (data.status === 'blocked') {
          chatResponseContainer.classList.add('blocked');
        } else {
          chatResponseContainer.classList.add('error');
        }
      } catch (err) {
        chatResponse.textContent = JSON.stringify({ error: err.message }, null, 2);
        chatResponseContainer.classList.add('error');
      } finally {
        chatSendBtn.disabled = false;
        chatSendBtn.textContent = 'Send to Mock Chat';
        chatResponseContainer.classList.remove('hidden');
      }
    });
  }
});
