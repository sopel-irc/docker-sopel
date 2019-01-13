# Sopel for Docker
[![Docker Stars](https://img.shields.io/docker/stars/sopelirc/sopel.svg)](https://hub.docker.com/r/sopelirc/sopel)
[![Docker Pulls](https://img.shields.io/docker/pulls/sopelirc/sopel.svg)](https://hub.docker.com/r/sopelirc/sopel)
[![Image Layers](https://images.microbadger.com/badges/image/sopelirc/sopel.svg)](https://microbadger.com/images/sopelirc/sopel)
[![Build from Commit](https://images.microbadger.com/badges/commit/sopelirc/sopel.svg)](https://microbadger.com/images/sopelirc/sopel)

:whale: Officially Unofficial™ Docker container for Sopel, a Python IRC bot

##### Relevant links
* Sopel Homepage @ [Sopel, The Python IRC Bot](https://sopel.chat)
* Sople GitHub @ [sopel-irc/sopel](https://github.com/sopel-irc/sopel)
* Docker GitHub @ [sopel-irc/sopel-docker](https://github.com/sopel-irl/sopel-docker)
* Docker Registry @ [sopelirc/sopel](https://hub.docker.com/r/sopel-irc/sopel)

## Quickstart

* Pull the docker image for the latest Sopel release ([v6.5.3]([https://github.com/sopel-irc/sopel/releases/tag/v6.5.3))

      $ docker pull sopelirc/sopel:latest 

* Start your bot. Specify a name (e.g., `my_first_sopel`) for the container to make subsequent startups
and shutdowns easier.

      $ docker run --name=my_first_sopel -ti sopelirc/sopel

    On the first run, you will be taken through the setup wizard to write the bot's
    configuration file. See the ["First run" Sopel Wiki entry](https://github.com/sopel-irc/sopel/wiki/Sopel-tutorial,-Part-1#first-run) for more details.

#### Stopping and starting the bot
* You can stop the bot started with the command above with a simple keyboard
interrupt (`Ctrl-C`), or use the docker stop command: `docker stop my_first_sopel`
* The bot can be restarted with the docker start command: `docker start -ia my_first_sopel`. _Note: containers started with `docker start ...` need to be
stopped with `docker stop ...` (`Ctrl-C` will not work) as in the example above.
-----
# :construction: :construction: :construction: :construction: :construction: </h2>
**Detailed documentation is under construction.** 

_Check back soon!_ :smile: