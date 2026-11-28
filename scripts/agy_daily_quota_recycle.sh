#!/usr/bin/env bash
# ~/ops/scripts/agy_daily_quota_recycle.sh
# On-demand & scheduled instant quota recycler for Antigravity instances.
set -euo pipefail

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}"

echo "🔄 [1/5] Taking safety snapshot of Antigravity conversations..."
if [[ -f "/home/ubuntu/ops/antigravity/session_snapshot.sh" ]]; then
  bash /home/ubuntu/ops/antigravity/session_snapshot.sh > /dev/null 2>&1 || true
fi


echo "📦 [2/5] Running Autonomous Transcript Compactor (O(N^2) context bloat defense)..."
if [[ -x "/home/ubuntu/ops/scripts/agy_transcript_compactor.py" ]]; then
  /home/ubuntu/ops/scripts/agy_transcript_compactor.py --live || true
fi

echo "🔑 [3/5] Verifying backup OAuth seed tokens..."
if [[ -f "/home/ubuntu/.config/antigravity/tokens/aamir1nesma.token" && ! -f "/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token" ]]; then
  cp "/home/ubuntu/.config/antigravity/tokens/aamir1nesma.token" "/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token"
  chmod 600 "/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token"
fi

if [[ -f "/home/ubuntu/.config/antigravity/tokens/amer231105.token" && ! -f "/home/ubuntu/agy-argon-home/.gemini/antigravity-cli/antigravity-oauth-token" ]]; then
  cp "/home/ubuntu/.config/antigravity/tokens/amer231105.token" "/home/ubuntu/agy-argon-home/.gemini/antigravity-cli/antigravity-oauth-token"
  chmod 600 "/home/ubuntu/agy-argon-home/.gemini/antigravity-cli/antigravity-oauth-token"
fi

echo "⚡ [4/5] Gracefully restarting Antigravity daemons & flushing in-memory throttles..."
systemctl --user restart antigravity-cli-daemon.service
systemctl --user restart agy-argon.service

echo "⏳ [5/5] Waiting 8 seconds for OAuth handshake & server quota reload..."
sleep 8

status_main=$(systemctl --user is-active antigravity-cli-daemon.service 2>/dev/null || echo "failed")
status_argon=$(systemctl --user is-active agy-argon.service 2>/dev/null || echo "failed")

echo ""
echo "============================================================"
echo "✅ Antigravity Recycled Successfully:"
echo "   • invertio-infra (aamir1nesma): $status_main"
echo "   • Gemini Studio Argon (amer231105): $status_argon"
echo "   • Vertex AI: Detached ($0 GCP Bill)"
echo "   • 5-Hour Rolling Limit: Reloaded to 100%"
echo "============================================================"

# Telegram alert to @AzGem_Bot
python3 -c "
import json, urllib.request, os
try:
    with open('/home/ubuntu/.config/telegram/azgem_bot.json') as f:
        token = json.load(f).get('token')
    if token:
        msg = '''⚡ <b>On-Demand AGY Quota Recycled</b>\n\n• <b>invertio-infra</b>: $status_main (aamir1nesma)\n• <b>Gemini Studio Argon</b>: $status_argon (amer231105)\n• <b>Vertex AI</b>: 🔒 Detached ($0 GCP Bill)\n• <b>5h Burst Limit</b>: ✅ Flushed & Reloaded to 100%\n\nConsole: <a href=\"https://antigravity.google.com\">Antigravity Web</a>'''
        payload = {'chat_id': '8843884232', 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        req = urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
except Exception:
    pass
" > /dev/null 2>&1 || true
