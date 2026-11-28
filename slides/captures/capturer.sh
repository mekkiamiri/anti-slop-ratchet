#!/usr/bin/env bash
# Rend chaque capture HTML (fond sombre) en PNG avec WebKit headless, sans fenêtre.
# Largeur 1280 px ; --full-page donne la hauteur exacte du contenu.
# Usage : slides/captures/capturer.sh   (depuis la racine du dépôt)
# Prérequis : npx, et un registre npm joignable (NPM_CONFIG_REGISTRY si le registre public est bloqué).
set -euo pipefail
cd "$(dirname "$0")"
sortie=../../docs/slides/img
mkdir -p "$sortie"
for f in [0-9][0-9]-*.html; do
  npx -y playwright@1.66.0-alpha-2026-11-09 screenshot --browser webkit --viewport-size 1280,400 \
    --full-page "file://$PWD/$f" "$sortie/${f%.html}.png"
done
