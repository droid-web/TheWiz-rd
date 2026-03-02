Dans ton repository, clique sur Add file → Upload files
Glisse-dépose ces fichiers :
main.py
system_utils.py
constants.py
build_exe.py
requirements.txt
En bas, écris un message : Initial commit - The Wizard v2.0
Clique sur Commit changes
Méthode B : Via Git en ligne de commande
# 1. Clone ton repo vide
git clone https://github.com/TON_USERNAME/TheWizard.git
cd TheWizard

# 2. Copie tes fichiers Python dans ce dossier

# 3. Ajoute les fichiers
git add .

# 4. Commit
git commit -m "Initial commit - The Wizard v2.0"

# 5. Push
git push origin main
4. Structure finale sur GitHub
TheWizard/
├── README.md          ← GitHub l'a créé
├── .gitignore         ← GitHub l'a créé
├── LICENSE            ← GitHub l'a créé
├── main.py            ← Interface Tkinter
├── system_utils.py    ← Logique système
├── constants.py       ← Configuration/couleurs
├── build_exe.py       ← Script pour créer .exe
└── requirements.txt   ← Dépendances
5. Modifier le README.md
Clique sur README.md dans ton repo
Clique sur le crayon ✏️ pour éditer
Remplace le contenu par :
# ⚡ The Wizard - Optimiseur Gamer

Un optimiseur système Windows conçu pour les gamers.

## Fonctionnalités

- 🚀 **Optimisation RAM** - Mode Safe qui protège les processus système
- 🧹 **Nettoyage fichiers temp** - Aperçu avant suppression
- 💾 **Monitoring système** - RAM, Disque, GPU en temps réel
- 📋 **Journalisation** - Toutes les actions sont loggées

## Installation

```bash
# Clone le repo
git clone https://github.com/TON_USERNAME/TheWizard.git
cd TheWizard

# Installe les dépendances
pip install -r requirements.txt

# Lance l'application
python main.py
