run_app() {
  if [ "$AUTO_UPDATE" = "True" ]; then
    echo "Auto update enabled"
    sh /usr/local/bin/auto-update.sh;
  else
    echo "Auto update disabled (AUTO_UPDATE not True)";
  fi

  if [ -d "/overrides" ]; then
    cp -r /overrides/* /app;
  fi

  gunicorn --bind 0.0.0.0:5000 app:app &
  PID=$!
  wait $PID
}

trap 'kill -TERM $PID && wait $PID && echo "SIGTERM received, exiting." && run_app' TERM HUP INT
run_app
