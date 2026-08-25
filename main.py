import hashlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import threading
import time
import requests

# Konfiguracja
TARGET_URL = "https://metagarden.eu"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1541812140766404669/mUHHRYZT5xkbjlJ8VwTAho8fGz-BOGapmnbrnV-_JOVdpQVyzeKAmmv4cr7iQxEkGa2i"
CHECK_INTERVAL = 30  # w sekundach

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}


def send_discord_notification(message: str):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"Błąd Discord: {e}")


def get_page_hash(url: str):
    # Dodanie parametru czasowego wymusza pobranie świeżej wersji bez pamięci podręcznej serwera/CDN
    fresh_url = f"{url}?_nocache={int(time.time() * 1000)}"
    res = requests.get(fresh_url, headers=HEADERS, timeout=15)
    res.raise_for_status()
    return hashlib.sha256(res.text.encode("utf-8")).hexdigest()


def monitor_loop():
    print(f"Monitorowanie {TARGET_URL} wystartowało...")
    send_discord_notification(f"🟢 **Bot monitorujący {TARGET_URL} wystartował!**")
    last_hash = None

    while True:
        try:
            current_hash = get_page_hash(TARGET_URL)

            if last_hash is None:
                last_hash = current_hash
                print("Zainicjalizowano pierwszy stan strony.")
            elif current_hash != last_hash:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                alert = (
                    f"🚨 **Wykryto zmianę na stronie!**\n"
                    f"**URL:** {TARGET_URL}\n"
                    f"**Czas:** `{timestamp}`"
                    f"@everyone @here @draze.kutasiarze"
                )
                print(alert)
                send_discord_notification(alert)
                last_hash = current_hash

        except Exception as e:
            print(f"Błąd podczas sprawdzania strony: {e}")

        time.sleep(CHECK_INTERVAL)


def run_dummy_server():
    # Mini-serwer HTTP wymagany przez darmowy plan Render.com
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    run_dummy_server()
