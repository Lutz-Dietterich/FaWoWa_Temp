import network
import espnow
import time
import dht
from machine import Pin, deepsleep

# Initialisiere den DHT11-Sensor auf Pin GPIO2 (D4 auf ESP8266/ESP32)
sensor_power = Pin(4, Pin.OUT)  # Pin für die Stromversorgung des DHT11-Sensors
dht_sensor = dht.DHT11(Pin(2)) # Pin für die Datenleitung des DHT11-Sensors

# WLAN-Interface muss aktiv sein, um send()/recv() zu verwenden
sta = network.WLAN(network.STA_IF)  # Oder network.AP_IF
sta.active(True)
sta.disconnect()  # Optional, für ESP8266 relevant

# ESP-NOW initialisieren
e = espnow.ESPNow()
e.active(True)

# MAC-Adressen der Empfänger (Peers)
peer1 = b'\x08\xD1\xF9\xE0\x0E\x94'  # Setze hier die richtige MAC-Adresse für den ersten Empfänger ein
peer2 = b'\x08\xD1\xF9\xDF\xAE\x2C'  # Setze hier die richtige MAC-Adresse für den zweiten Empfänger ein

# Peers hinzufügen
e.add_peer(peer1)  # Ersten Peer hinzufügen
e.add_peer(peer2)  # Zweiten Peer hinzufügen

# Funktion zum Auslesen der Daten vom DHT11-Sensor
def read_dht_data():
    try:
        sensor_power.value(1)  # Sensor mit Strom versorgen
        print("Sensor wird gestartet...")
        time.sleep(2)          # 2 Sekunden warten, damit der Sensor starten kann
        dht_sensor.measure()  # Daten vom DHT11-Sensor auslesen
        print("Daten vom Sensor ausgelesen.")
        sensor_power.value(0)  # Sensor ausschalten
        print("Sensor wird ausgeschaltet.")
        temperature = dht_sensor.temperature()  # Temperatur in °C
        humidity = dht_sensor.humidity()        # Luftfeuchtigkeit in %
        return temperature, humidity
    except OSError as e:
        print("Fehler beim Auslesen des DHT11-Sensors:", e)
        return None, None

# Funktion zum Senden der DHT-Daten an beide Empfänger
def send_dht_data():
    temperature, humidity = read_dht_data()  # DHT11-Daten auslesen
    if temperature is not None and humidity is not None:
        # Nachricht formatieren
        message = f"Temperatur: {temperature}°C, Luftfeuchtigkeit: {humidity}%"
        
        # Nachricht an beide Peers senden
        e.send(peer1, message)
        print(f"Daten an Peer1 gesendet: {message}")
        
        e.send(peer2, message)
        print(f"Daten an Peer2 gesendet: {message}")

# Hauptprogramm
print("Sende DHT11-Daten an zwei Empfänger und gehe dann in Deep Sleep...")

# Daten senden
send_dht_data()

# Deep Sleep für 60 Sekunden (1 Minute)
time_in_ms = 60 * 1000  # 60 Sekunden in Millisekunden
print("Gehe in Deep Sleep für 60 Sekunden...")
deepsleep(time_in_ms)

