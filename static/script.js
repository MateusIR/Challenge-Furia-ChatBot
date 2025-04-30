window.onload = () => {

  fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: '' })
  })
  .then(response => response.json())
  .then(data => {
    
    const chatBox = document.querySelector('.chat-box');
    const botMessage = document.createElement('div');
    botMessage.classList.add('message', 'bot');
    botMessage.textContent = data.reply;
    chatBox.appendChild(botMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
  });
};





const form = document.getElementById('chat-form');
const input = document.getElementById('chat-input');
const chatBox = document.getElementById('chat-box');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const userText = input.value.trim();
  if (!userText) return;

  addMessage(userText, 'user');
  input.value = '';

  addLoading();

  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userText })
  });
  const data = await res.json();

  removeLoading();
  addMessage(data.reply, 'bot');
});

function addMessage(text, sender) {
  const div = document.createElement('div');
  div.className = `message ${sender}`;
  
  if (sender === 'bot') {
    div.innerHTML = text;
  } else {
    div.innerText = text;
  }
  
  chatBox.appendChild(div);
 
}

function addLoading() {
  const div = document.createElement('div');
  div.className = 'message bot loading';
  div.innerText = 'Digitando...';
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeLoading() {
  const loadingDiv = document.querySelector('.loading');
  if (loadingDiv) loadingDiv.remove();
}

