#!/bin/bash
/root/updateCore.sh
/root/updateHdfs.sh
/root/updateMapred.sh
/usr/sbin/sshd -D
