if [ "$AUTO_UPDATE" = "True" ]; then
  echo "Auto update enabled"
  sh /usr/local/bin/auto-update.sh;
else
  echo "Auto update disabled (AUTO_UPDATE not True)";
fi

if [ -d "/overrides" ]; then
  cp -r /overrides/* /app;
fi

shutdown() {
  kill -TERM $PID && wait $PID
}

trap "shutdown" TERM

gunicorn --bind 0.0.0.0:5000 app:app &
PID=$!
wait $PID
