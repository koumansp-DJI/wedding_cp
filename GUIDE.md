# Galerie de mariage — Marche à suivre

Un site élégant où tes invités **regardent et téléchargent** les photos et vidéos.
100 % gratuit, lien public, sans base de données ni serveur à entretenir.

> **Temps estimé :** ~30 à 45 minutes la première fois. Ensuite, ajouter des
> photos ne prend que quelques minutes.

---

## 1. Comment ça marche

Le défi d'une galerie de mariage, ce n'est pas la page — c'est **où loger les Go de
médias** et laisser les gens les télécharger sans facture. La solution :

```
   Tes fichiers (originals/<fête>/)
            │  python generate.py
   ┌────────┴─────────┬───────────────────────────┐
   │  thumbs/         │  web/                      │  manifest.json
   │  (mini-aperçus)  │  (photos/vidéos optimisées)│  (la liste + albums)
   └────────┬─────────┴──────────────┬─────────────┘
            │                        │
   Hébergement du SITE          Stockage des MÉDIAS
   (Cloudflare Pages ou         (Cloudflare R2 : 10 Go
    GitHub Pages — gratuit)      gratuits, 0 € de téléchargement)
            │
     https://…  ← le lien public à envoyer aux invités
```

Le point clé : **Cloudflare R2 ne facture jamais le téléchargement.** Peu importe
combien d'invités téléchargent : c'est gratuit. La seule limite du palier gratuit,
c'est **10 Go de stockage** — d'où la compression (indolore) pour y tenir.

---

## 2. Ce qu'il te faut (tout est gratuit)

**Comptes :** un compte **Cloudflare** (R2 + Pages) et ton compte **GitHub**.

**Outils :**
```bash
pip install pillow pillow-heif          # traitement photos (+ HEIC iPhone)
# ffmpeg :  macOS → brew install ffmpeg | Windows → winget install Gyan.FFmpeg | Linux → sudo apt install ffmpeg
# rclone :  https://rclone.org/downloads/  (envoi en masse vers R2)
```

---

## 3. Étape par étape

### Étape 1 — Déposer tes médias

Copie tes photos/vidéos dans `originals/`. Tous formats (JPG, PNG, HEIC, MP4, MOV…).

**Pour les albums (vos 3 fêtes) :** crée un **sous-dossier par fête** — le **nom du
dossier devient le nom de l'album** :

```
originals/
├── Cérémonie/      (photos + vidéos)
├── Vin d'honneur/  (photos + vidéos)
└── Soirée/         (photos + vidéos)
```

Sans sous-dossiers (tout à plat), il n'y a simplement pas de filtres d'album.
Décompresse tes .zip et dépose les **fichiers** (les .zip sont ignorés).

### Étape 2 — Créer le stockage Cloudflare R2

1. **dash.cloudflare.com** → **R2** → *Create bucket* (ex. `mariage-photos`).
2. Ouvre le bucket → **Settings** → **Public access / Public Development URL** →
   **Enable**. Tu obtiens `https://pub-xxxxxxxx.r2.dev`.
3. Colle-la en haut de `generate.py` (garde la `/` finale) :
   ```python
   R2_PUBLIC_BASE = "https://pub-xxxxxxxx.r2.dev/"
   ```

### Étape 3 — Générer la galerie

```bash
python generate.py                 # ou : python generate.py --compress-videos
```

Vérifie le **poids de `web/`** affiché. Objectif : **< 10 Go**. Si ça dépasse :
```bash
python generate.py --compress-videos --web-max 2560
```

### Étape 4 — Envoyer les médias vers R2 (rclone)

Crée une clé : Cloudflare → **R2** → **Manage R2 API Tokens** → *Create* →
**Object Read & Write** → tu obtiens Access Key ID, Secret Access Key et un endpoint.

Configure rclone (`rclone config file` t'indique où est `rclone.conf`) :
```ini
[r2]
type = s3
provider = Cloudflare
access_key_id = TON_ACCESS_KEY_ID
secret_access_key = TON_SECRET_ACCESS_KEY
endpoint = https://TON_ACCOUNT_ID.r2.cloudflarestorage.com
acl = private
```

Puis :
```bash
rclone copy web/ r2:mariage-photos/ --progress
```

### Étape 5 — Autoriser les téléchargements (CORS)

Bucket R2 → **Settings** → **CORS Policy** → *Edit* → colle :
```json
[
  { "AllowedOrigins": ["*"], "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"], "ExposeHeaders": ["Content-Length", "Content-Disposition"],
    "MaxAgeSeconds": 3600 }
]
```
Sans cette règle, le téléchargement bascule sur un repli (ouverture du fichier).

### Étape 6 — Personnaliser

Ouvre `index.html`, bloc **`CONFIG`** (en bas) : prénoms, accueil, et libellés
d'albums (`CONFIG.albums`, ex. `[{id:"ceremonie", label:"Cérémonie"}, …]`).

### Étape 7 — Publier le site

Le site = `index.html` + `thumbs/` + `manifest.json` (+ `assets/`).

**Cloudflare Pages (recommandé)** : pousse le dossier sur GitHub, puis Cloudflare →
*Workers & Pages* → *Create* → *Pages* → *Connect to Git* → framework **None**,
build **vide**, output **`/`**. Tu obtiens `https://…pages.dev`.

**GitHub Pages** : dépôt → *Settings* → *Pages* → branche `main`, dossier `/`.

---

## 4. Ajouter des photos plus tard

`originals/` ← nouveaux fichiers · `python generate.py` · `rclone copy web/ r2:mariage-photos/`
· `git add -A && git commit && git push` → le site se met à jour tout seul.

## 5. Rester 100 % gratuit

| Ressource | Palier gratuit | En pratique |
|---|---|---|
| **R2 — stockage** | **10 Go** | La seule vraie limite. Compression → tu y tiens. |
| **R2 — téléchargements** | **illimité, 0 €** | Aucun frais de bande passante. |
| **Cloudflare Pages** | illimité | Largement suffisant. |
| **GitHub Pages** | site ≤ 1 Go, ~100 Go/mois | OK pour le site + `thumbs/`. |

Au-delà de 10 Go sur R2 : ~0,015 $/Go/mois (dérisoire). Alternative : Backblaze B2.

## 6. Dépannage

- **Grandes images absentes** → `R2_PUBLIC_BASE` mal réglé, ou `web/` pas encore envoyé.
- **Le téléchargement ouvre au lieu d'enregistrer** → règle CORS manquante (Étape 5).
- **Photos iPhone (HEIC) ignorées** → `pip install pillow-heif`, puis relance.
- **Vidéos trop lourdes** → `python generate.py --compress-videos`.
- **Tester en local** → `python -m http.server 8000` puis http://localhost:8000
  (le double-clic direct passe en mode démo).

Félicitations, et bonne mise en ligne ! 🥂
