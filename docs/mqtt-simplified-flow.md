# MQTT in ParkingSpot-IFY (Simplified)

This document explains MQTT in this repo from **both sides**:
1) Android app as MQTT subscriber/UI, and
2) Jetson pipeline as likely upstream publisher for `Parking/Furnas/spot*` messages.

## 1) End-to-end architecture (publisher + subscriber)

```text
         (camera/video frames)
+--------------------------+
| Jetson detection app     |
| ParkingApplicationMQTT.py|
+-----------+--------------+
            |
            | detect car occupancy per spot
            | publish QoS 1
            v
      topic: Parking/Furnas/spot1..spot8
+-------------------------------------------+
| AWS IoT Core (MQTT broker, TLS 8883)      |
+-------------------+-----------------------+
                    |
                    | subscribe QoS 0 to Parking/Furnas/#
                    v
+-------------------------------------------+
| Android app (MqttTestActivity)            |
| updates spot icons in UI                  |
+-------------------------------------------+
```

## 2) Upstream publisher side (Jetson) — likely source of spot topics

The repository contains a concrete publisher implementation in `Jetson/ParkingApplicationMQTT.py`.

### Publisher workflow

```text
Load object detection model
   |
Read frame (video file or stream)
   |
Detect vehicles in frame
   |
For each configured parking center (spot):
   |
   +-- if a car bbox covers that spot center -> status = 0 (occupied)
   +-- else                               -> status stays 1 (available)
   |
Every N frames (frameNo == 35), publish each spot status:
   topic = Parking/Furnas/spot{n}
   payload = 0 or 1
   QoS = 1
```

### Publisher MQTT setup (Jetson)

```text
AWSIoTMQTTClient(clientId="nvidiaEdgeJetson")
  -> endpoint a1qbvgvdp6hvgv-ats.iot.us-east-1.amazonaws.com:8883
  -> TLS certs: root CA + device cert + private key
  -> connect()
  -> publish("Parking/Furnas/spotX", status, qos=1)
```

So the likely producer of `Parking/Furnas/spot*` in this project is:
- **Jetson computer vision process** reading parking footage/stream,
- inferring occupancy per spot,
- publishing per-spot status to AWS IoT Core.

## 3) Subscriber/UI side (Android)

```text
App start
  |
Initialize AWSMobileClient (Cognito)
  |
Create AWSIotMqttManager(clientId, endpoint)
  |
Ensure device cert exists in keystore
  |\
  | yes -> load cert
  | no  -> create key+cert via AWS IoT API, attach policy, save keystore
  |
Enable Connect button
```

At runtime:

```text
User taps Connect
   |
MQTT connect(clientKeyStore)
   |
On Connected -> subscribe Parking/Furnas/# (QoS 0)
   |
Message arrives on Parking/Furnas/spot1..spot8
   |
payload "1" -> hide spot icon (treated occupied in UI logic)
else        -> show spot icon
```

> Note: Jetson comments imply `0` = occupied and `1` = available, while Android UI currently hides icon on `"1"`. That indicates the producer/consumer convention may be inverted and should be standardized.

## 4) Topic model

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

- **Jetson** is the edge publisher (vision -> occupancy -> MQTT messages).
- **AWS IoT Core** is the broker routing those messages.
- **Android app** is the subscriber that turns topic/payload updates into parking-spot visuals.
