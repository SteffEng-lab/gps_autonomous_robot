# Connect PS4 Controller via Bluetooth
1. Install Bluetooth Tools
bashsudo apt install bluetooth bluez bluez-tools -y
sudo systemctl enable --now bluetooth

2. Open Bluetooth Console
bluetoothctl

3. Pair Controller
Inside bluetoothctl:

power on
agent on
default-agent
scan on

Put controller into pairing mode:
→ Hold Share + PS button simultaneously until LED flashes rapidly
Controller appears in bluetoothctl:
[NEW] Device XX:XX:XX:XX:XX:XX Wireless Controller

pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
scan off
exit