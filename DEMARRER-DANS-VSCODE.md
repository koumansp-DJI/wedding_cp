# Démarrer dans Visual Studio Code — pas à pas

Tout se fait depuis VS Code : ouvrir le projet, le prévisualiser, générer les médias,
versionner avec Git, et (option) lancer Claude Code dans le terminal intégré.

## 1. Ouvrir le projet
Décompresse le projet, puis VS Code → **Fichier → Ouvrir le dossier…** → `wedding-gallery`.
Accepte « Oui, je fais confiance aux auteurs ».

## 2. Installer 3 extensions (`Ctrl+Shift+X`)
- **Python** (Microsoft) — exécuter `generate.py`.
- **Live Server** (Ritwick Dey) — prévisualiser le site.
- **Claude Code** (Anthropic) — facultatif, pour piloter par l'IA.

## 3. Terminal intégré
**Terminal → Nouveau terminal**. C'est ici que tu tapes les commandes.

## 4. Voir le site tout de suite (aperçu démo)
Clic droit sur `index.html` → **« Open with Live Server »** (ou bouton **« Go Live »**).
⚠️ Toujours via Live Server, jamais par double-clic : en `file://`, le navigateur
bloque `manifest.json` et tu restes en mode démo.

## 5. Personnaliser les prénoms
`index.html`, bloc **`CONFIG`** (en bas), déjà réglé sur **Philippe & Chamila**.
`Ctrl+S` → Live Server recharge.

## 6. Déposer tes photos
Glisse-dépose tes fichiers dans `originals/` (un sous-dossier par fête pour les albums).

## 7. Générer (terminal)
```bash
pip install pillow pillow-heif
python generate.py --compress-videos
```
Recharge l'aperçu : tes vraies photos remplacent la démo.

## 8. Versionner avec Git (panneau `Ctrl+Shift+G`)
« Initialiser le dépôt » → crée un `.gitignore` (`originals/`, `web/`, `__pycache__/`,
`*.env`) → message + **✓ Valider** → **« Publier la branche »** vers GitHub.

## 9. Publier le site
Cloudflare Pages (connecter le dépôt, build vide, output `/`) ou GitHub Pages.
→ ton lien public.

## 10. (Option) Laisser Claude Code piloter
Dans le terminal : `claude`, puis colle le contenu de **PROMPT-CLAUDE-CODE.md**.

**Résumé :** Ouvrir le dossier → Live Server → déposer les médias → `python generate.py`
→ Git → Cloudflare Pages. 🥂
