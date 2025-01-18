To check if any clients are connected to the Mosquitto MQTT broker, you can use the `mosquitto_sub` and `mosquitto_pub` tools, or you can inspect the broker logs. Here are a few methods:

---

### 1. **Check Mosquitto Logs**
Mosquitto logs show information about client connections and disconnections.

#### Steps:
1. Open the terminal.
2. Run the following command to view Mosquitto's logs:
   ```bash
   sudo journalctl -u mosquitto
   ```
3. Look for messages indicating client connections or disconnections. Example log entries:
   ```
   Client clientID1234 connected
   Client clientID1234 disconnected
   ```

---

### 2. **Use `mosquitto_sub` to Subscribe to a Topic**
Subscribing to a topic allows you to see if messages are being published, indicating active clients.

#### Steps:
1. Open a terminal and subscribe to a topic:
   ```bash
   mosquitto_sub -h localhost -t "#" -v
   ```
   - `-h localhost`: Replace `localhost` with the IP or hostname of your MQTT broker.
   - `-t "#"`: Subscribes to all topics (`#` is a wildcard).
   - `-v`: Displays the topic and message.

2. If clients are publishing messages, you will see output like this:
   ```
   topic1 message1
   topic2 message2
   ```

---

### 3. **Query Connected Clients via the Mosquitto Control Interface**
If the Mosquitto control interface is enabled (often on port 1883), you can query the broker for connected clients.

#### Steps:
1. Enable the control interface by editing `/etc/mosquitto/mosquitto.conf` (if not already enabled):
   ```
   listener 1883
   allow_anonymous true
   ```
2. Restart Mosquitto:
   ```bash
   sudo systemctl restart mosquitto
   ```

3. Use an MQTT client tool or script to monitor clients (e.g., `mosquitto_sub` or Python).

---

### 4. **Use `mosquitto_pub` and `mosquitto_sub` for Testing**
You can test the broker by publishing and subscribing to topics:

1. **Open Terminal 1:** Subscribe to a topic:
   ```bash
   mosquitto_sub -h localhost -t "test/topic"
   ```

2. **Open Terminal 2:** Publish a message:
   ```bash
   mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT"
   ```

3. If the subscription terminal receives the message, the broker is functioning and at least these clients are active.

---

### 5. **Use the Mosquitto Command to List Clients**
If supported, you can use the Mosquitto broker commands (requires version 2.x or later):
   ```bash
   mosquitto_ctrl -h localhost clients list
   ```
This will list all currently connected clients.

---

These methods will help you identify if any clients are connected to your Mosquitto broker and monitor their activity.