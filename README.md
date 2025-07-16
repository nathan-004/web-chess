# Echecs en ligne


![Made with Flask](https://img.shields.io/badge/Made%20with-Flask-blue)
![Frontend](https://img.shields.io/badge/Frontend-JavaScript-yellow)
![Backend](https://img.shields.io/badge/Backend-Python%20%7C%20Flask-green)
![Pytest](https://img.shields.io/badge/tests-pytest-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![GitHub last commit](https://img.shields.io/github/last-commit/nathan-004/web-chess)


## Description du projet

Ce projet est une application web de jeu d’échecs multijoueur permettant à deux joueurs de s’affronter sur un échiquier interactif. Elle gère les règles classiques du jeu, les déplacements valides, la détection d’échec, et synchronise l’état de la partie via un serveur Flask.

L’objectif de ce projet est d’explorer le développement d’interfaces interactives connectées à un backend Python, tout en respectant les règles complexes d’un jeu stratégique comme les échecs.

### Technologies utilisées

- **JavaScript** & [Chessboard.js](https://github.com/oakmac/chessboardjs) pour gérer l’échiquier visuel et les mouvements des pièces en drag-and-drop.
- **Python (Flask)** pour traiter la logique métier (validation des coups, détection d’échecs, gestion de la partie).
- **Fetch API (JS)** pour la communication client-serveur (envoie les coups à jouer, récupère la position FEN du serveur).

### Défis rencontrés

- Etablir les règles des échecs (mouvements des pièces, échecs et échecs et mat)
- Lier l'interface graphique avec le serveur Flask

### Améliorations futures

- Finir les règles des échecs (roque, prise en passant, pat)
- Permettre de stocker plusieurs parties simultanément
- Améliorer l'expérience utilisateur

---

## Installation

1. Clone le repo :
```bash
git clone https://github.com/nathan-004/web-chess.git
cd web-chess
```
2. Installe les dépendances Python :
```bash
pip install -r requirements.txt
```
3. Lance le serveur :
```bash
python run.py
```
4. Accède à l'application :
```bash
http://127.0.0.1:5000
```

## Ressources

[Chessboard.js](https://github.com/oakmac/chessboardjs) : Bibliothèque javascript permettant d'afficher des échiquiers et de bouger les pièces

## License

Voir le fichier [LICENSE](https://github.com/nathan-004/web-chess/blob/main/LICENSE)
