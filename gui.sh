#!/bin/bash
# Fantasy Map Generator GUI control script
# Usage: ./gui.sh [start|stop|restart|status|logs]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="/tmp/fantasy-map-gui.pid"
LOG_FILE="/tmp/fantasy-map-gui.log"
PORT=3000

function start_server() {
  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "✗ Server already running (PID: $(cat "$PID_FILE"))"
    exit 1
  fi

  echo "Starting Fantasy Map Generator GUI..."
  cd "$PROJECT_DIR"
  python -m fantasy_map_generator.gui > "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"

  # Wait for server to start
  sleep 3

  if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "✓ Server started successfully (PID: $(cat "$PID_FILE"))"
    echo "✓ Available at http://localhost:$PORT"
  else
    echo "✗ Server failed to start. Check logs:"
    cat "$LOG_FILE"
    exit 1
  fi
}

function stop_server() {
  if [ ! -f "$PID_FILE" ]; then
    echo "✗ Server not running"
    exit 1
  fi

  PID=$(cat "$PID_FILE")
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "✗ Server not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 1
  fi

  echo "Stopping server (PID: $PID)..."
  kill "$PID"

  # Wait for graceful shutdown
  for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
      rm -f "$PID_FILE"
      echo "✓ Server stopped"
      return 0
    fi
    sleep 0.5
  done

  echo "✗ Server did not stop gracefully, force killing..."
  kill -9 "$PID" || true
  rm -f "$PID_FILE"
  echo "✓ Server force stopped"
}

function restart_server() {
  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    stop_server
    sleep 1
  fi
  start_server
}

function server_status() {
  if [ ! -f "$PID_FILE" ]; then
    echo "✗ Server not running"
    exit 1
  fi

  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "✓ Server running (PID: $PID)"
    echo "  URL: http://localhost:$PORT"
    echo "  Log: $LOG_FILE"
  else
    echo "✗ Server not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 1
  fi
}

function show_logs() {
  if [ -f "$LOG_FILE" ]; then
    tail -f "$LOG_FILE"
  else
    echo "✗ Log file not found: $LOG_FILE"
    exit 1
  fi
}

case "${1:-status}" in
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  restart)
    restart_server
    ;;
  status)
    server_status
    ;;
  logs)
    show_logs
    ;;
  *)
    echo "Fantasy Map Generator GUI Control"
    echo ""
    echo "Usage: $0 [start|stop|restart|status|logs]"
    echo ""
    echo "Commands:"
    echo "  start   - Start the GUI server"
    echo "  stop    - Stop the GUI server"
    echo "  restart - Restart the GUI server"
    echo "  status  - Show server status"
    echo "  logs    - Follow server logs"
    exit 1
    ;;
esac
