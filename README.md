# BrewersEye
Homebrew remote sensor array

![Output waveform](hardware.jpg?raw=true "Fermenter hooked up to Sensor arryay")


#### Developed by: Micheal Burin
A simple sensor array that transmits temperature and bubble rates via Zigbee

# Notes and Installation Instructions
This project is meant to run on **Python 3**. Specifically tested under **3.7.3**

Project additionally uses **Node.js**. version **v10.16.3**
```sh
curl -sL https://deb.nodesource.com/setup_10.x | sudo bash -
    sudo apt-get install -y nodejs
    node --version
        v10.16.3
```

**pip3 install**\
python3-pip     8.1.1-2ubuntu0.4\

**apt-get install**\
python3-mysqldb\
mariadb-server\
tornado

**Javascript libraries are already included in Subprojects**\
vis (version 6.2.9)\
jqeury (version 3.4.1)

# Installation Instructions

**MySQL-like database setup**
```sh
$ sudo mysql_secure_installation
    Enter current password for root (enter for none):
    Set root password? [Y/n]    <eidf19>
    Remove anonymous users? [Y/n]   <enter>
    Disallow root login remotely? [Y/n] <enter>
    Remove test database and access to it? [Y/n] <enter>
    Reload privilege tables now? [Y/n] <enter>
```

**Create MySQl sensors user for database**
```sh
$ sudo mysql
    CREATE USER 'sensors'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON * . * TO 'sensors'@'localhost';
    FLUSH PRIVILEGES;
    quit
```

**Give sensors user permissions**

```sh
$ sudo mysql (Yeah, there's a problem with using our root login)
    GRANT ALL PRIVILEGES ON project1.* TO 'sensors'@'localhost';
    FLUSH PRIVILEGES;
```

**Setup node database and tables**

```sh
$ mysql -u sensors --password=password
    CREATE DATABASE node88;
    USE node88

    create table sensor1 (id BIGINT not NULL AUTO_INCREMENT, value FLOAT(24), timestamp DATETIME(6), PRIMARY KEY (id));
    create table sensor2 (id BIGINT not NULL AUTO_INCREMENT, value FLOAT(24), timestamp DATETIME(6), PRIMARY KEY (id));
    create table bubbles (id BIGINT not NULL AUTO_INCREMENT, value INT, timestamp DATETIME(6), PRIMARY KEY (id));

# 12-8-2019 Fix this, so latest wrties are readable:

    # https://stackoverflow.com/questions/5943418/chronic-stale-results-using-mysqldb-in-python
    MariaDB [node88]> SELECT @@GLOBAL.tx_isolation, @@tx_isolation;
    +-----------------------+-----------------+
    | @@GLOBAL.tx_isolation | @@tx_isolation  |
    +-----------------------+-----------------+
    | REPEATABLE-READ       | REPEATABLE-READ |
    +-----------------------+-----------------+
    1 row in set (0.001 sec)

    SET GLOBAL tx_isolation='READ-COMMITTED';
    SET SESSION tx_isolation='READ-COMMITTED';

    MariaDB [node88]> SELECT @@GLOBAL.tx_isolation, @@tx_isolation;
    +-----------------------+----------------+
    | @@GLOBAL.tx_isolation | @@tx_isolation |
    +-----------------------+----------------+
    | READ-COMMITTED        | READ-COMMITTED |
    +-----------------------+----------------+
    1 row in set (0.001 sec)

```

**Install code from GitHub**

```sh
$ git clone --recurse-submodules https://github.com/burinm/EID.git
$ cd BrewersEye 

#sensors array
    sudo cp bubbles.service -> /lib/systemd/system/
    systemctl enable bubbles

    # useful information
    # https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6
    # 
    # For my implementation, I copied sshd.service and modified it

```

**Run - sensors array**
```sh
systemctl start bubbles
```

**Run - gateway**
```sh
nohup ./receive.py &
(optional) tail -f nohup.out

./webserver.py
```

Point your web browser to 172.16.0.1:8080\
(additionally you may need to modify webserver.py if this address doesn't fit your network)
