# Brief de génération — Galerie de mariage (pour Claude Code)

> Décompresse le projet, ouvre le dossier dans VS Code, lance Claude Code **dans ce
> dossier**, et colle le bloc « PROMPT À COLLER ». Ce dossier contient une
> **implémentation de référence complète et testée** (`index.html`, `generate.py`).

---

## 📸 Où mettre tes photos et vidéos

Tout part de **`originals/`**.

**Avec albums (vos 3 fêtes)** → un **sous-dossier par fête** (le nom du dossier = le
nom de l'album) :

```
originals/
├── Cérémonie/          (photos + vidéos)
├── Vin d'honneur/      (photos + vidéos)
└── Soirée/             (photos + vidéos)
```

**Sans albums** → tous les fichiers à plat dans `originals/`. Décompresse tes .zip et
dépose les **fichiers**.

---

## ▶️ PROMPT À COLLER dans Claude Code

Tu es mon assistant pour construire et mettre en ligne un site de galerie de mariage. Le dossier courant contient une implémentation de référence complète et testée : index.html (le site), generate.py (préparation des médias), et GUIDE.md (procédure). Commence par LIRE index.html, generate.py et GUIDE.md pour comprendre le design et l'architecture avant d'agir. Respecte la spec ci-dessous.

Objectif : un site statique gratuit et public où mes invités regardent et téléchargent nos photos et vidéos. Médias sur Cloudflare R2 (10 Go gratuits, téléchargements gratuits) ; site sur Cloudflare Pages ou GitHub Pages. Prénoms : « Philippe & Chamila ». Pas de date (trois fêtes). Thème : blanc, lilas, bleu pâle (un seul thème clair). Fonctionnalités : écran d'accueil cinématique (cadre de faire-part, médaillon, coins gravés, pétales, bouton « Ouvrir »), fond aquarelle animé, albums filtrables par fête (sous-dossiers de originals/), galerie en mosaïque avec révélations au défilement, visionneuse plein écran (clavier + téléchargement), lecture et téléchargement des vidéos. Responsive, accessible, respecte prefers-reduced-motion.

Procède étape par étape. À chaque étape qui demande une info de ma part (URL du bucket R2, clés API R2, dépôt GitHub), ARRÊTE-TOI et demande-la moi. Ne mets jamais mes clés secrètes dans un fichier suivi par git. Explique chaque commande avant de la lancer et demande validation avant tout push.

1. Vérifie Python 3, puis : pip install pillow pillow-heif. Vérifie ffmpeg et rclone ; s'il en manque, donne-moi la commande d'installation et attends.
2. Vérifie que j'ai rangé mes photos/vidéos dans originals/ (un sous-dossier par fête pour les albums). Liste le contenu et estime le volume.
3. Demande-moi l'URL publique de mon bucket Cloudflare R2 et mets-la dans R2_PUBLIC_BASE en haut de generate.py.
4. Lance python generate.py --compress-videos. Vérifie le poids de web/ ; s'il dépasse ~10 Go, relance avec --web-max 2560. Montre-moi le résultat.
5. Ouvre le site en local (python -m http.server) et confirme que l'accueil, les albums, la visionneuse et les vidéos marchent.
6. Aide-moi à envoyer web/ sur R2 avec rclone (sans committer les secrets), puis rclone copy web/ r2:<bucket>/ --progress.
7. Donne-moi la règle CORS à coller sur le bucket (voir GUIDE.md).
8. Crée un .gitignore (originals/, web/, __pycache__/, *.env), initialise git, committe index.html + thumbs/ + manifest.json + generate.py + assets/ + GUIDE.md, pousse vers mon dépôt GitHub, puis guide-moi pour Cloudflare Pages (framework None, build vide, output /) ou GitHub Pages. Donne-moi le lien public.
9. Vérifie en ligne : une photo s'affiche, s'agrandit, se télécharge ; les filtres d'album marchent ; les vidéos se lisent.

Travaille en français.

---

## 🧩 Spécification (pour reconstruire ou modifier fidèlement)

### Palette (thème clair unique, peint explicitement)
- Fond `--paper #FBFAFE`, surface `#FFFFFF`, texte `--ink #2B2742`, secondaire `--muted #78748F`, filets `--line #ECE8F5`.
- Lilas `--lilac #B49AD9` / `--lilac-deep #6E58A2` (lisible). Bleu `--blue #A9C7EA` / `--blue-deep #4E6FA1`.
- Boutons `--primary #6E58A2` texte blanc. Dégradé `--grad linear-gradient(115deg,#B49AD9,#AABEE9,#A9C7EA)`.

### Typographie (Google Fonts) — registre « faire-part gravé »
- **Fraunces** (serif d'affichage : prénoms, titres en italique).
- **Cormorant Garamond** (serif classique : libellés en majuscules espacées, chips d'albums, textes).
- **Jost** (interface, boutons, compteurs).
- **Pinyon Script** (fioritures : sous-titre de couverture, « Merci » du pied de page). Usage parcimonieux.

### Habillage « faire-part gravé »
- Couverture : **cadre** à double filet + fleurons de coin, **médaillon** monogramme P&C, **coins gravés** botaniques (parallaxe douce) — remplaçables par `assets/venue-1.png` / `venue-2.png`.
- Fleurons de séparation ; marque ornementale devant les titres de section ; chips d'album en Cormorant ; léger reflet sur le CTA ; apparitions avec easing back.out. Tout neutralisé sous `prefers-reduced-motion`.

### Architecture
- **Site statique** = `index.html` + `thumbs/` + `manifest.json` + `assets/` → Cloudflare Pages ou GitHub Pages.
- **Médias pleine résolution** = `web/` → Cloudflare R2. Le site lit les URLs R2 depuis le manifest. Sans manifest (ouverture locale), un **aperçu de démonstration** s'affiche.

### Schéma du manifest
```json
{ "albums": ["ceremonie","soiree"],
  "photos": [ { "thumb":"thumbs/ceremonie_img_001.jpg", "full":"https://pub-xxxx.r2.dev/ceremonie_img_001.jpg", "name":"ceremonie_img_001.jpg", "w":3000, "h":2000, "album":"ceremonie" } ],
  "videos": [ { "thumb":"thumbs/soiree_danse.jpg", "full":"https://pub-xxxx.r2.dev/soiree_danse.mp4", "name":"soiree_danse.mp4", "duration":158, "album":"soiree" } ] }
```

### generate.py
- Parcourt `originals/` récursivement ; chaque sous-dossier = un album.
- Photos → miniature (`thumbs/`, ~1000 px) + version web (`web/`, ~3000 px, JPEG). Orientation EXIF, conversion HEIC→JPG.
- Vidéos → poster (ffmpeg) + durée ; copie dans `web/` (ou ré-encode 1080p avec `--compress-videos`).
- Options : `--web-max`, `--thumb-max`, `--web-q`, `--thumb-q`, `--compress-videos`. Objectif : `web/` < 10 Go.
