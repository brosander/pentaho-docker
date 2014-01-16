#!/bin/bash

su - mongodb -c "/mongodb/bin/mongod --config /home/mongodb/mongod.conf"
/usr/sbin/sshd -D
