# py_check_redis


Add redis user with these permissions:
```
-@all +info +ping
```

Plugin checks backup nodes automatically for being readonly and connection to master, ie:
```
master_link_status:up
slave_read_only:1
```

Number of expected replicas on a master is configurable, ie:
```
check_redis.py -u monitoring -P $(/usr/bin/cat /etc/check_redis_auth) --backup_nodes=1
```

Or omit the ```--backup_nodes``` flag for a standalone/single instance.
