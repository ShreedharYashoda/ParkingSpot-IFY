# MQTT in ParkingSpot-IFY (Simplified)

This document explains the MQTT flow used by the Android app in a simple, visual way.

## 1) High-level architecture

```text
+--------------------+        +-----------------------+        +-------------------+
| Android App        |        | AWS Cognito           |        | AWS IoT Core      |
| (MqttTestActivity) |<------>| (temporary AWS creds) |------->| (MQTT broker)     |
+--------------------+        +-----------------------+        +-------------------+
         |                                                           ^
         | UI updates (spot1..spot8)                                 |
         v                                                           |
+--------------------+                                              |
| Parking screen     |<---------------------------------------------+
| (icons visible/    |      MQTT messages on Parking/Furnas/spot*    
| invisible)         |
+--------------------+
```

## 2) Connection + certificate bootstrap flow

```text
App start
   |
   v
Initialize AWSMobileClient (Cognito)
   |
   v
Create AWSIotMqttManager(clientId, endpoint)
   |
   v
Is keystore/cert already on device?
   |\
   | yes ------------------> Load cert from keystore
   |
   no
   |
   v
Create new key + cert via AWS IoT API
   |
   v
Attach IoT policy (iotPolicy)
   |
   v
Save cert + private key in local keystore
   |
   v
Enable "Connect" button
```

## 3) Runtime MQTT messaging flow

```text
User taps Connect
   |
   v
MQTT connect(clientKeyStore)
   |
   v
On Connected:
Subscribe to: Parking/Furnas/#   (QoS 0)
   |
   v
Incoming message (topic + payload)
   |
   +--> topic = Parking/Furnas/spot1 ... spot8
   |        payload "1" -> hide car icon (occupied)
   |        else         -> show car icon (available)
   |
   +--> update last-message text + notify listener
```

## 4) Topic model used in this project

```text
Parking/Furnas/#
 ├── Parking/Furnas/spot1
 ├── Parking/Furnas/spot2
 ├── Parking/Furnas/spot3
 ├── Parking/Furnas/spot4
 ├── Parking/Furnas/spot5
 ├── Parking/Furnas/spot6
 ├── Parking/Furnas/spot7
 └── Parking/Furnas/spot8
```

## 5) Quick mental model

- **Cognito** gives app permission to call AWS IoT APIs.
- App ensures it has a device certificate (reuse existing or create once).
- **AWSIotMqttManager** uses that cert to open MQTT session with AWS IoT endpoint.
- App subscribes to `Parking/Furnas/#` and updates parking-slot visuals from payloads.
- App can also manually publish/subscribe via UI fields for testing.
