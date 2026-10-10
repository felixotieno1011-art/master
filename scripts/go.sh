#!/data/data/com.termux/files/usr/bin/bash
case "$1" in
  note)
    shift
    num="$1"
    # Try zero-padded first (01, 02, ..., 09)
    f=$(ls "$HOME/master/NOTES/" | grep -E "^(0${num}|${num})-" | head -n1)
    if [ -z "$f" ]; then
      echo "❌ No notes file found for Part $num"
      exit 1
    fi
    nano "$HOME/master/NOTES/$f"
    ;;
  work)
    shift
    num="$1"
    # Try zero-padded first (01, 02, ..., 09)
    d=$(ls "$HOME/master/PRACTICALS/" | grep -E "^(0${num}|${num})-" | head -n1)
    if [ -z "$d" ]; then
      echo "❌ No practicals folder found for Part $num"
      exit 1
    fi
    cd "$HOME/master/PRACTICALS/$d" && exec bash
    ;;
  toc)   nano "$HOME/master/TOC.md" ;;
  log)   nano "$HOME/master/JOURNAL.md" ;;
  res)   nano "$HOME/master/RESOURCES.md" ;;
  prog)  nano "$HOME/master/PROGRESS.md" ;;
  *)     cd "$HOME/master" && exec bash ;;
esac
