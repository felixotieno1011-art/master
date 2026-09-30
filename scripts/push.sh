#!/data/data/com.termux/files/usr/bin/bash
# push.sh — commit (if needed) and always push to origin main

cd ~/master || { echo "❌ ~/master not found"; exit 1; }

if [ ! -d .git ]; then
  echo "❌ Not a git repo. Run: cd ~/master && git init"
  exit 1
fi

msg="${1:-update: $(date +%Y-%m-%d\ %H:%M)}"

git add .

if git diff --cached --quiet; then
  echo "ℹ️  Nothing new to commit — pushing anyway…"
else
  git commit -m "$msg"
fi

echo "🚀 Pushing to GitHub…"
git push origin main
echo "✅ Done."
