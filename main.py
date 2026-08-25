import hashlib
import time
import requests

TARGET_URL = "https://metagraden.eu"
DISCORD_WEBHOOK_URL = "TUTAJ_WKLEJ_SWOJ_WEBHOOK_DISCORD"
CHECK_INTERVAL = 30  # co 30 sekund

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def send_discord_notification(message: str):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"Błąd Discord: {e}")


def get_page_hash(url: str):
    res = requests.get(url, headers=HEADERS, timeout=15)
    res.raise_for_status()
    return hashlib.sha256(res.text.encode("utf-8")).hexdigest()


def main():
    print(f"Monitorowanie {TARGET_URL} wystartowało...")
    send_discord_notification(f"🟢 **Bot monitorujący {TARGET_URL} wystartował!**")
    last_hash = None

    while True:
        try:
            current_hash = get_page_hash(TARGET_URL)

            if last_hash is None:
                last_hash = current_hash
            elif current_hash != last_hash:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                alert = (
                    f"🚨 **Wykryto zmianę na stronie!**\n"
                    f"**URL:** {TARGET_URL}\n"
                    f"**Czas:** `{timestamp}`"
                )
                print(alert)
                send_discord_notification(alert)
                last_hash = current_hash

        except Exception as e:
            print(f"Błąd pobierania: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()