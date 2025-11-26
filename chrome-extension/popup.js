const statusEl = document.getElementById('status');
const helloBtn = document.getElementById('helloBtn');
const signinBtn = document.getElementById('signinBtn');
const authStatusEl = document.getElementById('authStatus');

function formatExpiry(ms) {
  if (!ms) return '';
  const dt = new Date(ms);
  return dt.toLocaleTimeString();
}

async function loadAuthState() {
  const { gmailAuth } = await chrome.storage.local.get('gmailAuth');
  const now = Date.now();
  if (gmailAuth?.token && gmailAuth?.expiresAt && gmailAuth.expiresAt > now) {
    authStatusEl.textContent = `Signed in (expires ~${formatExpiry(gmailAuth.expiresAt)})`;
  } else if (gmailAuth?.expiresAt && gmailAuth.expiresAt <= now) {
    authStatusEl.textContent = 'Token expired. Please sign in again.';
  } else {
    authStatusEl.textContent = 'Not signed in.';
  }
}

helloBtn.addEventListener('click', async () => {
  statusEl.textContent = 'Sending message…';
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.runtime.sendMessage({ type: 'HELLO_WORLD', tabId: tab?.id });
    statusEl.textContent = 'Message sent! Check the console for logs.';
  } catch (error) {
    console.error(error);
    statusEl.textContent = 'Could not send message.';
  }
});

signinBtn.addEventListener('click', async () => {
  authStatusEl.textContent = 'Opening Google sign-in…';
  try {
    const resp = await chrome.runtime.sendMessage({ type: 'START_GMAIL_SIGNIN' });
    if (!resp?.ok) {
      throw new Error(resp?.error || 'Unknown error');
    }
    authStatusEl.textContent = `Signed in! Token stored (expires ~${formatExpiry(resp.expiresAt)})`;
  } catch (error) {
    console.error(error);
    authStatusEl.textContent = `Sign-in failed: ${error.message}`;
  }
});

loadAuthState();
