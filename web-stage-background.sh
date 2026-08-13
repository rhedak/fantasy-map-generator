#!/usr/bin/env bash
# Stage the site (like ./web-stage.sh) and serve it in the background, so the
# terminal stays usable.
#
#   ./web-stage-background.sh          stage + serve in background, open browser
#   ./web-stage-background.sh stop     stop the background server
#   ./web-stage-background.sh logs     follow the server log
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
stage="$root/out/web-stage"
port="${FMG_PORT:-8000}"
log="$root/out/web-stage-server.log"
pidfile="$root/out/web-stage-server.pid"

case "${1-}" in
  stop)
    if [ -f "$pidfile" ]; then
      kill "$(cat "$pidfile")" 2>/dev/null || true
      rm -f "$pidfile"
      echo "stopped"
    else
      echo "not running"
    fi
    exit 0
    ;;
  logs)
    exec tail -f "$log"
    ;;
esac

"$root/web-stage.sh"

if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
  echo "already running at http://localhost:$port (pid $(cat "$pidfile"))"
  exit 0
fi
rm -f "$pidfile"

(
    cd "$stage"
    nohup python3 -m http.server "$port" >"$log" 2>&1 &
    echo $! >"$pidfile"
)

# Wait until the server answers before reporting success.
for _ in $(seq 1 25); do
    if curl -s -o /dev/null "http://localhost:$port/"; then
        break
    fi
    sleep 0.2
done

echo "serving http://localhost:$port (pid $(cat "$pidfile"), log $log)"
if command -v open >/dev/null 2>&1; then
    open "http://localhost:$port"
fi
