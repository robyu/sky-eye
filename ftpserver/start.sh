#!/bin/bash
ftpdir=$(pwd)/transfer
logdir=$(pwd)/log
docker run -p 21:21 -p 20:20 -p 21100-21110:21100-21110 \
       -e FTP_USER=myuser -e FTP_PASS=myuser \
       -e PASV_ADDRESS=127.0.0.1 -e PASV_MIN_PORT=21100 -e PASV_MAX_PORT=21110 \
       -e LOGSTDOUT=t \
       -v "$ftpdir":/home/vsftpd \
       -v "logdir":/var/log/vsftpd \
       --rm --name vsftpd fauria/vsftpd
