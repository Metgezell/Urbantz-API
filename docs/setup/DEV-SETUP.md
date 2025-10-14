# 🚀 Urbantz Development Setup - Stabiel & Live-reload

Deze setup zorgt ervoor dat je servers stabiel draaien zonder dat Cursor blijft hangen, met live-reload functionaliteit.

## 🎯 Wat je krijgt

- ✅ **Stabiele server startup** - geen meer "hangende" Cursor
- ✅ **Live-reload** - code wijzigingen worden automatisch herladen
- ✅ **Health checks** - servers melden wanneer ze echt klaar zijn
- ✅ **Eén-toets startup** - alles starten met één commando
- ✅ **Automatische port management** - conflicten worden opgelost
- ✅ **Debugging support** - breakpoints werken perfect

## 🚀 Snelle Start

### Optie 1: PowerShell Script (Aanbevolen)
```powershell
# Start beide servers met live-reload
.\start-urbantz-dev.ps1 -Both -Watch

# Alleen Python server
.\start-urbantz-dev.ps1 -Python -Watch

# Alleen Node.js server  
.\start-urbantz-dev.ps1 -Node -Watch

# Stop alle servers
.\start-urbantz-dev.ps1 -Kill

# Help
.\start-urbantz-dev.ps1 -Help
```

### Optie 2: Cursor/VS Code Tasks
1. **Ctrl+Shift+P** → "Tasks: Run Task"
2. Kies **"Backend: Start Both Servers"**
3. Of kies individuele servers:
   - "Backend: Start Python Server (Fast)"
   - "Backend: Start Node.js Server"

### Optie 3: Terminal Commands
```powershell
# Python server met live-reload
npx watchfiles "python start-server-with-reload.py" --extensions py

# Node.js server met live-reload  
npm run server:watch

# Beide servers tegelijk (in aparte terminals)
```

## 🔧 Server Details

### Python Server (Poort 8080)
- **Bestand**: `start-server-with-reload.py`
- **Endpoints**:
  - `GET /api/health` - Health check
  - `GET /api/status` - Server status
  - `POST /api/smart-analyze` - AI document analysis
  - `POST /api/urbantz-export` - Export to Urbantz

### Node.js Server (Poort 3001)  
- **Bestand**: `local-server.js`
- **Endpoints**:
  - `GET /api/health` - Health check
  - `POST /api/smart-analyze` - AI document analysis
  - `POST /api/urbantz-export` - Export to Urbantz
  - `POST /api/analyze-document` - File upload analysis

## 🐛 Debugging

### In Cursor/VS Code:
1. **F5** of **Ctrl+Shift+D** → Debug panel
2. Kies configuratie:
   - **"Debug Python Server (Fast)"** - Debug Python
   - **"Debug Node.js Server"** - Debug Node.js
   - **"Debug Both Servers"** - Debug beide

### Breakpoints:
- Zet breakpoints in je code
- Start debug configuratie
- Servers starten automatisch in debug mode
- Breakpoints werken direct

## 📊 Health Checks

Test of je servers draaien:

```bash
# Python server
curl http://localhost:8080/api/health

# Node.js server  
curl http://localhost:3001/api/health

# Of in browser:
http://localhost:8080/api/health
http://localhost:3001/api/health
```

## 🔄 Live-reload

### Python (met watchfiles):
- Wijzigingen in `.py` bestanden triggeren herstart
- Server herstart automatisch binnen 1-2 seconden
- Geen handmatige herstart nodig

### Node.js (met nodemon):
- Wijzigingen in `.js` bestanden triggeren herstart
- `node_modules/` en `dist/` worden genegeerd
- 1 seconde delay om multiple saves te voorkomen

## 🛠️ Troubleshooting

### Server start niet op:
```powershell
# Check welke poorten bezet zijn
netstat -ano | findstr :8080
netstat -ano | findstr :3001

# Kill processen handmatig
taskkill /PID <PID> /F

# Of gebruik het script
.\start-urbantz-dev.ps1 -Kill
```

### Cursor blijft hangen:
- ❌ **Gebruik NIET** "Run Code" voor long-running servers
- ✅ **Gebruik WEL** Tasks (Ctrl+Shift+P → Tasks) of PowerShell script
- ✅ **Check** of servers echt draaien via health endpoints

### Live-reload werkt niet:
```powershell
# Installeer dependencies
npm install

# Check of watchfiles werkt
npx watchfiles --help

# Check of nodemon werkt  
npx nodemon --help
```

### OneDrive vertraging:
- Overweeg project te verplaatsen naar `C:\dev\urbantz\`
- Schakel real-time AV-scan uit voor project folder
- Gebruik lokale git repo i.p.v. OneDrive sync

## 📁 Bestandsstructuur

```
├── .vscode/
│   ├── tasks.json          # VS Code tasks voor server management
│   └── launch.json         # Debug configuraties
├── start-urbantz-dev.ps1   # PowerShell script voor alles
├── start-server-with-reload.py  # Verbeterde Python server
├── local-server.js         # Node.js server
├── nodemon.json           # Nodemon configuratie
└── package.json           # Met nieuwe scripts
```

## 🎉 Voordelen van deze setup

1. **Geen meer hangende Cursor** - servers starten in dedicated terminals
2. **Automatische herstart** - code wijzigingen worden direct toegepast  
3. **Health monitoring** - weet wanneer servers echt klaar zijn
4. **Debug support** - breakpoints werken perfect
5. **Port management** - geen conflicten meer
6. **Eén commando** - start alles met één toets

## 🚀 Volgende stappen

1. **Test de setup**: `.\start-urbantz-dev.ps1 -Both -Watch`
2. **Check health**: Open `http://localhost:8080/api/health`
3. **Debug test**: Zet breakpoint en start debug configuratie
4. **Live-reload test**: Wijzig code en zie automatische herstart

Je bent nu klaar voor stabiele development! 🎯
