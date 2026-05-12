## Packet Sniffer
The packet sniffer is responsible for monitoring network traffic on a specific port and logging relevant data.

### Workflow
```puml
@startuml
skinparam backgroundColor #FFFFFF
skinparam activityBackgroundColor #E1F5FE
skinparam activityBorderColor #01579B

title Packet Sniffer Flow

start
:Initialize Sniffer;
:Check Root Privileges;
if (Permissions OK?) then (yes)
    :Start Scapy Sniffing;
    repeat
        :Capture TCP Packet;
        if (Port == MONITORED_PORT?) then (yes)
            :Extract IP & TCP Layers;
            if (Has Raw Data?) then (yes)
                :Decode UTF-8;
                :Log Captured Data;
            else (no)
                :Log Binary Data;
            endif
        endif
    repeat while (Timeout reached?) is (no)
    ->yes;
    :Stop Sniffer;
else (no)
    :Log Error & Exit;
endif
stop

@enduml
```

### Key Features
- **Scapy Integration**: Uses Scapy for low-level packet capture.
- **Filtering**: Specifically monitors the `MONITORED_PORT`.
- **Decoding**: Attempts to decode payloads as UTF-8 for readability.
- **Logging**: Provides detailed info about captured packets including source/destination IP and ports.
