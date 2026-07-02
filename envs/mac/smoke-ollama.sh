#!/usr/bin/env bash
set -euo pipefail

MODEL_VALUE="${MODEL:-gemma4:e4b}"
BASE_URL_VALUE="${BASE_URL:-http://127.0.0.1:11434/v1}"
CHAT_URL="${BASE_URL_VALUE%/}/chat/completions"

python3 - "${CHAT_URL}" "${MODEL_VALUE}" <<'PY'
import json
import sys
import urllib.request

chat_url = sys.argv[1]
model = sys.argv[2]
payload = {
    "model": model,
    "messages": [{"role": "user", "content": "Reply with OK."}],
    "max_tokens": 8,
    "stream": False,
}
request = urllib.request.Request(
    chat_url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
    data = json.loads(response.read().decode("utf-8"))

print(json.dumps({"model": model, "chat_url": chat_url, "response": data}, ensure_ascii=False))
PY
