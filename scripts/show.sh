#!/data/data/com.termux/files/usr/bin/bash
# show.sh — pretty progress + recent ticks

MASTER="$HOME/master"
TOC="$MASTER/TOC.md"

total=$(grep -c -e "^- \[.\] [0-9]" "$TOC")
done_count=$(grep -c -e "^- \[x\] [0-9]" "$TOC")
percent=0
[ "$total" -gt 0 ] && percent=$(( done_count * 100 / total ))

bar_len=30
filled=$(( percent * bar_len / 100 ))
bar=""
for i in $(seq 1 $bar_len); do
  if [ $i -le $filled ]; then bar="${bar}█"; else bar="${bar}░"; fi
done

echo ""
echo "🎓 MASTER — Learning Progress"
echo "────────────────────────────────"
echo "  [$bar] $percent%"
echo "  Done: $done_count / $total  |  Left: $((total - done_count))"
echo "────────────────────────────────"
echo ""
echo "Recent completed:"
grep -e "^- \[x\] [0-9]" "$TOC" | tail -n 5
echo ""
echo "Next up:"
grep -e "^- \[ \] [0-9]" "$TOC" | head -n 3
echo ""



