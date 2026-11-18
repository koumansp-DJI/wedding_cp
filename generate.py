#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — Prépare la galerie de mariage.

Lit tous tes fichiers dans `originals/` et produit :
  - thumbs/       : petites miniatures (restent dans le site, chargement rapide)
  - web/          : versions "pleine résolution" optimisées, À ENVOYER sur Cloudflare R2
  - manifest.json : la liste que le site lit pour afficher photos et vidéos

ALBUMS : chaque SOUS-DOSSIER de `originals/` devient un album (une fête).
         Fichiers posés directement dans `originals/` = sans album.

Pourquoi un dossier `web/` séparé ? Redimensionner les photos (côté le plus long
≈ 3000 px) réduit énormément le poids sans différence visible — c'est ce qui
permet de tenir dans les 10 Go GRATUITS de R2.

Utilisation :
    python generate.py
    python generate.py --compress-videos     # ré-encode les vidéos en 1080p (bien plus léger)
    python generate.py --web-max 2560         # change la taille max des photos web

Dépendances :
    pip install pillow pillow-heif
    + ffmpeg installé (vignettes/durées de vidéos et --compress-videos)
"""

import os, sys, json, argparse, subprocess, shutil

try:  # console Windows : évite les plantages sur les emoji / accents
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# =========================================================================
#  ⚙️  À CONFIGURER : l'adresse publique de ton bucket R2
#  (ex. https://pub-xxxxxxxx.r2.dev/ ). Garde la barre oblique finale « / ».
# =========================================================================
R2_PUBLIC_BASE = "https://REMPLACER-PAR-TON-URL-R2.r2.dev/"

ORIGINALS_DIR = "originals"
# Dossiers d'albums posés directement à la racine du projet (un dossier = une fête).
# Ex. mariage_arlon_septembre_2024/, mariage_sri_lanka_aout_2025/ …
ROOT_ALBUM_PREFIX = "mariage_"
THUMBS_DIR    = "thumbs"
WEB_DIR       = "web"
MANIFEST      = "manifest.json"

THUMB_MAX = 1000    # côté le plus long des miniatures (px)
WEB_MAX   = 3000    # côté le plus long des photos web (px)
THUMB_Q   = 82      # qualité JPEG des miniatures
WEB_Q     = 88      # qualité JPEG des photos web

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("❌ Pillow manquant.  Installe-le :  pip install pillow pillow-heif")

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_OK = True
except Exception:
    HEIC_OK = False


def have(cmd):
    return shutil.which(cmd) is not None

FFMPEG_OK  = have("ffmpeg")
FFPROBE_OK = have("ffprobe")


def human(n):
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} To"


def slugify(name):
    keep = "-_."
    s = "".join(c if (c.isalnum() or c in keep) else "-" for c in name)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-").lower()


def dir_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def natural_key(s):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def r2_ready():
    return "REMPLACER" not in R2_PUBLIC_BASE


def url_path(p):
    """Chemin local -> URL relative (espaces, accents, emoji encodés)."""
    from urllib.parse import quote
    return quote(p.replace(os.sep, "/"), safe="/")


def shot_date(im):
    """Date de prise de vue EXIF -> « 2025-05-09T18:55:18.12 » (ou None)."""
    try:
        ex = im.getexif()
        sub = ex.get_ifd(0x8769)
        dt = sub.get(0x9003) or sub.get(0x9004) or ex.get(0x0132)   # DateTimeOriginal / Digitized / DateTime
        if not dt:
            return None
        dt = str(dt).strip().replace(":", "-", 2).replace(" ", "T")
        ss = str(sub.get(0x9291) or "").strip()                     # fraction de seconde (rafales)
        return dt + ("." + ss if ss.isdigit() else "")
    except Exception:
        return None


def make_photo(src, stem, args):
    """Crée la miniature (+ la version web si R2 est configuré). Renvoie l'entrée manifest.

    Tant que R2 n'est pas configuré, la photo « pleine résolution » pointe vers le
    fichier d'origine en local : pas de copie de plusieurs Go dans web/."""
    thumb_name = stem + ".jpg"
    thumb_path = os.path.join(THUMBS_DIR, thumb_name)
    web_name = stem + ".jpg"
    web_path = os.path.join(WEB_DIR, web_name)
    need_web = r2_ready()
    try:
        im = Image.open(src)
        w, h = im.size
        taken = shot_date(im)
        if im.getexif().get(0x0112, 1) in (5, 6, 7, 8):   # photo tournée de 90°
            w, h = h, w
        have_thumb = os.path.exists(thumb_path) and not args.force
        have_web = (not need_web) or (os.path.exists(web_path) and not args.force)
        if not (have_thumb and have_web):
            if not need_web:
                im.draft("RGB", (args.thumb_max, args.thumb_max))   # décodage JPEG réduit = bien plus rapide
            im = ImageOps.exif_transpose(im)          # respecte l'orientation de l'appareil
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            if not have_web:
                web = im.copy()
                web.thumbnail((args.web_max, args.web_max), Image.LANCZOS)
                web.save(web_path, "JPEG", quality=args.web_q, optimize=True, progressive=True)
            if not have_thumb:
                th = im.copy()
                th.thumbnail((args.thumb_max, args.thumb_max), Image.LANCZOS)
                th.save(thumb_path, "JPEG", quality=args.thumb_q, optimize=True, progressive=True)
    except Exception as e:
        print(f"   ⚠️  ignorée (illisible) : {os.path.basename(src)} — {e}")
        return None

    entry = {
        "thumb": url_path(f"{THUMBS_DIR}/{thumb_name}"),
        "full":  (R2_PUBLIC_BASE + web_name) if need_web else url_path(os.path.relpath(src)),
        "name":  web_name if need_web else os.path.basename(src),
        "w": w, "h": h,
    }
    if taken:
        entry["taken"] = taken
    try:  # poids du fichier téléchargé (sert à découper les ZIP côté site)
        entry["size"] = os.path.getsize(web_path if need_web else src)
    except OSError:
        pass
    return entry


def video_duration(src):
    if not FFPROBE_OK:
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", src],
            capture_output=True, text=True, timeout=60)
        return float(out.stdout.strip())
    except Exception:
        return None


def make_video(src, stem, args):
    """Poster + durée + fichier web de la vidéo. Renvoie l'entrée manifest."""
    dur = video_duration(src)

    thumb_rel = ""
    if FFMPEG_OK:
        poster = os.path.join(THUMBS_DIR, stem + ".jpg")
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "1", "-i", src, "-frames:v", "1",
                 "-vf", f"scale='min({args.thumb_max},iw)':-2", poster],
                capture_output=True, timeout=120)
            if os.path.exists(poster):
                thumb_rel = f"{THUMBS_DIR}/{stem}.jpg"
        except Exception:
            pass

    ext = os.path.splitext(src)[1].lower()
    if args.compress_videos and FFMPEG_OK:
        web_name = stem + ".mp4"
        dst = os.path.join(WEB_DIR, web_name)
        print(f"   🎬 compression {os.path.basename(src)} … (peut être long)")
        subprocess.run(
            ["ffmpeg", "-y", "-i", src,
             "-vf", "scale='min(1920,iw)':-2",
             "-c:v", "libx264", "-crf", "23", "-preset", "medium",
             "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", dst],
            capture_output=True)
    else:
        web_name = stem + ext
        shutil.copy2(src, os.path.join(WEB_DIR, web_name))

    entry = {"thumb": thumb_rel, "full": R2_PUBLIC_BASE + web_name, "name": web_name}
    if dur:
        entry["duration"] = round(dur)
    return entry


def main():
    ap = argparse.ArgumentParser(description="Prépare la galerie de mariage.")
    ap.add_argument("--web-max", type=int, default=WEB_MAX)
    ap.add_argument("--thumb-max", type=int, default=THUMB_MAX)
    ap.add_argument("--web-q", type=int, default=WEB_Q)
    ap.add_argument("--thumb-q", type=int, default=THUMB_Q)
    ap.add_argument("--compress-videos", action="store_true",
                    help="ré-encode les vidéos en 1080p H.264 (recommandé si > quelques Go)")
    ap.add_argument("--force", action="store_true",
                    help="régénère toutes les miniatures (sinon celles déjà créées sont gardées)")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1),
                    help="nombre de photos traitées en parallèle")
    args = ap.parse_args()

    root_albums = sorted((d for d in os.listdir(".")
                          if os.path.isdir(d) and d.lower().startswith(ROOT_ALBUM_PREFIX)),
                         key=natural_key)
    if not os.path.isdir(ORIGINALS_DIR) and not root_albums:
        sys.exit(f"❌ Aucun dossier de photos : mets-les dans « {ORIGINALS_DIR}/ » "
                 f"ou dans des dossiers « {ROOT_ALBUM_PREFIX}… » à la racine.")

    os.makedirs(THUMBS_DIR, exist_ok=True)
    if r2_ready():
        os.makedirs(WEB_DIR, exist_ok=True)
    else:
        print("ℹ️  R2_PUBLIC_BASE n'est pas encore configuré (en haut de generate.py).")
        print("    Mode local : les photos pleine résolution pointent vers tes fichiers d'origine.")
        print("    Avant de publier en ligne, configure R2 et relance le script.\n")

    # Collecte récursive : chaque SOUS-DOSSIER de originals/ devient un album (une fête),
    # ainsi que chaque dossier « mariage_… » posé à la racine du projet.
    # Fichiers posés directement dans originals/ = sans album.
    items = []  # (chemin, album_slug_ou_None)
    def collect(base, fixed_album=None):
        for root, dirs, fnames in os.walk(base):
            dirs.sort(key=natural_key)
            rel = os.path.relpath(root, base)
            if fixed_album:
                album = fixed_album
            else:
                album = None if rel == "." else slugify(rel.split(os.sep)[0])
            for f in sorted(fnames, key=natural_key):
                if f.startswith("."):
                    continue
                items.append((os.path.join(root, f), album))
    if os.path.isdir(ORIGINALS_DIR):
        collect(ORIGINALS_DIR)
    for d in root_albums:
        collect(d, slugify(d))

    photos, videos = [], []
    albums_seen = []
    seen = set()
    n_ph = n_vi = 0

    # Photos traitées en parallèle (plusieurs milliers de fichiers).
    from concurrent.futures import ProcessPoolExecutor
    pool = ProcessPoolExecutor(max_workers=args.jobs)
    pending = []   # (future, album) dans l'ordre d'origine

    for src, album in items:
        if not os.path.isfile(src):
            continue
        f = os.path.basename(src)
        ext = os.path.splitext(f)[1].lower()
        if album and album not in albums_seen and ext in (PHOTO_EXT | VIDEO_EXT):
            albums_seen.append(album)

        # nom de base propre et unique (préfixé par l'album pour éviter les collisions)
        prefix = (album + "_") if album else ""
        stem = slugify(prefix + os.path.splitext(f)[0]) or "media"
        base, i = stem, 2
        while stem in seen:
            stem = f"{base}-{i}"; i += 1
        seen.add(stem)

        if ext in PHOTO_EXT:
            if ext in (".heic", ".heif") and not HEIC_OK:
                print(f"   ⚠️  HEIC non pris en charge (installe pillow-heif) : {f}")
                continue
            pending.append((pool.submit(make_photo, src, stem, args), album))
        elif ext in VIDEO_EXT:
            os.makedirs(WEB_DIR, exist_ok=True)
            print(f"   🎥 {f}" + (f"   [{album}]" if album else ""))
            e = make_video(src, stem, args)
            if e:
                if album: e["album"] = album
                videos.append(e); n_vi += 1
        else:
            print(f"   —  ignoré (type inconnu) : {f}")

    total = len(pending)
    print(f"   📷 {total} photo(s) à traiter avec {args.jobs} processus…")
    for k, (fut, album) in enumerate(pending, 1):
        e = fut.result()
        if e:
            if album: e["album"] = album
            photos.append(e); n_ph += 1
        if k % 100 == 0 or k == total:
            print(f"   … {k}/{total}", flush=True)
    pool.shutdown()

    # Ordre chronologique (date de prise de vue) à l'intérieur de chaque album ;
    # les albums gardent leur ordre, les photos sans date restent à leur place relative en fin d'album.
    album_rank = {a: i for i, a in enumerate(albums_seen)}
    photos = [p for _, p in sorted(enumerate(photos), key=lambda ip: (
        album_rank.get(ip[1].get("album"), -1),
        0 if ip[1].get("taken") else 1,
        ip[1].get("taken", ""),
        ip[0]))]

    manifest = {
        "generatedWith": "generate.py",
        "albums": albums_seen,
        "photos": photos,
        "videos": videos,
    }
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, separators=(",", ":"))

    web_sz = dir_size(WEB_DIR)
    thumb_sz = dir_size(THUMBS_DIR)

    print("\n" + "─" * 56)
    print(f"✅ Terminé : {n_ph} photo(s) et {n_vi} vidéo(s).")
    if albums_seen:
        print(f"   • Albums (fêtes) détectés : {', '.join(albums_seen)}")
    print(f"   • thumbs/  {human(thumb_sz)}  → reste dans le site (déployé avec index.html)")
    print(f"   • web/     {human(web_sz)}  → À ENVOYER sur Cloudflare R2")
    print(f"   • {MANIFEST} écrit.")
    if web_sz > 10 * 1024**3:
        print("\n   ⚠️  web/ dépasse 10 Go (limite du palier gratuit R2).")
        print("      → réduis --web-max (ex. 2560) et/ou ajoute --compress-videos.")
    if "REMPLACER" in R2_PUBLIC_BASE:
        print("\n   ❗ Configure R2_PUBLIC_BASE en haut du script, puis relance-le.")
    print("─" * 56)
    print("Étapes suivantes : voir GUIDE.md (upload R2 + déploiement).")


if __name__ == "__main__":
    main()
