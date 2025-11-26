console.log('Phish Net content script injected.');

function showToast(subjectText) {
  const toast = document.createElement('div');
  toast.textContent = subjectText || 'Phish Net: email opened';
  Object.assign(toast.style, {
    position: 'fixed',
    top: '12px',
    right: '12px',
    padding: '10px 12px',
    background: '#663399',
    color: '#fff',
    fontSize: '13px',
    borderRadius: '6px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
    zIndex: 2147483647,
    maxWidth: '320px',
    lineHeight: '1.3',
    fontFamily: 'Arial, sans-serif',
  });
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === 'HELLO_FROM_BACKGROUND') {
    console.log('Background says hello!');
  }
  if (message?.type === 'NOT_SIGNED_IN') {
    showToast('Phish Net: please sign in to Gmail in the popup');
  }
});

// --- Gmail email-open detection (debug helper) ---
(() => {
  let lastThreadId = null;

  function detectEmailOpen() {
    const header = document.querySelector('div[role="main"] h2[data-legacy-thread-id]');
    if (!header) return;

    const threadId = header.getAttribute('data-legacy-thread-id');
    if (!threadId || threadId === lastThreadId) return;

    lastThreadId = threadId;
    const subject = header.textContent?.trim() || '';
    const messageEl = document.querySelector('div[role="main"] div[data-legacy-message-id]');
    const messageId = messageEl?.getAttribute('data-legacy-message-id') || '';

    console.log('Phish Net detected opened email', { threadId, messageId, subject });
    showToast(subject ? `Phish Net: opened "${subject}"` : 'Phish Net: email opened');

    chrome.runtime.sendMessage({
      type: 'EMAIL_OPENED',
      threadId,
      messageId,
      subject,
      url: location.href,
    }).catch(() => {
      /* ignore if background not available */
    });
  }

  const observer = new MutationObserver(() => detectEmailOpen());
  observer.observe(document.documentElement, { childList: true, subtree: true });
  detectEmailOpen();

  const { pushState, replaceState } = history;
  history.pushState = function (...args) {
    const ret = pushState.apply(this, args);
    setTimeout(detectEmailOpen, 0);
    return ret;
  };
  history.replaceState = function (...args) {
    const ret = replaceState.apply(this, args);
    setTimeout(detectEmailOpen, 0);
    return ret;
  };

  window.addEventListener('popstate', () => detectEmailOpen());
})();
