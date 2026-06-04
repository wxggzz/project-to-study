#!/usr/bin/env bash
# Sync the canonical skill (root SKILL.md + references/) into the plugin copy
# at plugins/tracedocs/skills/tracedocs/. Run this after editing SKILL.md or
# references/ so the /plugin install path stays in step with the manual one.
set -euo pipefail
cd "$(dirname "$0")/.."

dest="plugins/tracedocs/skills/tracedocs"
mkdir -p "$dest"
rm -rf "$dest/references"
cp SKILL.md "$dest/SKILL.md"
cp -R references "$dest/references"
echo "Synced root skill -> $dest"
