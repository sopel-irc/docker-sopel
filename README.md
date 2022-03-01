# Sopel for Docker

[![Docker Stars](https://img.shields.io/docker/stars/sopelirc/sopel.svg)](https://hub.docker.com/r/sopelirc/sopel)
[![Docker Pulls](https://img.shields.io/docker/pulls/sopelirc/sopel.svg)](https://hub.docker.com/r/sopelirc/sopel)
[![Image Layers](https://images.microbadger.com/badges/image/sopelirc/sopel.svg)](https://microbadger.com/images/sopelirc/sopel)
[![Build from Commit](https://images.microbadger.com/badges/commit/sopelirc/sopel.svg)](https://microbadger.com/images/sopelirc/sopel)

:whale: Officially Unofficial™ Docker container for Sopel, a Python IRC bot

**Relevant links**:

* Sopel Homepage @ [Sopel, The Python IRC Bot](https://sopel.chat)
* Sopel GitHub @ [sopel-irc/sopel](https://github.com/sopel-irc/sopel)
* Docker GitHub @ [sopel-irc/docker-sopel](https://github.com/sopel-irc/docker-sopel)
* Docker Registry @ [sopelirc/sopel](https://hub.docker.com/r/sopelirc/sopel)

---

## Quickstart

### First run

* Pull the docker image for the latest Sopel release ([v7.1.8](https://github.com/sopel-irc/sopel/releases/tag/v7.1.8))

    ```console
    $ docker pull sopelirc/sopel:latest
    ```

* Start your bot. Specify a name (e.g., `my_first_sopel`) for the container to make subsequent startups and shutdowns easier.

    ```console
    $ docker run --name=my_first_sopel -ti sopelirc/sopel
    ```

    On the first run, you will be taken through the setup wizard to write the bot's configuration file. See the ["First run" Sopel Wiki entry](https://sopel.chat/tutorials/part-1-installation/#first-run) for more details.

### Stopping and starting the bot

* You can stop the bot started with the command above with a simple keyboard interrupt (`Ctrl-C`), or use the docker stop command: `docker stop my_first_sopel`
* The bot can be restarted with the docker start command: `docker start -ia my_first_sopel`. 

    **Note:**  containers started with `docker start ...` need to be stopped with `docker stop ...` (`Ctrl-C` will not work) as in the example above.

---

## How to use this image

The minimum requirement for a Sopel bot is valid configuration file. You can create one by [starting a new bot](#quickstart), or you can [plug in a configuration file you already have](#use-an-existing-configuration)! While Sopel already comes packaged with a wide variety of modules, you can easily add third-party and custom modules to your container.

### Save a new configuration

Following the [Quickstart](#quickstart) steps will generate a configuration directory in the container's filesystem. You will likely want to extract this to your host for easier modification and persistence. You can use the copy command, `docker cp ...`, to extract the `.cfg` file or entire configuration folder to the directory of your choosing:

* copy the `default.cfg` file to `/some/path/on/the/host` directory
    ```console
    $ docker cp my_first_sopel:/home/sopel/.sopel/default.cfg /some/path/on/the/host/
    ```
* copy the entire `~/.sopel` configuration directory to `/some/path/on/the/host` directory
  
    ```console
    $ docker cp my_first_sopel:/home/sopel/.sopel /some/path/on/the/host/
    ```

The extracted configuration file/folder can now be transfered or copied to be used as a template for other bots.

### Use an existing configuration

A configuration file or folder can be mounted at `/home/sopel/.sopel` for use by the bot. The default configuration file name (`default.cfg`) should be used, or the correct file name should be passed as an argument to the command by appending `-c correct_file_name.cfg` to the `docker run ...` command.

* mount a configuration file
    ```console
    $ docker run -v "/path/to/my/default.cfg:/home/sopel/.sopel/default.cfg" ...
    ```

* mount a configuration folder
    ```console
    $ docker run -v "/path/to/config/folder:/home/sopel/.sopel" ...
    ```

If you are having permission issues, use the [`PUID` and `PGID` environment variables](#puid-and-pgid) to have the user in the container match the host ids. Alternately, you can change ownership of the configuration file/folder to match the container user (`uid=100000`, `gid=100000`)

### Add third-party packages

#### Python packages

##### Modules available from PyPI

See [`EXTRA_PYPI_PACKAGES` environment variable](#extra_pypi_packages).

You can also mount a pip `requirements.txt` formatted file to `/pypi_packages.txt` with a list of packages to be installed on startup.


##### Modules from source

Mount the module source directory into `/home/sopel/.sopel/modules`, and Sopel will automatically recognize and load the module.

#### Alpine Linux packages

See [`EXTRA_APK_PACKAGES` environment variable](#extra_apk_packages).

You can also mount a text file to `/apk_packages.txt` with a list of packages to be installed on startup.

### Nightly Builds

An image based on the master branch of [sopel-irc/sopel](https://github.com/sopel-irc/sopel) is rebuilt each day at 00:00 UTC using the `nightly` tag.

---

## Environment Variables

When you start the bot, you can adjust various settings related to the environment for the bot process by passing one or more environment variables on the `docker run ...` command line. 

### `PUID` and `PGID`

Normally, the `sopel` process runs with `UID` and `GID` of `100000` to prevent any unwanted/accidental access to host resources. This means that mounted volumes will need to allow read and write to a user with those ids. Instead, you can set these to change the ids of the sopel user on startup. For example, 

```console
$ docker run -e PUID=1000 ...
Setting UID for user sopel to 1000... Done.
...
...
Welcome to Sopel. Loading modules...
...
```

where, generally, you would set the `PUID`/`PGID` to match the mounted volume owner ids.

### `EXTRA_PYPI_PACKAGES`

Packages from PyPI can be installed at startup by providing a space separated list of package names. Since `pip install ...` is being called under the hood, any pip-valid package name is acceptable. For example,

```console
$ docker run -e EXTRA_PYPI_PACKAGES="sopel-modules.weather google-api-python-client sopel-modules.youtube" ...
Installing package "sopel-modules.weather" with pip...
...
Installing package "google-api-python-client" with pip...
...
Installing package "sopel-modules.youtube" with pip...
...
...
Welcome to Sopel. Loading modules...
...
```

will install the [sopel weather module](https://pypi.org/project/sopel-modules.weather), the [sopel YouTube module](https://pypi.org/project/sopel_modules.youtube) and its [google-api-python-client](https://pypi.org/project/google-api-python-client) requirement.

### `EXTRA_APK_PACKAGES`

Occasionally, you may need to install system packages to satisfy requirements for various Python packages. These packages can be specified as a space separated list of packages to be installed by `apk add --no-cache ...`. For example, you may need a database client, various tools required for compiling source code, and git to allow pip to install from a repository:

```console
$ docker run -e EXTRA_APK_PACKAGES="mysql-client build-base git" ...
Installing apk packages: mysql-client build-base git...
...
...
Welcome to Sopel. Loading modules...
...
```

will install the required system packages.
