#!/bin/bash
find locales -type f -name "*.po" | while IFS= read -r po_file; do
    mo_file="${po_file%.po}.mo"
    msgfmt -o "$mo_file" "$po_file"
done