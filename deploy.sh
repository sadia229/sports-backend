#!/usr/bin/env bash
#
# deploy.sh — integrate Vercel CLI (env vars) + git auto-deploy in one step.
#
#   1. Ensures the Vercel CLI is installed and you're logged in.
#   2. Links this folder to the Vercel project (first run only).
#   3. Pushes every non-empty var from .env into Vercel (Production + Preview).
#   4. Triggers the normal git-push auto-deploy so the new build picks them up.
#
# Usage:
#   ./deploy.sh                 # sync env vars + push to trigger auto-deploy
#   ./deploy.sh --env-only      # only sync env vars, don't push
#   ./deploy.sh "commit message"
#
set -euo pipefail
cd "$(dirname "$0")"

ENV_FILE=".env"
TARGETS=("production" "preview")
PUSH=true
MSG="redeploy: sync env vars"

# --- args ---
for arg in "$@"; do
  case "$arg" in
    --env-only) PUSH=false ;;
    *) MSG="$arg" ;;
  esac
done

# --- 1. CLI present? ---
if ! command -v vercel >/dev/null 2>&1; then
  echo "Installing Vercel CLI..."
  npm i -g vercel
fi

# --- 2. logged in? ---
if ! vercel whoami >/dev/null 2>&1; then
  echo "Not logged in — opening Vercel login..."
  vercel login
fi

# --- 3. linked? ---
if [ ! -f ".vercel/project.json" ]; then
  echo "Linking this folder to a Vercel project..."
  vercel link
fi

# --- 4. sync .env -> Vercel ---
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found." >&2
  exit 1
fi

echo ""
echo "Syncing $ENV_FILE -> Vercel (${TARGETS[*]})..."
while IFS= read -r line || [ -n "$line" ]; do
  # skip blanks and comments
  [[ -z "${line// }" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  # split KEY=VALUE on the first '='
  key="${line%%=*}"
  value="${line#*=}"
  key="$(echo -n "$key" | xargs)"          # trim
  # skip empty values (e.g. unset SMTP_HOST=)
  [[ -z "$value" ]] && { echo "  · skip $key (empty)"; continue; }

  for target in "${TARGETS[@]}"; do
    # remove existing value (ignore if absent) then add fresh
    vercel env rm "$key" "$target" -y >/dev/null 2>&1 || true
    printf '%s' "$value" | vercel env add "$key" "$target" >/dev/null 2>&1
  done
  echo "  ✓ $key"
done < "$ENV_FILE"

echo "Env vars synced."

# --- 5. trigger auto-deploy via git push ---
if [ "$PUSH" = true ]; then
  echo ""
  echo "Triggering auto-deploy (git push origin main)..."
  git add -A
  if git diff --cached --quiet; then
    git commit --allow-empty -m "$MSG"
  else
    git commit -m "$MSG"
  fi
  git push origin main
  echo ""
  echo "Pushed. Watch the build at: https://vercel.com/dashboard"
else
  echo "Skipped git push (--env-only). Run 'git push origin main' to deploy."
fi
