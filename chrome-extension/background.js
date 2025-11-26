chrome.runtime.onInstalled.addListener(() => {
  console.log('Phish Net demo extension installed.');
});

const { oauth2 } = chrome.runtime.getManifest();
const OAUTH_CLIENT_ID = oauth2?.client_id || '';
const OAUTH_SCOPES = oauth2?.scopes || ['https://www.googleapis.com/auth/gmail.readonly'];

function parseHashParams(url) {
  const hash = url.split('#')[1] || '';
  return Object.fromEntries(new URLSearchParams(hash));
}

async function getStoredAuth() {
  const { gmailAuth } = await chrome.storage.local.get('gmailAuth');
  if (!gmailAuth?.token || !gmailAuth?.expiresAt) return null;
  if (gmailAuth.expiresAt <= Date.now()) return null;
  return gmailAuth;
}

function decodeBase64UrlToUint8(base64) {
  const normalized = base64.replace(/-/g, '+').replace(/_/g, '/');
  const binary = atob(normalized);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function bytesToBase64(bytes) {
  let binary = '';
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

async function downloadEmlFile(messageId, subject) {
  const auth = await getStoredAuth();
  if (!auth) {
    throw new Error('NOT_SIGNED_IN');
  }

  const resp = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/messages/${messageId}?format=raw`, {
    headers: { Authorization: `Bearer ${auth.token}` },
  });
  if (!resp.ok) {
    let detail = '';
    try {
      const errJson = await resp.json();
      detail = errJson?.error?.message || JSON.stringify(errJson);
    } catch (e) {
      try {
        detail = await resp.text();
      } catch (e2) {
        detail = '';
      }
    }
    throw new Error(`Gmail API error ${resp.status}${detail ? `: ${detail}` : ''}`);
  }
  const data = await resp.json();
  if (!data.raw) {
    throw new Error('No raw message data returned');
  }
  const bytes = decodeBase64UrlToUint8(data.raw);
  const dataUrl = `data:message/rfc822;base64,${bytesToBase64(bytes)}`;
  const filenameSafeSubject = subject ? subject.replace(/[/\\\\:*?"<>|]+/g, '').slice(0, 60) : 'email';
  const filename = `phish-net/${filenameSafeSubject || 'email'}-${messageId}.eml`;

  await chrome.downloads.download({ url: dataUrl, filename, saveAs: false });
}

async function resolveMessageIdFromThread(threadId) {
  const auth = await getStoredAuth();
  if (!auth) {
    throw new Error('NOT_SIGNED_IN');
  }
  const resp = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/threads/${threadId}`, {
    headers: { Authorization: `Bearer ${auth.token}` },
  });
  if (!resp.ok) {
    throw new Error(`Gmail API thread error ${resp.status}`);
  }
  const data = await resp.json();
  const msgs = data.messages;
  if (!Array.isArray(msgs) || msgs.length === 0) {
    throw new Error('No messages found in thread');
  }
  // Use the last message in the thread (most recent)
  return msgs[msgs.length - 1].id;
}

async function startGmailSignIn() {
  if (!OAUTH_CLIENT_ID || OAUTH_CLIENT_ID.startsWith('REPLACE_WITH_')) {
    throw new Error('OAuth client ID is not configured in manifest/background');
  }

  const redirectUri = chrome.identity.getRedirectURL();
  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  authUrl.searchParams.set('client_id', OAUTH_CLIENT_ID);
  authUrl.searchParams.set('response_type', 'token');
  authUrl.searchParams.set('redirect_uri', redirectUri);
  authUrl.searchParams.set('scope', OAUTH_SCOPES.join(' '));
  authUrl.searchParams.set('prompt', 'consent');

  // Debug logging to help diagnose redirect_uri_mismatch issues
  console.log('Phish Net OAuth', {
    redirectUri,
    authUrl: authUrl.toString(),
  });

  const launchResult = await chrome.identity.launchWebAuthFlow({
    url: authUrl.toString(),
    interactive: true
  });

  const params = parseHashParams(launchResult);
  const token = params.access_token;
  if (!token) {
    throw new Error('No access_token returned');
  }
  const expiresInSec = Number(params.expires_in || 0);
  const expiresAt = Date.now() + expiresInSec * 1000;

  await chrome.storage.local.set({ gmailAuth: { token, expiresAt } });
  return { token, expiresAt };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'HELLO_WORLD') {
    console.log('Received HELLO_WORLD from popup', { sender, message });
    if (message.tabId) {
      chrome.tabs.sendMessage(message.tabId, { type: 'HELLO_FROM_BACKGROUND' });
    }
    sendResponse({ ok: true });
    return true;
  }

  if (message?.type === 'EMAIL_OPENED') {
    console.log('Phish Net: email opened', {
      from: sender?.tab?.url,
      threadId: message.threadId,
      messageId: message.messageId,
      subject: message.subject,
      url: message.url,
    });

    const promise = (async () => {
      let messageId = message?.messageId;
      if (!messageId && message?.threadId) {
        messageId = await resolveMessageIdFromThread(message.threadId);
      }
      if (!messageId) {
        throw new Error('No messageId found on page or thread');
      }
      await downloadEmlFile(messageId, message.subject);
    })();

    promise
      .then(() => sendResponse?.({ ok: true }))
      .catch((error) => {
        console.error('Failed to download EML', error);
        if (error.message === 'NOT_SIGNED_IN' && sender?.tab?.id) {
          chrome.tabs.sendMessage(sender.tab.id, { type: 'NOT_SIGNED_IN' }).catch(() => {});
        }
        sendResponse?.({ ok: false, error: error.message });
      });
    return true;
  }

  if (message?.type === 'START_GMAIL_SIGNIN') {
    startGmailSignIn()
      .then((result) => sendResponse?.({ ok: true, ...result }))
      .catch((error) => sendResponse?.({ ok: false, error: error.message }));
    return true; // keep the message channel open for async response
  }
  return undefined;
});
