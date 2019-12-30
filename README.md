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

5 Create a configuration file for supernova
   > $ cp ./conf/settings.example.json ./conf/settings-dev.json
   
   (Edit the new file in case you need CLIPy or email functionality)

6 The moment of truth
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

To stop docker compose press `ctrl + c` in the execution terminal.

Now you only need data. To continue...