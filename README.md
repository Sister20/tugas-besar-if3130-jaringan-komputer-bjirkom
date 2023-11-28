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

The program consists of a <b>server</b> and a <b>client</b> that communicate over a network using a <b>"TCP-Like"</b> protocol created from scratch. It uses and runs over the UDP protocol to send data, implementing a <b>Three Way Handshake</b>, <b>CRC Checksum</b>, <b>Optimize Buffer</b> and <b>Automatic Repeat Request (ARQ) Go-Back-N</b>. The program uses Python 3 and built-in libraries such as socket, struct, io, etc.

## FEATURE

-   Three Way Handshake
-   File Transfer with Automatic Repeat Request (ARQ) Go-Back-N
-   Optimize Buffer
-   Metadata
-   Parallelization
-   Two end device communication (Virtual with Docker)

## REQUIREMENTS

-   Python 3
-   Docker

## HOW TO RUN

### A. Basic File Transfer

1.  Make sure the files to be sent are available
2.  Run Server with certain arguments

        python3 Server.py

3.  Run Client with certain arguments (<i>Make sure broadcast port and clients port are different</i>)

        python3 Client.py

4.  If transfer is succesful, file will be written in folder `out`

### B. Two Virtual File Transfer

1.  Run docker-compose.yml

        docker compose up

2.  Jump into each container

        docker exec -it $(docker compose ps -q <name-service>) sh

3.  Inside the server container run Server.py with certain arguments

        python3 Server.py

4.  Inside the client container run Client.py with certain arguments

        python3 Client.py

## TEAM - BJIRKOM

| Name                    |   NIM    |
| ----------------------- | :------: |
| Rizky Abdillah Rasyid   | 13521109 |
| Saddam Annais Shaquille | 13521121 |
| Hanif Muhammad Zhafran  | 13521157 |
