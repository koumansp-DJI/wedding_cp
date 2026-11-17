# Galerie de mariage — le projet

Un site élégant (façon faire-part gravé) où tes invités **regardent et téléchargent**
les photos et vidéos. 100 % gratuit, lien public, sans serveur à entretenir.

## Fichiers

```
wedding-gallery/
├── index.html                     ← le site (design "faire-part gravé", déjà prêt)
├── generate.py                    ← prépare miniatures + web/ + manifest.json
├── manifest.sample.json           ← exemple du format (référence)
├── assets/                        ← gravures des lieux (venue-1.png / venue-2.png)
├── originals/                     ← 📥 TES photos et vidéos (un sous-dossier par fête)
├── thumbs/                        ← miniatures (généré)
├── GUIDE.md                       ← marche à suivre complète (R2 + déploiement)
├── DEMARRER-DANS-VSCODE.md        ← prise en main dans VS Code
├── PROMPT-CLAUDE-CODE.md          ← brief complet pour Claude Code
└── APPLIQUER-DESIGN-CLAUDE-CODE.md← appliquer/mettre à jour le design via Claude Code
```

## En bref

1. Mets tes photos/vidéos dans `originals/` (un **sous-dossier par fête** = un album).
2. `python generate.py --compress-videos` → crée `thumbs/`, `web/`, `manifest.json`.
3. Envoie `web/` sur **Cloudflare R2** (stockage gratuit, téléchargements gratuits).
4. Déploie `index.html` + `thumbs/` + `manifest.json` sur **Cloudflare Pages** ou **GitHub Pages**.

Détails pas-à-pas dans **GUIDE.md**. Personnalisation (prénoms, etc.) dans le bloc
`CONFIG` en bas d'`index.html`.
