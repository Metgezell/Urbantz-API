# 🔄 Git Backup & Restore Workflow

> **Doel**: Snel een snapshot nemen van een werkende API-koppeling en bij problemen terugzetten.  
> **Waarom**: Voorkomt dat Cursor je werkende API setup verliest als de environment breekt.

---

## 📦 Commando: "backup code"

### Wat gebeurt er?
1. Voeg alle bestanden toe aan git staging met `git add .`
2. Maak een commit met de boodschap "Backup: working API integration"
3. (Optioneel) Push de commit naar origin/main als een remote repository bestaat
4. Bevestig met: "Backup created successfully"

### Wanneer gebruiken?
- ✅ API koppeling werkt correct
- ✅ Net een feature af
- ✅ Voor grote refactoring
- ✅ Einde van de werkdag

### Terminal commando's (handmatig)
```bash
git add .
git commit -m "Backup: working API integration"
git push origin main  # optioneel, als remote bestaat
```

---

## 🔄 Commando: "restore backup"

### Wat gebeurt er?
1. Toon de laatste 5 commits met hun ID's en boodschappen
2. Vraag welke commit je wil terugzetten
3. Voer `git checkout <commit_id>` uit 
4. Bevestig met: "Project restored to <commit_id>"

### Wanneer gebruiken?
- ⚠️ API koppeling is kapot
- ⚠️ Environment geeft errors
- ⚠️ Code werkt niet meer na wijzigingen
- ⚠️ Wil oude versie inspecteren

### Terminal commando's (handmatig)
```bash
# Toon laatste commits
git log --oneline -5

# Terug naar specifieke commit
git checkout <commit_id>

# Terug naar laatste versie van branch
git checkout main
```

### ⚠️ Belangrijk
- `git checkout <commit_id>` zet je in "detached HEAD" state
- Om terug te gaan naar je branch: `git checkout main`
- Om wijzigingen permanent te maken: `git checkout -b new-branch-name`

---

## 🧪 Commando: "new experiment"

### Wat gebeurt er?
1. Maak een nieuwe branch aan met de naam `experiment/<datum>-<beschrijving>`
2. Wissel naar die branch zodat je veilig kan testen zonder hoofdversie te breken

### Wanneer gebruiken?
- 🔬 Nieuwe feature testen
- 🔬 Verschillende aanpak proberen
- 🔬 Breaking changes maken
- 🔬 Experimenteren zonder risico

### Terminal commando's (handmatig)
```bash
# Maak en wissel naar nieuwe branch
git checkout -b experiment/2025-10-14-nieuwe-feature

# Toon alle branches
git branch -a

# Terug naar main
git checkout main

# Verwijder experiment branch (als niet meer nodig)
git branch -d experiment/2025-10-14-nieuwe-feature
```

### Branch naamgeving voorbeelden
```
experiment/2025-10-14-urbantz-webhook
experiment/2025-10-14-claude-model-upgrade
experiment/2025-10-14-pdf-extraction-fix
```

---

## 📋 Snelle Referentie

| Situatie | Commando | Resultaat |
|----------|----------|-----------|
| Code werkt, wil opslaan | "backup code" | Commit gemaakt |
| Code kapot, terug naar werkend | "restore backup" | Kies oude commit |
| Wil experiment doen | "new experiment" | Veilige test branch |
| Terug naar main branch | `git checkout main` | Terug naar hoofdversie |
| Toon huidige branch | `git branch` | Zie waar je bent |
| Status bekijken | `git status` | Zie wijzigingen |

---

## 🎯 Best Practices

### ✅ DO
- Backup maken VOOR grote wijzigingen
- Duidelijke experiment branch namen gebruiken
- Regelmatig backups maken (elke werkende staat)
- Experiment branches verwijderen na gebruik

### ❌ DON'T
- Niet pushen naar main zonder testen
- Niet werken in detached HEAD state zonder nieuwe branch
- Niet experiment branches ophopen (opruimen!)
- Niet vergeten terug te gaan naar main na restore

---

## 🚀 Gebruik met Cursor AI

In Cursor, typ gewoon:
- **"backup code"** - AI voert de backup workflow uit
- **"restore backup"** - AI toont commits en helpt terugzetten
- **"new experiment"** - AI maakt experiment branch aan

De AI begrijpt deze commando's en voert de juiste git operaties uit!

---

## 📝 Notities

### Urbantz API Project Specifiek
- **Belangrijke bestanden om te backuppen**:
  - `scripts/local-server.js` - Lokale server met API routes
  - `api/*.js` - API endpoint handlers
  - `.env` - Environment variabelen (⚠️ niet in git!)
  - `functions/src/*.ts` - Firebase functions

### Als iets misgaat
1. Geen paniek! Git onthoudt alles
2. Typ `git reflog` om ALLE acties te zien
3. Gebruik `git reset --hard <commit_id>` om écht terug te gaan
4. Vraag Cursor AI om hulp: "help me restore to working state"

---

## 🔗 Gerelateerde Documentatie
- [DEV-SETUP.md](./DEV-SETUP.md) - Development environment setup
- [FIREBASE-SETUP.md](./FIREBASE-SETUP.md) - Firebase configuratie
- [../SERVER-README.md](../SERVER-README.md) - Server documentatie

---

**💡 Pro Tip**: Maak elke dag minimaal één backup voordat je stopt met werken. Je toekomstige zelf zal je bedanken! 🙏

