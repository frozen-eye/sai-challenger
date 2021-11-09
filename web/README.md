# Scripts

## Sources update and start the webui

```bash
# update the sources with the latest changes
$ cd /src/sai-challenger/
$ git pull
Already up to date.

# restart the container and create a switch
$ docker restart sai-challenger-run
sai-challenger-run

$ docker exec -it sai-challenger-run sh -c "sai create switch SAI_SWITCH_ATTR_INIT_SWITCH true SAI_SWITCH_ATTR_TYPE SAI_SWITCH_TYPE_NPU"

SWITCH
       1)  oid:0x21000000000000

# check if switch exists
$ docker exec -it sai-challenger-run sh -c "sai list switch"

# check if webui is running. should see the following because of automatic webui start
$ docker exec -it sai-challenger-run sh -c "ps ax | grep 'python3 main.py'"
    127 ?        Rl     0:08 python3 main.py
    207 pts/0    Ss+    0:00 bash -c ps ax | grep 'python3 main.py'
    215 pts/0    S+     0:00 grep python3 main.py

```
