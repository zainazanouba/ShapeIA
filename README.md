#  ShapeIA — Assistant Géométrique Intelligent

> **ShapeIA** est un assistant intelligent qui permet de générer, visualiser et analyser des formes géométriques (2D & 3D) à partir de simples descriptions en langage naturel (Français & Anglais & Darija).

---
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![React](https://img.shields.io/badge/React-Frontend-61dafb)
![Plotly](https://img.shields.io/badge/Plotly-3D%20Graphs-purple)
![NumPy](https://img.shields.io/badge/NumPy-Scientific-blueviolet)
![FuzzyWuzzy](https://img.shields.io/badge/FuzzyWuzzy-Text%20Matching-orange)

![NLP](https://img.shields.io/badge/NLP-Natural%20Language-blue)
![3D](https://img.shields.io/badge/3D-Visualization-brightgreen)
![AI](https://img.shields.io/badge/AI-Assistant-black)
![OpenSource](https://img.shields.io/badge/Open%20Source-Yes-success)
![License](https://img.shields.io/badge/License-Educational-lightgrey)


## 🚀 Fonctionnalités

✔ Compréhension du langage naturel (Français & Anglais & Darija)  
✔ Tolérance aux fautes d’orthographe (NLP fuzzy)  
✔ Génération de formes 2D & 3D  
✔ Calcul automatique :
- Aire  
- Volume  
- Circonférence  
- Surface latérale  

✔ Visualisation 3D interactive (rotation, zoom, déplacement)  
✔ Support de plusieurs formes dans une même scène  
✔ Interface Web type ChatBot  
✔ Tracé de fonctions 2D `f(x)=...` et surfaces 3D `f(x,y)=...`  

---


## 🧠 Exemple d'utilisation

| Commande utilisateur | Résultat |
|--------------------|--------|
| `Dessine un cube rouge de 5` | Cube 3D + Volume + Surface |
| `Kora bleue 10` | Sphère de rayon 10 |
| `Un cercle 4 et un carré 6` | Deux formes 2D |
| `Dessine un cube rouge et une sphère bleue` | Deux objets dans la même scène |
| `f(x)=x^2 + 2x + 1 domain [-3,3]` | Courbe 2D |
| `f(x,y)=cos(x)*sin(y) domain [-5,5]` | Surface 3D |

---

## 🧩 Architecture du projet

Le projet suit une architecture inspirée du modèle **MVC** :
```
└── 📁 ShapeIA_v2
    ├── 📁 backend
    │   ├── 📁 api
    │   │   ├── 🐍 __init__.py
    │   │   └── 🐍 main.py
    │   └── 📁 src
    │       ├── 🐍 __init__.py
    │       ├── 🐍 bot_logique.py
    │       ├── 🐍 function_plotter.py
    │       ├── 🐍 geometry.py
    │       └── 🐍 nlp_parser.py
    ├── 📁 web
    │   ├── 📁 src
    │   │   ├── 📄 App.jsx
    │   │   ├── 📄 main.jsx
    │   │   └── 🎨 styles.css
    │   ├── 🌐 index.html
    │   ├── ⚙️ package-lock.json
    │   ├── ⚙️ package.json
    │   └── 📄 vite.config.js
    ├── ⚙️ .gitignore
    ├── 📝 README.md
    ├── ⚙️ package-lock.json
    └── 📄 requirements.txt
```

---

## 🛠️ Technologies utilisées

| Technologie | Rôle |
|-----------|------|
| Python 3.9+ | Langage principal |
| FastAPI | API backend |
| React + Vite | Interface web |
| Plotly | Visualisation 3D |
| Numpy | Calcul matriciel |
| FuzzyWuzzy | Tolérance aux fautes |
| Levenshtein | Distance de similarité |

---

## ⚙️ Installation complète (Windows, macOS, Linux)

Ce projet contient:
- Un backend Python (`FastAPI`)
- Un frontend JavaScript (`React + Vite`)

### 1) Telecharger le projet

```bash
git clone <URL_DU_REPO>
cd ShapeIA_v2
```

### 2) Prérequis

Vérifiez d'abord les outils:

```bash
git --version
python --version
node -v
npm -v
```

Versions recommandées:
- Python `3.10+`
- Node.js `18+` (LTS)
- npm `9+`

### 3) Si les outils ne sont pas installés

#### Windows (PowerShell)

Installer les outils:

```powershell
winget install Git.Git
winget install Python.Python.3.11
winget install OpenJS.NodeJS.LTS
```

Si l'activation de l'environnement virtuel est bloquée:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS

Installer Homebrew (si nécessaire), puis les outils:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew update
brew install git python node
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nodejs npm
```

### 4) Installation et lancement du backend (FastAPI)

#### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
cd backend/api
uvicorn main:app --reload --port 8000
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd backend/api
uvicorn main:app --reload --port 8000
```

Test rapide API:

```bash
curl http://localhost:8000/health
```

Réponse attendue:

```json
{"status":"ok"}
```

### 5) Installation et lancement du frontend (React + Vite)

Ouvrez un **deuxième terminal** à la racine du projet:

```bash
cd web
npm install
npm run dev
```

Puis ouvrez:

```text
http://localhost:5173
```

### 6) Configuration API côté web (si vous n'utilisez pas le proxy Vite)

Par défaut, Vite proxy `/api` vers `http://localhost:8000` (déjà configuré dans `web/vite.config.js`).

Si vous voulez appeler l'API directement sans proxy, créez `web/.env` avec:

```env
VITE_API_BASE=http://localhost:8000/api
```

### 7) Build de production (frontend)

```bash
cd web
npm run build
npm run preview
```

### 8) Problèmes courants

- `node` ou `npm` introuvable: installez Node.js LTS puis redémarrez le terminal.
- `python` introuvable: installez Python puis redémarrez le terminal.
- Port `5173` occupé:
```bash
cd web
npm run dev -- --port 5174
```
- Port `8000` occupé:
```bash
cd backend/api
uvicorn main:app --reload --port 8001
```
