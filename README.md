# Liseuse

Liseuse PDF en Python.

- **PyMuPDF** rend chaque page en image : aucun JavaScript du PDF n'est exécuté.
- **PySide6** fournit l'interface.
- Un fichier **JSON** garde la bibliothèque, la dernière page lue et les préférences.

## Installation

Python 3.9 ou plus récent.

```
pip install -r requirements.txt
```

## Lancement

```
python run.py                  # ouvre la bibliothèque
python run.py mon_livre.pdf    # ouvre directement un PDF
python -m liseuse              # équivalent de run.py (depuis ce dossier)
```

## Fonctionnalités

- Bibliothèque en cartes (couverture, titre, barre de progression), avec recherche et tri (récemment lus, titre, progression).
- Ajout de PDF ou de dossiers entiers, ou par glisser-déposer dans la fenêtre.
- Menu clic droit sur un livre : ouvrir, renommer, exporter une version nettoyée, marquer comme non lu, retirer.
- Thèmes clair et nuit.
- Ajustement à la page, à la largeur ou zoom libre ; double page ; lecture de droite à gauche.
- Sommaire du PDF dans un panneau latéral.
- Reprise automatique à la dernière page lue.
- Export d'une copie nettoyée du PDF (JavaScript, pièces jointes, liens et actions automatiques retirés).
- Position et taille de la fenêtre mémorisées.

## Commandes

### Clavier

| Touche | Action |
|---|---|
| `←` / `→`, `PgUp` / `PgDn`, `Espace`, `Retour arrière` | Page précédente / suivante (`←` et `→` s'inversent en mode droite à gauche) |
| `Début` / `Fin` | Première / dernière page |
| `Ctrl` + `+` / `-` | Zoom avant / arrière |
| `F` / `W` | Ajuster à la page / à la largeur |
| `D` | Double page |
| `T` | Afficher le sommaire |
| `N` | Changer de thème |
| `F11` | Plein écran |
| `Ctrl` + `E` | Exporter une version nettoyée |
| `Ctrl` + `,` | Paramètres |
| `Échap` | Retour à la bibliothèque (ou quitte le plein écran) |

### Souris

- **Clic sur les bords** de la page : page précédente / suivante (zone réglable).
- **Clic au centre** : masque ou affiche les barres.
- **Molette** : change de page, ou fait défiler si la page est zoomée.
- **Ctrl + molette** : zoom.
- **Glisser** : déplace la page quand elle est zoomée.

## Paramètres

Ils s'ouvrent avec `Ctrl+,` ou le bouton ⚙ et s'appliquent immédiatement :

- **Apparence** : thème, taille du texte de l'interface, ombre autour de la page.
- **Lecture** : ajustement, double page, droite à gauche, pas de zoom, masquer les barres à l'ouverture.
- **Navigation** : clic sur les bords, largeur des zones de clic, molette.
- **Général** : rouvrir le dernier livre au démarrage, vider le cache des couvertures.

## Données

Tout est stocké dans `/liseuse/saved_data` :

- `data.json` : préférences, bibliothèque, progression.
- `covers/` : miniatures des couvertures (supprimables sans risque).

## Structure du code

```
liseuse_app/
├── run.py                  # lanceur
└── liseuse/
    ├── app.py              # assemble Storage → Settings → Library → MainWindow
    ├── config.py           # chemins, constantes, valeurs par défaut
    ├── core/               # logique, sans widgets Qt
    │   ├── storage.py      # JSON atomique, sauvegarde différée
    │   ├── settings.py     # préférences + signal changed(clé, valeur)
    │   ├── library.py      # livres, progression, tri, filtre
    │   ├── pdf_tools.py    # couvertures, copie nettoyée, nombre de pages
    │   └── reader_state.py # page courante, double page, sommaire, calcul d'échelle
    └── ui/
        ├── main_window.py  # orchestre pages, barres, raccourcis, plein écran
        ├── library_page.py # page bibliothèque + dessin des cartes
        ├── reader_page.py  # zone de lecture, zoom, barre de navigation
        ├── toc_dock.py     # panneau du sommaire
        ├── settings_dialog.py
        ├── page_widgets.py # PageView, PageScroll
        ├── rendering.py    # PyMuPDF → QPixmap (pages, ombre)
        └── theme.py        # thèmes et feuille de style
```

