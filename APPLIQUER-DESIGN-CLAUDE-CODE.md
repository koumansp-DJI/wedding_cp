# Appliquer / mettre à jour le design « faire-part gravé » (pour Claude Code)

Le design est **entièrement contenu dans `index.html`** (HTML + CSS + JS + Google Fonts).
Rien à changer dans `generate.py`, le `manifest.json` ou l'hébergement. Appliquer le
design = **remplacer `index.html`** par la version fournie, puis reporter tes réglages.

---

## ▶️ PROMPT À COLLER dans Claude Code

Adopte le design « faire-part gravé » pour mon site de galerie de mariage. Le fichier index.html fourni dans ce dossier EST la version cible (couverture encadrée, monogramme, coins gravés, albums filtrables, visionneuse, téléchargements). Fais ceci, en français, et montre-moi un résumé avant de committer :

1. Sauvegarde : copie mon index.html actuel en index.backup.html.
2. Mets la version fournie en place comme nouvel index.html (elle garde toutes les fonctionnalités : accueil, albums, lightbox, téléchargements photos + vidéos, aperçu de démo).
3. Reporte MES personnalisations dans le bloc CONFIG (bas du fichier) : prénoms « Philippe & Chamila », texte d'accueil (welcome), sous-titre de couverture (coverSub), pied de page (thanks), et l'ordre/les libellés des albums (CONFIG.albums) si je les avais personnalisés.
4. Gravures des lieux : vérifie que assets/venue-1.png (haut-gauche) et assets/venue-2.png (bas-droit) existent ; sinon un ornement gravé par défaut s'affiche. Si mes images sont ailleurs, déplace-les vers ces deux noms dans assets/.
5. Ne touche PAS à generate.py ni au manifest.json.
6. Lance python -m http.server 8000 et vérifie sur http://localhost:8000 : l'écran d'accueil (médaillon P&C + coins gravés + bouton « Ouvrir »), les onglets Photos/Vidéos, les filtres d'albums, la visionneuse, et le respect de prefers-reduced-motion. Corrige tout souci.

Travaille en français.

---

## Ce qui caractérise le design
- **Typo** : Fraunces (prénoms) + Cormorant Garamond (libellés/chips/textes) + Jost (interface) + Pinyon Script (fioritures).
- **Couverture** : cadre de faire-part + fleurons de coin, médaillon P&C, coins gravés botaniques (parallaxe), sous-titre manuscrit, reflet sur « Ouvrir ».
- **Galerie** : chips d'albums en Cormorant, marque ornementale devant les titres, liseré intérieur au survol des vignettes, fleurons, apparitions avec rebond.
- **Palette** : blanc, lilas, bleu pâle (inchangée). **Accessibilité/motion** : contrastes conservés, focus visibles, `prefers-reduced-motion` respecté.

## À préserver
- Le bloc **CONFIG** (prénoms, textes, albums).
- Le dossier **`assets/`** (gravures des lieux).
- **`thumbs/`**, **`manifest.json`** générés, et **`generate.py`** tel quel.
