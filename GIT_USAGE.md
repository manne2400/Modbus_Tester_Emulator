# Git Brug - Modbus Tester

## Repository Status
✅ **Git repository er initialiseret og første commit er lavet**

## Grundlæggende Git Kommandoer

### Se status
```bash
git status
```

### Se commit historie
```bash
git log --oneline
```

### Tilføj ændringer
```bash
# Tilføj alle ændrede filer
git add .

# Eller tilføj specifikke filer
git add filnavn.py
```

### Commit ændringer
```bash
git commit -m "Beskrivelse af ændringerne"
```

### Se forskelle
```bash
# Se forskelle i filer der ikke er staged
git diff

# Se forskelle i staged filer
git diff --staged
```

### Gå tilbage til tidligere version
```bash
# Se alle commits
git log --oneline

# Gå tilbage til en specifik commit
git checkout <commit-hash>

# Gå tilbage til seneste commit
git checkout master
```

### Opret ny branch (til eksperimenter)
```bash
# Opret og skift til ny branch
git checkout -b feature-navn

# Skift tilbage til master
git checkout master

# Se alle branches
git branch
```

## Hvad er gemt i Git

✅ **Alle kildefiler** (Python kode)
✅ **Konfigurationsfiler** (requirements.txt, .spec filer)
✅ **Dokumentation** (README.md, STATUS.md, guides)
✅ **Build scripts**

❌ **Ikke gemt:**
- `__pycache__/` - Python cache
- `dist/` - Byggede executables
- `build/` - Build artifacts
- `*.log` - Log filer
- User config data (gemmes i ~/.modbus_tester/)

## Eksempel Workflow

```bash
# 1. Lav ændringer i koden
# 2. Tjek status
git status

# 3. Tilføj ændringer
git add .

# 4. Commit
git commit -m "Tilføj ny feature X"

# 5. Se historie
git log --oneline
```

## Vigtige Noter

- **Lokalt repository:** Dette er kun lokalt - ikke synkroniseret med remote
- **Brugerdata:** Config filer gemmes i `~/.modbus_tester/` og er ikke i Git
- **Build artifacts:** Executables og build filer er ignoreret (se .gitignore)

## Hvis du vil tilføje Remote Repository

```bash
# Tilføj remote (fx GitHub)
git remote add origin https://github.com/brugernavn/modbus-tester.git

# Push til remote
git push -u origin master
```

---
**Repository oprettet:** 2025-11-16
**Første commit:** Initial commit med komplet Modbus Tester applikation
