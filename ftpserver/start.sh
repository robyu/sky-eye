#!/bin/bash
ftpdir=$(pwd)/../tests/ftpout
logdir=$(pwd)/log

# Check if $ftpdir exists, if not, create it
if [ ! -d "$ftpdir" ]; then
  mkdir -p "$ftpdir"
fi

if [ ! -d "$logdir" ]; then
    mkdir -p "$logdir"
fi

docker run -it \
       -p 21:21 -p 20:20 -p 21100-21110:21100-21110 \
       -e FTP_USER=testuser -e FTP_PASS=testpasswd \
       -e PASV_ADDRESS=127.0.0.1 -e PASV_MIN_PORT=21100 -e PASV_MAX_PORT=21110 \
       -e LOG_STDOUT='' \
       -v "$ftpdir":/home/vsftpd \
       -v "logdir":/var/log/vsftpd \
       --rm --name vsftpd fauria/vsftpd

# docker run -it \
#        -p 21:21 -p 20:20 -p 21100-21110:21100-21110 \
#        -e FTP_USER=testuser -e FTP_PASS=testpasswd \
#        -e PASV_ADDRESS=127.0.0.1 -e PASV_MIN_PORT=21100 -e PASV_MAX_PORT=21110 \
#        -e LOG_STDOUT="yes" \
#        -v "$ftpdir":/home/vsftpd \
#        --rm --name vsftpd fauria/vsftpd
