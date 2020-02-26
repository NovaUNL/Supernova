Development guide
=================
Requirements
------------
In order to get a Supernova instance running, one has a few requirements:

- Docker installed
- 2-3GB of **spare** RAM
- Possibly a Linux host (TODO: confirm this)

It is expected from you to have some knowledge of Python and to know how to use a command prompt.
A vague idea about Docker would also come handy, although it is not that needed.

| In case you have no clue about these things, feel free to contact us (through the provided communication
  channels in the homepage) and ask for some help. Supernova is not that hard (at least most of it), and as such
  is a decent pretext to learn more about these technologies.
| From now on it is assumed that you somewhat know what you are doing.

Installation
------------
| 1. Setup docker and docker compose.
  `Debian <https://docs.docker.com/install/linux/docker-ce/debian/>`_, `Ubuntu <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_, `Arch <https://wiki.archlinux.org/index.php/Docker>`_, `Fedora <https://docs.docker.com/install/linux/docker-ce/fedora/>`_.
| Make sure that the daemon is running.

2. Point your favourite shell at this project's root folder
::

$ cd /repository/root

3.  Build the development docker image
::

# docker build -f Dockerfile-dev -t supernova-dev .

4. Fetch the necessary images and build their containers
::

# docker-compose -f docker-compose-dev.yml up --no-start

5. Apply a few kernel tweaks to ensure smooth sailing
::

# sysctl -w vm.max_map_count=262144
# echo never > /sys/kernel/mm/transparent_hugepage/enabled

(these do **not** persist on reboot, if your system becomes troublesome rebooting might help)

6. Create a configuration file for Supernova
::

$ cp ./conf/settings.example.json ./conf/settings-dev.json

(Edit the new file in case you need CLIPy or email functionality)

7. The moment of truth
::

# docker-compose -f docker-compose-dev.yml up

After a few seconds you should be left with the following services running:

+----------------+------+
| Service        | Port |
+================+======+
| Nginx          | 80   |
+----------------+------+
| Pgadmin        | 81   |
+----------------+------+
| Kibana         | 82   |
+----------------+------+
| Supernova-wsgi | 1893 |
+----------------+------+
| Postgres       | 5432 |
+----------------+------+
| Redis          | 6379 |
+----------------+------+
| Elasticsearch  | 9200 |
+----------------+------+
| Logstash       | 5959 |
+----------------+------+

The default user is ``supernova``, email ``admin@supernova`` and password ``changeme``.


| While the CLIP data is read-only and unmanaged by Supernova,
  you need to instantiate the CLIPy tables as they are expected to exist.
| To create them fire up a python3 terminal inside the django container:

::

  # docker exec -it sn_django bash
  $ python3

You need to let the crawler taste the database. It will instantiate every missing table.

::

  from CLIPy import CacheStorage
  storage = CacheStorage.postgresql('supernova', 'changeme', 'supernova')


| Close the python interpreter (``CTRL + c`` should do).
| Now you need to tell Supernova to instantiate its tables.

::

  python3 manage.py makemigrations
  python3 manage.py migrate

And finally, you need to create a user and add at least one catchphrase/slogan

::

  python3 manage.py createsuperuser
  python3 manage.py addcatchphrase "The awesome system"

| By now Supernova is running.
| Note that with the default settings Supernova is only accessible in the loopback network interface.

To stop docker compose press ``CTRL + c`` in the execution terminal.