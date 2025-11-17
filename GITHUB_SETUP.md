# Guide til at uploade til GitHub

## Trin 1: Opret repository på GitHub

1. Gå til [GitHub.com](https://github.com) og log ind
2. Klik på **"+"** i øverste højre hjørne → **"New repository"**
3. Vælg et navn (fx `Modbus_Tester` eller `modbus-tester`)
4. Vælg **Public** eller **Private** (som du foretrækker)
5. **VIGTIGT:** Lad være med at tilføje README, .gitignore eller license (vi har dem allerede)
6. Klik **"Create repository"**

## Trin 2: Tilføj alle ændringer og commit

Kør disse kommandoer i PowerShell (fra projektmappen):

```powershell
# Tilføj alle nye og ændrede filer
git add .

# Commit med en beskrivende besked
git commit -m "Tilføj simulator integration og multi-view funktionalitet"
```

## Trin 3: Tilføj GitHub remote og push

GitHub vil vise dig kommandoerne efter du har oprettet repository'et. De ser typisk sådan ud:

```powershell
# Tilføj GitHub repository som remote (erstatt YOUR_USERNAME og REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push til GitHub (første gang)
git push -u origin master
```

**Eller hvis din default branch hedder `main` i stedet for `master`:**

```powershell
git push -u origin main
```

## Hvad jeg har brug for fra dig:

1. **Dit GitHub brugernavn** - så jeg kan hjælpe med at sætte remote URL'en korrekt
2. **Repository navnet** - det navn du valgte da du oprettede repository'et

## Alternativ: Jeg kan hjælpe med kommandoerne

Hvis du giver mig:
- GitHub brugernavn
- Repository navn

Så kan jeg oprette kommandoerne for dig, som du bare skal køre.

## Efter første push

Efter første push kan du bruge:

```powershell
# For fremtidige opdateringer
git add .
git commit -m "Beskrivelse af ændringer"
git push
```

## Noter

- Alle dine lokale ændringer er allerede gemt lokalt med Git
- `.gitignore` er allerede sat op til at ignorere build filer, logs, etc.
- README.md er opdateret med alle nye funktioner
- Du kan altid se status med: `git status`

