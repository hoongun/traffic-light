Traffic light
=============

A web server, which process observations of traffic light


**Installation**::

    sudo docker pull ubuntu:14.04
    sudo docker run -i -t -p 8080:8080 -v /absolute/path/to/current/folder:/mnt ubuntu:14.04

    apt-get update
    apt-get install -y python python-pip python-sqlalchemy python-flask python-flask-sqlalchemy
    
    cd /mnt
    dpkg -i traffic-light.deb
    service traffic-light start
    
    # If you want to change a port or IP(0.0.0.0:8080 by default):
    # vi /etc/default/traffic-light

**Tests**::

    python setup.py test


**Sample of curl scripts to test the service**::

    curl -i -H "Content-Type: application/json" -X POST -d '{}' http://127.0.0.1:8080/sequence/create
    curl -i -H "Content-Type: application/json" -X POST -d '{"observation": {"color": "green","numbers": ["1110111", "0011101"]},"sequence": "7750e067-2372-499d-98c0-84a81300a0d2"}' http://127.0.0.1:8080/observation/add
    curl -i -H "Content-Type: application/json" -X POST -d '{"observation": {"color": "green","numbers": ["1110111", "0010000"]}, "sequence": "7750e067-2372-499d-98c0-84a81300a0d2"}' http://127.0.0.1:8080/observation/add
    curl -i -H "Content-Type: application/json" -X POST -d '{"observation": {"color": "red"}, "sequence": "7750e067-2372-499d-98c0-84a81300a0d2"}' http://127.0.0.1:8080/observation/add
    curl -i -H "Content-Type: application/json" -X POST -d '{}' http://127.0.0.1:8080/clear
