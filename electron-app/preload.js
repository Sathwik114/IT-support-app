const { ipcRenderer } = require('electron');

const AUTH_STORAGE_KEYS = ['user', 'token'];

function restoreAuthState() {
    const authState = ipcRenderer.sendSync('auth:get-state') || {};

    for (const key of AUTH_STORAGE_KEYS) {
        if (!localStorage.getItem(key) && authState[key]) {
            localStorage.setItem(key, authState[key]);
        }
    }
}

function persistExistingAuthState() {
    for (const key of AUTH_STORAGE_KEYS) {
        const value = localStorage.getItem(key);
        if (value) {
            ipcRenderer.send('auth:set-item', key, value);
        }
    }
}

restoreAuthState();
persistExistingAuthState();

window.addEventListener('DOMContentLoaded', () => {
    restoreAuthState();
    persistExistingAuthState();
});

const originalSetItem = localStorage.setItem.bind(localStorage);
const originalRemoveItem = localStorage.removeItem.bind(localStorage);
const originalClear = localStorage.clear.bind(localStorage);

localStorage.setItem = (key, value) => {
    originalSetItem(key, value);

    if (AUTH_STORAGE_KEYS.includes(key)) {
        ipcRenderer.send('auth:set-item', key, value);
    }
};

localStorage.removeItem = (key) => {
    originalRemoveItem(key);

    if (AUTH_STORAGE_KEYS.includes(key)) {
        ipcRenderer.send('auth:remove-item', key);
    }
};

localStorage.clear = () => {
    originalClear();
    ipcRenderer.send('auth:clear');
};

ipcRenderer.on('desktop:auth-state', () => {
    persistExistingAuthState();
});

ipcRenderer.on('desktop:notification-click', (event, payload) => {
    window.postMessage({
        type: 'desktop-notification-click',
        notification: payload || {}
    }, '*');
});

window.addEventListener('message', (event) => {
    const data = event.data || {};
    if (data.type === 'desktop-notification') {
        ipcRenderer.send('notification:show', data.title, data.body, data.notification || {});
    }

    if (data.type === 'desktop-auth-set') {
        const authState = data.authState || {};
        for (const key of AUTH_STORAGE_KEYS) {
            if (authState[key]) {
                ipcRenderer.send('auth:set-item', key, authState[key]);
            }
        }
    }

    if (data.type === 'desktop-auth-clear') {
        ipcRenderer.send('auth:clear');
    }
});
