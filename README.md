<p align="center">
  <b>Language / Langue :</b>&nbsp;&nbsp;
  <a href="#english">🇬🇧 English</a>&nbsp;&nbsp;•&nbsp;&nbsp;
  <a href="#français">🇫🇷 Français</a>
</p>

---

<span id="english"></span>
# Liseuse (English)

A Python PDF reader.

- **PyMuPDF** renders each page as an image: no PDF JavaScript is executed.
- **PySide6** provides the user interface.
- A **JSON** file stores the library, the last read page, and preferences.

## Installation

Python 3.9 or newer.

```bash
pip install -r requirements.txt
```

## Launch

```bash
python run.py                  # opens the library
python run.py my_book.pdf      # opens a PDF directly
python -m liseuse              # equivalent to run.py (from this folder)
```

## Features

- Card-based library view (cover, title, progress bar), with search and sorting (recently read, title, progress).
- Add individual PDFs or entire folders, or drag and drop into the window.
- Right-click context menu on a book: open, rename, export a sanitized copy, mark as unread, remove.
- Light and dark themes.
- Fit to page, fit to width, or free zoom; two-page spread; right-to-left reading mode.
- Table of contents in a collapsible side panel.
- Automatically resumes at the last read page.
- Export a sanitized copy of the PDF (removes JavaScript, attachments, links, and automatic actions).
- Window size and position are remembered.

## Controls

### Keyboard

| Key | Action |
|---|---|
| `←` / `→`, `PgUp` / `PgDn`, `Space`, `Backspace` | Previous / next page (`←` and `→` are swapped in right-to-left mode) |
| `Home` / `End` | First / last page |
| `Ctrl` + `+` / `-` | Zoom in / out |
| `F` / `W` | Fit to page / fit to width |
| `D` | Two-page view |
| `T` | Toggle table of contents |
| `N` | Toggle theme |
| `F11` | Fullscreen |
| `Ctrl` + `E` | Export sanitized copy |
| `Ctrl` + `,` | Settings |
| `Esc` | Back to library (or exit fullscreen) |

### Mouse

- **Click on page edges**: previous / next page (adjustable area).
- **Click in center**: toggle toolbar visibility.
- **Scroll wheel**: change page, or scroll if zoomed in.
- **Ctrl + scroll wheel**: zoom.
- **Drag**: pan across the page when zoomed in.

## Settings

Accessible via `Ctrl+,` or the ⚙ button, with immediate effect:

- **Appearance**: theme, UI font size, page drop shadow.
- **Reading**: fit mode, two-page view, right-to-left, zoom step, hide toolbars on open.
- **Navigation**: edge clicks, click zone width, scroll wheel behavior.
- **General**: reopen last book on launch, clear cover cache.

## Data Storage

Everything is stored in `/liseuse/saved_data`:

- `data.json`: preferences, library, reading progress.
- `covers/`: cached cover thumbnails (safe to delete).

## Project Structure

```text
liseuse_app/
├── run.py                  # launcher
└── liseuse/
    ├── app.py              # wires up Storage → Settings → Library → MainWindow
    ├── config.py           # paths, constants, defaults
    ├── core/               # logic, no Qt widgets
    │   ├── storage.py      # atomic JSON, debounced saving
    │   ├── settings.py     # preferences + changed(key, value) signal
    │   ├── library.py      # books, progress, sorting, filtering
    │   ├── pdf_tools.py    # covers, sanitized copy, page count
    │   └── reader_state.py # current page, two-page mode, TOC, scale calculation
    └── ui/
        ├── main_window.py  # coordinates pages, toolbars, shortcuts, fullscreen
        ├── library_page.py # library view + card rendering
        ├── reader_page.py  # reading viewport, zoom, navigation bar
        ├── toc_dock.py     # table of contents panel
        ├── settings_dialog.py
        ├── page_widgets.py # PageView, PageScroll
        ├── rendering.py    # PyMuPDF → QPixmap (pages, shadow)
        └── theme.py        # themes and stylesheet
```

<br>

<p align="right"><a href="#english">⬆ Back to English</a> • <a href="#français">⬇ Aller au Français</a></p>

---

<span id="français"></span>
# Liseuse (Français)

Liseuse PDF en Python.

- **PyMuPDF** rend chaque page en image : aucun JavaScript du PDF n'est exécuté.
- **PySide6** fournit l'interface.
- Un fichier **JSON** garde la bibliothèque, la dernière page lue et les préférences.

## Installation

Python 3.9 ou plus récent.

```bash
pip install -r requirements.txt
```

## Lancement

```bash
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

```text
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

<br>

<p align="right"><a href="#english">⬆ Aller à la version anglaise</a> • <a href="#français">⬆ Retour en haut de la version française</a></p>
