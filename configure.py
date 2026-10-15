import base64
import json
import os
from pathlib import Path

app_id = "ua.swiryyyyx.client"
missing = [key for key in ("TELEGRAM_API_ID", "TELEGRAM_API_HASH", "GOOGLE_SERVICES_JSON") if not os.environ.get(key)]
if missing:
    raise SystemExit("Missing repository Actions secrets: " + ", ".join(missing))
api_id = os.environ["TELEGRAM_API_ID"]
api_hash = os.environ["TELEGRAM_API_HASH"]
if not api_id.isdigit() or len(api_hash) != 32 or any(c not in "0123456789abcdef" for c in api_hash.lower()):
    raise SystemExit("Telegram API credentials have an invalid format")
firebase = json.loads(os.environ["GOOGLE_SERVICES_JSON"])
clients = firebase.get("client", [])
if not any(c.get("client_info", {}).get("android_client_info", {}).get("package_name") == app_id for c in clients):
    raise SystemExit("Firebase Android package must be ua.swiryyyyx.client")
root = Path("source")
(root / "app/google-services.json").write_text(json.dumps(firebase), encoding="utf-8")
sdk = os.environ["ANDROID_HOME"]
if any(c.isspace() for c in sdk):
    raise SystemExit("Android SDK path must not contain spaces")
(root / "local.properties").write_text(
    f"sdk.dir={sdk}\napp.id={app_id}\napp.name=swiryyyyX\n"
    "app.disable_signing=true\napp.download_url=https://telegram.org/dlx\n"
    f"app.sources_url=https://github.com/{os.environ['GITHUB_REPOSITORY']}\n"
    f"telegram.api_id={api_id}\ntelegram.api_hash={api_hash}\ntgx.extension=none\n",
    encoding="utf-8",
)
keystore = os.environ.get("ANDROID_DEBUG_KEYSTORE_BASE64")
if keystore:
    target = Path.home() / ".android/debug.keystore"
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(base64.b64decode(keystore, validate=True))
print("Validated personal client configuration; credentials are not printed")
