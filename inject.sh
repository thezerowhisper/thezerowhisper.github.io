#!/bin/bash

CSS_TAG='<link rel="stylesheet" href="/assets/shared.css"/>'
UMAMI_TAG='<script defer src="https://cloud.umami.is/script.js" data-website-id="502152b9-58c2-49b7-901c-de2a5c06436b"></script>'

TARGET_DIR="drug-doses"

find "$TARGET_DIR" -type f -name "*.html" | while read -r file; do
  updated=false

  # Check CSS
  if ! grep -q '/assets/shared.css' "$file"; then
    sed -i "/<\/body>/i $CSS_TAG" "$file"
    updated=true
    echo "➕ CSS added: $file"
  fi

  # Check Umami
  if ! grep -q 'cloud.umami.is/script.js' "$file"; then
    sed -i "/<\/body>/i $UMAMI_TAG" "$file"
    updated=true
    echo "➕ Umami added: $file"
  fi

  # If nothing changed
  if [ "$updated" = false ]; then
    echo "✔ Skipped: $file"
  fi
done
