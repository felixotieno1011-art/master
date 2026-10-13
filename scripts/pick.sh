#!/data/data/com.termux/files/usr/bin/bash
# pick.sh — shows random UNTICKED topics so YOU can choose one

TOC="$HOME/master/TOC.md"
N="${1:-3}"   # default: show 3 options

unticked=$(grep -e "^- \[ \] [0-9]" "$TOC")

if [ -z "$unticked" ]; then
  echo "🎉 Nothing left unticked — you finished everything!"
  exit 0
fi

count=$(echo "$unticked" | wc -l)

echo ""
echo "🎲 TOPIC SUGGESTIONS — you choose"
echo "────────────────────────────────"
echo "  $count unticked topics available"
echo ""
echo "  Here are $N random options:"
echo ""

echo "$unticked" | shuf -n "$N" | nl -w2 -s'. '

echo ""
echo "  👉 Now YOU pick one. Say the number or name it yourself."
echo ""
