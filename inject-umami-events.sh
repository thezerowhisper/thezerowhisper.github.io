#!/bin/bash

SCRIPT_TAG='<script defer src="/assets/umami-events.js"></script>'

find . -type f -name "*.html" ! -path "*/.git/*" | while read -r file; do

  # Skip if already present
  if grep -q 'assets/umami-events.js' "$file"; then
    echo "✔ Skipped: $file"
    continue
  fi

  # Only proceed if shared.css exists
  if grep -q '<link rel="stylesheet" href="/assets/shared.css"/>' "$file"; then

    # Insert immediately after shared.css
    sed -i '/<link rel="stylesheet" href="\/assets\/shared.css"\/>/a '"$SCRIPT_TAG" "$file"

    echo "➕ Added umami-events.js: $file"
  else
    echo "⚠ No shared.css: $file"
  fi

done
