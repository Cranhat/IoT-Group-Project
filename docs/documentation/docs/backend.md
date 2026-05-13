# Backend
The backend is built with **FastAPI** and integrates directly with a **PostgreSQL** database.


## Core Components
- **FastAPI App**: Provides a RESTful API for managing users, devices, and logs.
- **Database Class**: A wrapper around `psycopg2` that handles connection pooling, table initialization, and CRUD operations.

## Data Models
- **User**: ID, Name, Privilege.
- **Password**: User association and hashed passwords.
- **Device**: ID, Status, IP Address.
- **Logs**: Task logs, Task result logs, and HTTP traffic logs.
- **Packets**: [TBD]

## API Routes
The backend exposes the following generic endpoints for each supported table:
- `GET /{table}`: Fetch all records.
- `GET /{table}/{id}`: Fetch a specific record by ID.
- `POST /{table}`: Insert a new record (validated via Pydantic).
- `PUT /{table}/{id}`: Update an existing record.

## Security
- **CORS**: Configured to allow requests from the frontend
- **Validation**: Strict schema validation using Pydantic.
- **Environment Config**: Sensitive database credentials are managed via environment variables.
- **Encryption**: End-to-end encryption using TCP wit TLS(Transport Layer Security)

## System Architecture diagram
```puml
@startuml
skinparam componentStyle uml2
skinparam backgroundColor #FFFFFF
skinparam packageBackgroundColor #F9F9F9

package "Client Layer" {
    [Frontend (Vue.js)] as FE
}

package "Backend Layer" {
    [FastAPI (API)] as API
    [Database Logic (Python)] as DB_Logic
}

database "PostgreSQL" as DB {
    folder "Tables" {
        [users]
        [passwords]
        [devices]
        [logs]
    }
}

FE <--> API : HTTP/JSON (REST)
API <--> DB_Logic : Internal Calls
DB_Logic <--> DB : SQL (Psycopg2)

note top of DB_Logic
  Handles:
  - Table Initialization
  - CRUD Operations
  - Object Validation
end note

@enduml
```

## Client-server communication diagram
```puml
@startuml
skinparam backgroundColor #FFFFFF
skinparam activityBackgroundColor #E1F5FE
skinparam activityBorderColor #01579B
skinparam activityDiamondBackgroundColor #E8F5E9
skinparam activityDiamondBorderColor #2E7D32
skinparam noteBackgroundColor #F5F5F5
skinparam noteBorderColor #DDDDDD

title IoT Client-Server Flow

start
:Client becomes online;

partition "Client-Server Connection" {
    if (Server saved?) then (yes)
        :Connect to server\n(TLS);
    else (no)
        repeat
            :Advertise;
        repeat while (Server initiated\nconnection?) is (no)
        ->yes;
        :Connect to server\n(TLS);
    endif

    while (Connection\nsuccessful?) is (no)
        :Send information to\nserver (?);
        :Connect to server\n(TLS);
    endwhile (yes)

    if (Add to trusted\ndevices?\n[SERVER]) then (yes)
        :Save server;
    else (no)
        :Continue without\nsaving server;
    endif

    :Send available\nlibraries information;

    note right
      Client connection security:
      - Store server information
      - Connection initiation
      - Encrypt data channel

      Two available models:
      - Consider a dynamic database with available
        libraries on the server
      - Client sends only the board type id
    end note
}

partition "Task Execution" {
    while (Received\ninstructions?) is (no)
        :Send available\nlibraries information;
    endwhile (yes)

    :Read instructions;
    note left
      Process memory
    end note

    :Execute instructions;
    :Wait 5s;
    while (Is job done?) is (no)
        :Send "working..." info\nto the server;
        :Execute instructions;
        :Wait 5s;
    endwhile (yes)

    if (Was execution\nsuccessful\n(no errors)?) then (yes)
        :Send "success" message to\nthe server with results;
    else (no)
        :Send "error" message\nto the server with info;
    endif

    :Send "ready" status\ninfo to the server;
}

:Success;
stop

@enduml
```
