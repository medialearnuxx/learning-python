# learning-python

**General Information**

This is just a very simple Python applications from a total beginner.
The application has a CRUD function to retrieve, create, update and delete the users with just 3 column in 'Users' table as follows :
1. id   : sequentially id of the users (1,2,3, ..., n)
2. name : name of the users and must be unique
3. character_type : refer to common game, maybe the character just Wizard, Fighter, Assasin, etc (but not specify in this application)

**Prerequsite**

1. Install database **Postgresql** on your local machine.
Please go to this link https://www.postgresql.org/download/ download and install based on your operating system.

2. Create a new database, database user and password
let say, create a new database called **'dummies_db'**, user **'operator'** and password **'password'**
```
$ psql postgres
postgres=# CREATE ROLE operator with LOGIN PASSWORD 'password';
postgres=# ALTER ROLE operator CREATEDB;
postgres=# CREATE DATABASE dummies_db;
postgres=# GRANT ALL PRIVILEGES ON DATABASE dummies_db TO operator;
```

3. Install **Docker** on your local machine.
Please go to this link https://docs.docker.com/desktop/ and follow the steps based on your operating system.

**Configuration**

1. Update Postgresql configs since it is running locally, we need to make it listen to any addresses in our local machine.
- search your Postgresql installation with common command ```$ which postgres```
- update ```listen_addresses``` value in **postgresql.conf** from ```localhost``` to ```*```
- update ```IPv4 local connections``` in **pg_hba.conf** from ```127.0.0.1/32``` to ```0.0.0.0/0```

2. Update database **config.yaml**
- in the Prerequsite, we already create database, user and password. then update config.yaml according to your db name, user and password
```
database:
  dbname: "database name"
  user: "database user"
  password: "user password"
  host: "your local machine ip address"
  port: "default postgresql port or 5432"
```

**Build and Run Docker Image**

There are 2 Dockerfile
- ```Dockerfile_app``` to build application image
- ```Dockerfile_nginx``` to build nginx image to reverse the application backend port to 80 and apply rate limiter

1. Run this command on your local machine to build Docker image called **my-app** and **expose-app**

```
$ docker build -t my-app -f Dockerfile_app .
$ docker build -t expose-app -f Dockerfile_nginx .
```

2. Before you create and run docker container, create a docker network so that nginx and app able to communicate in the network
```
$ docker network create app-network
```

3. Run this command on your local machine to create a container called **my-app** and **expose-app** from each Docker image
```
$ docker run -d --name my-app --network app-network -p 8080:8080  my-app
$ docker run -d --name expose-app -p 80:80 --network app-network --link my-app:my-app expose-app
```

4. Check your docker container status
```
$ docker ps
```
and the output should be looks like
```
CONTAINER ID   IMAGE        COMMAND                  CREATED       STATUS          PORTS                    NAMES
ef523e84817e   expose-app   "/docker-entrypoint.…"   5 hours ago   Up 10 seconds   0.0.0.0:80->80/tcp       expose-app
6811ae9370e6   my-app       "python app.py"          5 hours ago   Up 12 seconds   0.0.0.0:8080->8080/tcp   my-app
```
