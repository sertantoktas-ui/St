/**
 * Preload – exposes a safe, typed bridge between renderer (index.html) and main process.
 * Only the listed channels are accessible; no arbitrary Node APIs exposed.
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('AXTEA', {
  // OSAI TCP communication
  osaiConnect:    (opts)   => ipcRenderer.invoke('osai-connect',    opts),
  osaiDisconnect: ()       => ipcRenderer.invoke('osai-disconnect'),
  osaiCommand:    (cmd, p) => ipcRenderer.invoke('osai-command',    { cmd, payload: p || '' }),
  osaiStatus:     ()       => ipcRenderer.invoke('osai-status'),

  // Incoming data from real OSAI unit
  onOsaiData:   (cb) => ipcRenderer.on('osai-data',   (_e, d) => cb(d)),
  onOsaiStatus: (cb) => ipcRenderer.on('osai-status', (_e, s) => cb(s)),

  // Menu-triggered events
  onMenuNav:     (cb) => ipcRenderer.on('menu-nav',      (_e, screen) => cb(screen)),
  onMenuConn:    (cb) => ipcRenderer.on('menu-open-conn',_e          => cb()),
  onMachineCmd:  (cb) => ipcRenderer.on('machine-cmd',   (_e, cmd)   => cb(cmd)),

  // System info
  getSysinfo: () => ipcRenderer.invoke('get-sysinfo'),

  // Platform helpers
  platform: process.platform,  // 'win32' | 'darwin' | 'linux'
  version:  process.env.npm_package_version || '1.0.0',
});
