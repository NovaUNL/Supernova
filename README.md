# Supernova

Here are the sources of the Supernova portal. A service that complements CLIP (the campus system), providing some useful services.  
This stated being written in late 2017, and will hopefully reach general availability somewhere in 2020.

Currently it is being matched with the systems from the College of Sciences and Technology of the New university of Lisbon (FCT-NOVA Lisboa), but it should be adaptable to run with something else if that is your wish.


## Team
Some C.S.(good ol' Informática) student that goes by the name Cláudio Pereira, and (hopefully) many more in the short future ~~specially since it took me a lot of time to make the development process noob friendly, write documentation, etc ...~~

### But... why?
Because learning is the most valuable thing one can do with his spare time.
Also, hopefully this will be useful to the thousands of students that will come after me.



## Build & run
Get yourself a Linux system with at least 2-3GB of **spare** RAM.
If you have less RAM do not bother trying to run this without tweaking the default configurations.  
No clue it this runs on non-Linux systems, it should mostly work but you are on your own.

### Dependencies:
It's recommended you install these from the package manager for your system.

- [python3](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [docker](https://docs.docker.com/get-docker/)
- [docker compose](https://docs.docker.com/compose/install/)
- [sass](https://sass-lang.com/install)
- [GDAL](https://gdal.org/)


1  Setup docker and docker compose. [Debian](https://docs.docker.com/install/linux/docker-ce/ubuntu/), [Ubuntu](https://docs.docker.com/install/linux/docker-ce/debian/), [Arch](https://wiki.archlinux.org/index.php/Docker), [Fedora](https://docs.docker.com/install/linux/docker-ce/fedora/).  
  Make sure that the daemon is running.
  
2 Point your favourite shell at this project's root folder
   > $cd /repository/root

3  Build the development image
   > \#docker build -f Dockerfile-dev -t supernova-dev .

4  Fetch the necessary images and build their containers
   > \#docker-compose -f docker-compose-dev.yml up --no-start 

5 Apply a few kernel tweaks to ensure smooth sailing
   > \#sysctl -w vm.max_map_count=262144
   
   > \#echo never > /sys/kernel/mm/transparent_hugepage/enabled

 (these do **not** persist on reboot, if your system becomes troublesome rebooting might help)

6 Create a configuration file for supernova
   > $ cp ./conf/settings.example.json ./conf/settings-dev.json
   
   (Edit the new file in case you need CLIPy or email functionality)

7 The moment of truth
   > \# docker-compose -f docker-compose-dev.yml up

After a few seconds you should be left with the following services running:

| Service        | Port |
| ---------------|:----:|
| Nginx          | 80   |
| Pgadmin        | 81   |
| Kibana         | 82   |
| Supernova-wsgi | 1893 |
| Postgres       | 5432 |
| Redis          | 6379 |
| Elasticsearch  | 9200 |
| Logstash       | 5959 |

The default user is `supernova`, email `admin@supernova` and password `changeme`.

8 Create a virtual environment and install the pip packages:
```
$ python3 -m venv ./venv
$ ./venv/bin/pip install -r pip-packages
```

9 Now you need to instruct Django to generate the database migrations for every app and apply them to the database.
```
$ ./venv/bin/python ./source/manage.py makemigrations chat college documents exercises feedback groups news planet services store supernova synopses users
$ ./venv/bin/python ./source/manage.py migrate
```

10 Create a user and add at least one catchphrase/slogan
```
$ ./venv/bin/python ./source/manage.py createsuperuser
$ ./venv/bin/python ./source/manage.py addcatchphrase "The awesome system"
```

11 Compile the styles:
```
$ sass ./source/static/sass/style.sass:./source/static/css/style.css
```

12 And finally, run the server:
```
$ ./venv/bin/python ./source/manage.py runserver localhost:8000
```

By now supernova is running. With the default settings supernova is only accessible in the loopback network interface.

To stop docker compose press `ctrl + c` in the execution terminal.