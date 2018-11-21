python PYMONT_Monitoring_v1.0.py --cli --conf CRISLER_config.json &> "logs/$(date +%F_%H-%M-%S)_pymontlog.log" &
bokeh serve --log-level debug PYMONT_IntranetDisplay.py --allow-websocket-origin=134.171.12.57:5006 &> "logs/$(date +%F_%H-%M-%S)_pymontlog.log" &

