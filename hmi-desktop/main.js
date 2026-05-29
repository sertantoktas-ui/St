/**
 * AXTEA CNC HMI – Electron Main Process
 * Handles: window lifecycle, OSAI TCP bridge, auto-updater, tray icon
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, shell } = require('electron');
const path   = require('path');
const net    = require('net');
const os     = require('os');

// ── Dev flag ──────────────────────────────────────────────────────────────────
const isDev = process.argv.includes('--dev') || !app.isPackaged;

// ── Single instance lock ──────────────────────────────────────────────────────
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) { app.quit(); process.exit(0); }

let mainWindow = null;
let tray       = null;

// ── Window ────────────────────────────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width:           1440,
    height:          900,
    minWidth:        1280,
    minHeight:       800,
    title:           'AXTEA CNC HMI',
    backgroundColor: '#0D1117',
    show:            false,
    frame:           true,
    titleBarStyle:   process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      preload:          path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration:  false,
      sandbox:          false,
    },
  });

  // Load the HMI page
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  // Show only when ready to avoid flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (process.platform !== 'darwin') mainWindow.maximize();
  });

  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  mainWindow.on('closed', () => { mainWindow = null; });

  // macOS: keep app running when window closed
  mainWindow.on('close', (e) => {
    if (process.platform === 'darwin' && !app.isQuitting) {
      e.preventDefault();
      mainWindow.hide();
    }
  });

  buildMenu();
}

// ── App menu ──────────────────────────────────────────────────────────────────
function buildMenu() {
  const template = [
    ...(process.platform === 'darwin' ? [{
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' }, { role: 'hideOthers' }, { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' },
      ]
    }] : []),
    {
      label: 'File',
      submenu: [
        {
          label: 'Connect to OSAI…',
          accelerator: 'CmdOrCtrl+Shift+C',
          click: () => mainWindow?.webContents.send('menu-open-conn'),
        },
        { type: 'separator' },
        process.platform === 'darwin' ? { role: 'close' } : { role: 'quit' },
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Home',    accelerator: 'CmdOrCtrl+1', click: () => mainWindow?.webContents.send('menu-nav', 'home') },
        { label: 'Design',  accelerator: 'CmdOrCtrl+2', click: () => mainWindow?.webContents.send('menu-nav', 'design') },
        { label: 'Work',    accelerator: 'CmdOrCtrl+3', click: () => mainWindow?.webContents.send('menu-nav', 'work') },
        { label: 'Inspect', accelerator: 'CmdOrCtrl+4', click: () => mainWindow?.webContents.send('menu-nav', 'inspect') },
        { label: 'Analyze', accelerator: 'CmdOrCtrl+5', click: () => mainWindow?.webContents.send('menu-nav', 'analyze') },
        { type: 'separator' },
        { role: 'togglefullscreen' },
        ...(isDev ? [{ type: 'separator' }, { role: 'toggleDevTools' }, { role: 'reload' }] : []),
      ]
    },
    {
      label: 'Machine',
      submenu: [
        { label: 'Start Program',  accelerator: 'F5',  click: () => mainWindow?.webContents.send('machine-cmd', 'start') },
        { label: 'Pause Program',  accelerator: 'F6',  click: () => mainWindow?.webContents.send('machine-cmd', 'pause') },
        { label: 'Stop Program',   accelerator: 'F7',  click: () => mainWindow?.webContents.send('machine-cmd', 'stop') },
        { label: 'Reset',          accelerator: 'F8',  click: () => mainWindow?.webContents.send('machine-cmd', 'reset') },
        { label: 'Homing',         accelerator: 'F9',  click: () => mainWindow?.webContents.send('machine-cmd', 'homing') },
      ]
    },
    {
      label: 'Help',
      submenu: [
        { label: 'About AXTEA CNC HMI', click: () => showAbout() },
        { label: 'System Info',         click: () => showSysInfo() },
        { type: 'separator' },
        { label: 'AXTEA Website', click: () => shell.openExternal('https://axtea.com') },
      ]
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

function showAbout() {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'AXTEA CNC HMI',
    message: 'AXTEA CNC HMI',
    detail: `Version: ${app.getVersion()}\nPlatform: ${os.platform()} ${os.arch()}\nElectron: ${process.versions.electron}\nNode: ${process.versions.node}\n\nAXTEA – Integrated Woodworking Solutions`,
    buttons: ['OK'],
    icon: path.join(__dirname, 'build', 'icon.png'),
  }).catch(() => {});
}

function showSysInfo() {
  const info = [
    `OS: ${os.platform()} ${os.release()} ${os.arch()}`,
    `CPU: ${os.cpus()[0].model} × ${os.cpus().length}`,
    `RAM: ${Math.round(os.totalmem()/1024/1024)} MB`,
    `Free: ${Math.round(os.freemem()/1024/1024)} MB`,
    `Hostname: ${os.hostname()}`,
    `Network interfaces:`,
    ...Object.entries(os.networkInterfaces()).flatMap(([name, addrs]) =>
      (addrs||[]).filter(a=>!a.internal&&a.family==='IPv4').map(a=>`  ${name}: ${a.address}`)
    ),
  ].join('\n');
  dialog.showMessageBox(mainWindow, {
    type: 'info', title: 'System Info', message: 'System Info', detail: info, buttons: ['OK'],
  }).catch(() => {});
}

// ═══════════════════════════════════════════════════════════════════════════════
// OSAI TCP BRIDGE  (main process ↔ renderer via IPC)
// ═══════════════════════════════════════════════════════════════════════════════

let osaiSocket   = null;
let osaiHost     = '192.168.1.10';
let osaiPort     = 5050;
let osaiConnected = false;

const STX = 0x02, ETX = 0x03;

function osaiSend(cmd, payload = '') {
  if (!osaiSocket || !osaiConnected) return false;
  const frame = `\x02${cmd}${payload ? ',' + payload : ''}\x03`;
  try { osaiSocket.write(frame, 'ascii'); return true; }
  catch (e) { return false; }
}

ipcMain.handle('osai-connect', async (_e, { host, port, simulation }) => {
  osaiHost = host;
  osaiPort = port;

  if (simulation) {
    osaiConnected = true;
    return { ok: true, simulation: true };
  }

  return new Promise((resolve) => {
    osaiSocket = new net.Socket();
    osaiSocket.setTimeout(3000);

    osaiSocket.connect(port, host, () => {
      osaiConnected = true;
      resolve({ ok: true, simulation: false });
    });

    osaiSocket.on('data', (buf) => {
      // Parse OSAI response frames and forward to renderer
      const str = buf.toString('ascii');
      mainWindow?.webContents.send('osai-data', str);
    });

    osaiSocket.on('error', (err) => {
      osaiConnected = false;
      mainWindow?.webContents.send('osai-status', { connected: false, error: err.message });
      resolve({ ok: false, error: err.message });
    });

    osaiSocket.on('timeout', () => {
      osaiSocket.destroy();
      osaiConnected = false;
      resolve({ ok: false, error: 'Connection timed out' });
    });

    osaiSocket.on('close', () => {
      osaiConnected = false;
      mainWindow?.webContents.send('osai-status', { connected: false });
    });
  });
});

ipcMain.handle('osai-disconnect', async () => {
  if (osaiSocket) { osaiSocket.destroy(); osaiSocket = null; }
  osaiConnected = false;
  return { ok: true };
});

ipcMain.handle('osai-command', async (_e, { cmd, payload }) => {
  return { ok: osaiSend(cmd, payload) };
});

ipcMain.handle('osai-status', async () => {
  return { connected: osaiConnected, host: osaiHost, port: osaiPort };
});

// System info for renderer
ipcMain.handle('get-sysinfo', async () => ({
  platform: process.platform,
  arch:     os.arch(),
  hostname: os.hostname(),
  version:  app.getVersion(),
  electron: process.versions.electron,
  network: Object.entries(os.networkInterfaces()).flatMap(([name, addrs]) =>
    (addrs||[]).filter(a=>!a.internal&&a.family==='IPv4').map(a=>({ name, address: a.address }))
  ),
}));

// ── App lifecycle ─────────────────────────────────────────────────────────────
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
    else mainWindow?.show();
  });
});

app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});

app.on('before-quit', () => { app.isQuitting = true; });

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
