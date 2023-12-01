---
runme:
  id: 01HGB3X926CP0DBJJ858ASX5W7
  version: v2.0
---

<div align="center">
    <h1>
        TUGAS BESAR IF3130 - Jaringan Komputer 2023 - BJIRKOM 
    </h1>
    <h3 align="center">
        Implementation of <i>TCP-like</i> protocol <i>Go-Back-N</i>
    </h3>
</div>
<br>

## DESCRIPTION

The program consists of a server and a client that communicate over a network using a "TCP-Like" protocol created from scratch. It uses and runs over the UDP protocol to send data, implementing a Three Way Handshake, CRC Checksum, Optimize Buffer and Automatic Repeat Request (ARQ) Go-Back-N. The program uses Python 3 and built-in libraries such as socket, struct, io, etc.

## FEATURE

- Three Way Handshake
- File Transfer with Automatic Repeat Request (ARQ) Go-Back-N
- Optimize Buffer
- Metadata
- Parallelization
- Two end device communication (Virtual with Docker)

## REQUIREMENTS

- Python 3.10 (minimal)
- Docker

## HOW TO RUN

### A. Basic File Transfer (localhost)

1. Make sure the files to be sent are available
2. Run Server with certain arguments

       python Server.py [-h] [-bip BROADCAST_IP] [-bp BROADCAST_PORT] [-ip INPUT_PATH]
       
   Example:

       python Server.py -bip 127.0.0.1 -bp 3001 -ip ./test/video.mkv

3. Run Client with certain arguments (Make sure broadcast port and clients port are different)

       python Client.py [-h] [-cip CLIENT_IP] [-cp CLIENT_PORT] [-bip BROADCAST_IP] [-bp BROADCAST_PORT] [-op OUTPUT_PATH]

   Example:

       python Client.py -cip 127.0.0.1 -cp 3002 -bip 127.0.0.1 -bp 3001 -op video.mkv

4. You can run more than one client at a time.
5. If transfer is succesful, file will be written in folder `out`

### B. Virtual File Transfer

1. Run docker-compose.yml

       docker compose up --build

2. Jump into each container (A server and at least one client must be run). The service name must be the same with the one listed in the docker-compose.yml file.

       docker exec -it $(docker compose ps -q <name-service>) sh

   Example:

       docker exec -it $(docker compose ps -q server) sh  // This is for server container
       docker exec -it $(docker compose ps -q client1) sh  // This is for client container

3. Inside the server container, run Server.py with certain arguments. Make sure that the IP and Port is the same as the one listed in he docker-compose.yml file.

       python Server.py [-h] [-bip BROADCAST_IP] [-bp BROADCAST_PORT] [-ip INPUT_PATH]

4. Inside the client container, run Client.py with certain arguments. Make sure that the IP and Port is the same as the one listed in he docker-compose.yml file.

       python Client.py [-h] [-cip CLIENT_IP] [-cp CLIENT_PORT] [-bip BROADCAST_IP] [-bp BROADCAST_PORT] [-op OUTPUT_PATH]

## TEAM - BJIRKOM

| Name                    |   NIM    |
| ----------------------- | :------: |
| Rizky Abdillah Rasyid   | 13521109 |
| Saddam Annais Shaquille | 13521121 |
| Hanif Muhammad Zhafran  | 13521157 |
