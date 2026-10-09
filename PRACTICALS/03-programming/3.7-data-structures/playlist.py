# ============================================
# Playlist Manager — demonstrates lists & queues
# ============================================

from collections import deque

# ---- The playlist (list) ----
playlist = ["Song A", "Song B", "Song C"]

# ---- The play queue ----
queue = deque()

print("🎵 PLAYLIST MANAGER")
print("=" * 40)

def show_playlist():
    print("\n📀 Current Playlist:")
    for i, song in enumerate(playlist, 1):
        print(f"  {i}. {song}")

def show_queue():
    if not queue:
        print("\n📭 Queue is empty.")
    else:
        print(f"\n🎫 Queue ({len(queue)} songs):")
        for i, song in enumerate(queue, 1):
            print(f"  {i}. {song}")

# ---- Main menu ----
while True:
    print("\n" + "=" * 40)
    print("1. Show playlist")
    print("2. Add song to playlist")
    print("3. Queue a song to play next")
    print("4. Play next song from queue")
    print("5. Exit")
    print("=" * 40)

    choice = input("\nChoose (1-5): ").strip()

    if choice == "1":
        show_playlist()

    elif choice == "2":
        song = input("Song name: ").strip()
        playlist.append(song)
        print(f"✅ Added '{song}' to playlist.")

    elif choice == "3":
        show_playlist()
        try:
            num = int(input("Song number to queue: "))
            song = playlist[num - 1]
            queue.append(song)
            print(f"✅ Queued: {song}")
        except (ValueError, IndexError):
            print("❌ Invalid song number.")

    elif choice == "4":
        if not queue:
            print("📭 Queue is empty. Queue a song first.")
        else:
            song = queue.popleft()
            print(f"🎶 Now playing: {song}")

    elif choice == "5":
        print("\n👋 Goodbye!")
        break

    else:
        print("❌ Invalid choice.")

    show_queue()
