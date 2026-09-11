# Terminal Log

Shell output captured for the Docker setup session on Fri Sep 11 16:59:17 IST 2026.
Every command is shown as `$ command` followed by its output.

```text
$ docker --version
Docker version 29.7.2, build a7dcaa6
[exit 0]

$ docker compose version
Docker Compose version v5.5.1
[exit 0]

$ docker compose ps
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
[exit 0]

$ docker compose up --build -d
 Image postgres:16-alpine Pulling 
 8bc4580efc9a Pulling fs layer 0B
 83373364c1a1 Pulling fs layer 0B
 5de55e5ef9c0 Pulling fs layer 0B
 9441768a3c04 Pulling fs layer 0B
 baa69516db24 Pulling fs layer 0B
 cfa20b885895 Pulling fs layer 0B
 0931630a3433 Pulling fs layer 0B
 e365de836bbc Pulling fs layer 0B
 262f5476e213 Pulling fs layer 0B
 bf5ce8e8fb48 Pulling fs layer 0B
 e46a888c76da Pulling fs layer 0B
 8bc4580efc9a Download complete 0B
 5de55e5ef9c0 Downloading 1.049MB
 5de55e5ef9c0 Downloading 2.097MB
 baa69516db24 Download complete 0B
 5de55e5ef9c0 Download complete 0B
 5de55e5ef9c0 Extracting 1B
 5de55e5ef9c0 Extracting 1B
 5de55e5ef9c0 Extracting 1B
 83373364c1a1 Downloading 1.049MB
 cfa20b885895 Download complete 0B
 5de55e5ef9c0 Extracting 1B
 83373364c1a1 Downloading 2.097MB
 5de55e5ef9c0 Extracting 1B
 e46a888c76da Download complete 0B
 83373364c1a1 Downloading 4.194MB
 5de55e5ef9c0 Extracting 1B
 83373364c1a1 Downloading 5.243MB
 5de55e5ef9c0 Extracting 1B
 83373364c1a1 Downloading 7.34MB
 5de55e5ef9c0 Extracting 1B
 e365de836bbc Download complete 0B
 83373364c1a1 Downloading 8.389MB
 9441768a3c04 Download complete 0B
 5de55e5ef9c0 Extracting 1B
 83373364c1a1 Downloading 9.437MB
 5de55e5ef9c0 Extracting 1B
 83373364c1a1 Downloading 10.49MB
 5de55e5ef9c0 Extracting 2B
 0931630a3433 Download complete 0B
 83373364c1a1 Downloading 11.53MB
 262f5476e213 Download complete 0B
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 12.58MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 13.63MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 15.73MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 15.73MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 17.83MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 18.87MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 20.97MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 20.97MB
 5de55e5ef9c0 Extracting 2B
 83373364c1a1 Downloading 22.02MB
 5de55e5ef9c0 Extracting 3B
 bf5ce8e8fb48 Download complete 0B
 83373364c1a1 Downloading 24.12MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 25.17MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 26.21MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 27.26MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 29.36MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 30.41MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 31.46MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 32.51MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 33.55MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 35.65MB
 5de55e5ef9c0 Extracting 3B
 83373364c1a1 Downloading 36.7MB
 5de55e5ef9c0 Extracting 4B
 83373364c1a1 Downloading 37.75MB
 5de55e5ef9c0 Extracting 4B
 83373364c1a1 Downloading 38.8MB
 5de55e5ef9c0 Extracting 4B
 83373364c1a1 Downloading 39.85MB
 5de55e5ef9c0 Extracting 4B
 83373364c1a1 Downloading 40.89MB
 5de55e5ef9c0 Extracting 4B
 83373364c1a1 Downloading 42.99MB
 5de55e5ef9c0 Extracting 4B
 83373364c1a1 Downloading 44.04MB
 5de55e5ef9c0 Pull complete 0B
 9441768a3c04 Pull complete 0B
 83373364c1a1 Downloading 45.09MB
 cfa20b885895 Pull complete 0B
 262f5476e213 Pull complete 0B
 bf5ce8e8fb48 Pull complete 0B
 83373364c1a1 Downloading 46.14MB
 83373364c1a1 Downloading 47.19MB
 83373364c1a1 Downloading 48.23MB
 83373364c1a1 Downloading 50.33MB
 9acfa0754869 Downloading 597.4kB
 83373364c1a1 Downloading 51.38MB
 9acfa0754869 Download complete 0B
 83373364c1a1 Downloading 52.43MB
 83373364c1a1 Downloading 53.48MB
 83373364c1a1 Downloading 54.53MB
 83373364c1a1 Downloading 55.57MB
 83373364c1a1 Downloading 56.62MB
 83373364c1a1 Downloading 57.67MB
 83373364c1a1 Downloading 59.77MB
 83373364c1a1 Downloading 60.82MB
 83373364c1a1 Downloading 61.87MB
 83373364c1a1 Downloading 63.96MB
 83373364c1a1 Downloading 65.01MB
 83373364c1a1 Downloading 66.06MB
 83373364c1a1 Downloading 67.11MB
 83373364c1a1 Downloading 68.16MB
 83373364c1a1 Downloading 70.25MB
 83373364c1a1 Downloading 71.3MB
 83373364c1a1 Downloading 72.35MB
 83373364c1a1 Downloading 73.4MB
 83373364c1a1 Downloading 75.5MB
 83373364c1a1 Downloading 75.5MB
 83373364c1a1 Downloading 76.55MB
 83373364c1a1 Downloading 78.64MB
 c0c3b63dd3e0 Download complete 0B
 83373364c1a1 Downloading 79.69MB
 83373364c1a1 Downloading 81.79MB
 83373364c1a1 Downloading 82.84MB
 83373364c1a1 Downloading 83.89MB
 83373364c1a1 Downloading 84.93MB
 83373364c1a1 Downloading 85.98MB
 83373364c1a1 Downloading 88.08MB
 83373364c1a1 Downloading 89.13MB
 83373364c1a1 Downloading 90.18MB
 83373364c1a1 Downloading 91.23MB
 83373364c1a1 Downloading 92.27MB
 83373364c1a1 Downloading 94.37MB
 83373364c1a1 Downloading 95.42MB
 83373364c1a1 Downloading 96.47MB
 83373364c1a1 Downloading 97.52MB
 83373364c1a1 Downloading 98.57MB
 83373364c1a1 Downloading 100.7MB
 83373364c1a1 Downloading 101.7MB
 83373364c1a1 Downloading 102.8MB
 83373364c1a1 Downloading 103.8MB
 83373364c1a1 Downloading 104.9MB
 83373364c1a1 Downloading 105.9MB
 83373364c1a1 Downloading 108MB
 83373364c1a1 Downloading 108.8MB
 83373364c1a1 Download complete 0B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 1B
 83373364c1a1 Extracting 2B
 8bc4580efc9a Pull complete 0B
 baa69516db24 Pull complete 0B
 e46a888c76da Pull complete 0B
 e365de836bbc Pull complete 0B
 0931630a3433 Pull complete 0B
 83373364c1a1 Pull complete 0B
 Image postgres:16-alpine Pulled 
 Image q-taskboard-frontend Building 
 Image q-taskboard-backend Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.09kB done
#1 DONE 0.0s

#2 [backend internal] load build definition from Dockerfile
#2 transferring dockerfile: 364B done
#2 DONE 0.0s

#3 [frontend internal] load build definition from Dockerfile
#3 transferring dockerfile: 214B done
#3 DONE 0.0s

#4 [frontend internal] load metadata for docker.io/library/node:20-bookworm-slim
#4 DONE 2.3s

#5 [backend internal] load metadata for docker.io/library/python:3.12-slim
#5 ...

#6 [frontend internal] load .dockerignore
#6 transferring context: 2B done
#6 DONE 0.0s

#7 [frontend internal] load build context
#7 transferring context: 33.70kB done
#7 DONE 0.0s

#8 [frontend 1/5] FROM docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
#8 resolve docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0 0.0s done
#8 sha256:ed7f19ee07f992aa9ce9fa1ca75db4ae36641464e404f6b720b4afce41cab9e4 0B / 447B 0.2s
#8 sha256:ed7f19ee07f992aa9ce9fa1ca75db4ae36641464e404f6b720b4afce41cab9e4 447B / 447B 0.2s done
#8 sha256:791fd1b17847094616ace4f04066a269c36bb89561d5d7f1a0dba4f615e16716 0B / 1.71MB 0.3s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 0B / 41.39MB 0.3s
#8 sha256:93f1e44b7642d94207805933fd52fd7b5a5a684cf69b340ae3df415754a0a614 0B / 3.31kB 0.2s
#8 ...

#5 [backend internal] load metadata for docker.io/library/python:3.12-slim
#5 DONE 2.7s

#9 [backend internal] load .dockerignore
#9 transferring context: 2B done
#9 DONE 0.0s

#8 [frontend 1/5] FROM docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 0B / 28.12MB 0.2s
#8 ...

#10 [backend internal] load build context
#10 transferring context: 40.45kB 0.0s done
#10 DONE 0.0s

#8 [frontend 1/5] FROM docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
#8 sha256:791fd1b17847094616ace4f04066a269c36bb89561d5d7f1a0dba4f615e16716 1.71MB / 1.71MB 0.6s done
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 3.15MB / 41.39MB 0.9s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 5.24MB / 41.39MB 1.1s
#8 sha256:93f1e44b7642d94207805933fd52fd7b5a5a684cf69b340ae3df415754a0a614 3.31kB / 3.31kB 1.1s done
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 7.34MB / 41.39MB 1.2s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 10.49MB / 41.39MB 1.5s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 12.58MB / 41.39MB 1.7s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 15.73MB / 41.39MB 2.0s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 17.83MB / 41.39MB 2.3s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 19.92MB / 41.39MB 2.4s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 22.02MB / 41.39MB 2.7s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 2.10MB / 28.12MB 2.6s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 24.12MB / 41.39MB 3.0s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 26.21MB / 41.39MB 3.3s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 28.31MB / 41.39MB 3.6s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 4.19MB / 28.12MB 3.6s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 30.41MB / 41.39MB 3.9s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 32.51MB / 41.39MB 4.2s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 34.60MB / 41.39MB 4.5s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 37.75MB / 41.39MB 4.8s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 6.29MB / 28.12MB 4.8s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 39.85MB / 41.39MB 5.1s
#8 sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 41.39MB / 41.39MB 5.3s done
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 8.39MB / 28.12MB 6.0s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 10.49MB / 28.12MB 6.6s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 12.58MB / 28.12MB 7.2s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 14.68MB / 28.12MB 7.8s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 16.78MB / 28.12MB 8.4s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 18.87MB / 28.12MB 9.2s
#8 ...

#11 [backend 1/6] FROM docker.io/library/python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
#11 resolve docker.io/library/python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea 0.0s done
#11 sha256:3550292b2150d689c8a69849320a815d1d54883f6aecf670f098c1a16f2c5436 251B / 251B 0.5s done
#11 sha256:8aff2d3a9af8ed70ae2aa065663f6a7b99d3cd41564528e8d5f039ec0faae595 12.05MB / 12.05MB 6.6s done
#11 sha256:bf7af0229701decd1b9f42143504fc8f69e5664c37e57001d198e731e4f86c2e 30.16MB / 30.16MB 8.2s done
#11 sha256:ab2cb3ee67af16dd0212f1564a3c1a7bfc96172b7c21c74895492bd87456fb24 4.61MB / 4.61MB 0.7s done
#11 extracting sha256:bf7af0229701decd1b9f42143504fc8f69e5664c37e57001d198e731e4f86c2e 0.5s done
#11 DONE 9.4s

#11 [backend 1/6] FROM docker.io/library/python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
#11 extracting sha256:ab2cb3ee67af16dd0212f1564a3c1a7bfc96172b7c21c74895492bd87456fb24 0.2s done
#11 DONE 9.5s

#8 [frontend 1/5] FROM docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 20.97MB / 28.12MB 9.8s
#8 ...

#11 [backend 1/6] FROM docker.io/library/python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
#11 extracting sha256:8aff2d3a9af8ed70ae2aa065663f6a7b99d3cd41564528e8d5f039ec0faae595 0.2s done
#11 extracting sha256:3550292b2150d689c8a69849320a815d1d54883f6aecf670f098c1a16f2c5436 done
#11 DONE 9.8s

#8 [frontend 1/5] FROM docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 23.07MB / 28.12MB 10.1s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 26.21MB / 28.12MB 10.4s
#8 sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 28.12MB / 28.12MB 10.4s done
#8 extracting sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d
#8 extracting sha256:46ac7a0b9811e518f6b5a0d52940c913a1a560a8f78b82267804914e50244d2d 0.7s done
#8 DONE 11.4s

#12 [backend 2/6] RUN apt-get update -qq &&     apt-get install -y --no-install-recommends libpq-dev gcc curl &&     rm -rf /var/lib/apt/lists/*
#12 ...

#8 [frontend 1/5] FROM docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
#8 extracting sha256:93f1e44b7642d94207805933fd52fd7b5a5a684cf69b340ae3df415754a0a614 0.0s done
#8 extracting sha256:b007268d7e627275df714577a74837e42ee450306295c30b987d482c667fbedf 0.7s done
#8 DONE 12.1s

#8 [frontend 1/5] FROM docker.io/library/node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
#8 extracting sha256:791fd1b17847094616ace4f04066a269c36bb89561d5d7f1a0dba4f615e16716 0.0s done
#8 extracting sha256:ed7f19ee07f992aa9ce9fa1ca75db4ae36641464e404f6b720b4afce41cab9e4 done
#8 DONE 12.2s

#13 [frontend 2/5] WORKDIR /app
#13 DONE 0.4s

#12 [backend 2/6] RUN apt-get update -qq &&     apt-get install -y --no-install-recommends libpq-dev gcc curl &&     rm -rf /var/lib/apt/lists/*
#12 ...

#14 [frontend 3/5] COPY package*.json ./
#14 DONE 0.1s

#15 [frontend 4/5] RUN npm install
#15 ...

#12 [backend 2/6] RUN apt-get update -qq &&     apt-get install -y --no-install-recommends libpq-dev gcc curl &&     rm -rf /var/lib/apt/lists/*
#12 3.996 Reading package lists...
#12 4.483 Building dependency tree...
#12 4.581 Reading state information...
#12 4.768 The following additional packages will be installed:
#12 4.768   binutils binutils-aarch64-linux-gnu binutils-common cpp cpp-14
#12 4.768   cpp-14-aarch64-linux-gnu cpp-aarch64-linux-gnu gcc-14
#12 4.768   gcc-14-aarch64-linux-gnu gcc-aarch64-linux-gnu libasan8 libatomic1
#12 4.768   libbinutils libbrotli1 libcc1-0 libcom-err2 libctf-nobfd0 libctf0
#12 4.768   libcurl4t64 libgcc-14-dev libgnutls30t64 libgomp1 libgprofng0
#12 4.768   libgssapi-krb5-2 libhwasan0 libidn2-0 libisl23 libitm1 libjansson4
#12 4.768   libk5crypto3 libkeyutils1 libkrb5-3 libkrb5support0 libldap2 liblsan0
#12 4.768   libmpc3 libmpfr6 libnghttp2-14 libnghttp3-9 libp11-kit0 libpq5 libpsl5t64
#12 4.769   librtmp1 libsasl2-2 libsasl2-modules-db libsframe1 libssh2-1t64 libssl-dev
#12 4.769   libtasn1-6 libtsan2 libubsan1 libunistring5
#12 4.770 Suggested packages:
#12 4.770   binutils-doc gprofng-gui binutils-gold cpp-doc gcc-14-locales cpp-14-doc
#12 4.770   gcc-multilib make manpages-dev autoconf automake libtool flex bison gdb
#12 4.770   gcc-doc gcc-14-doc gdb-aarch64-linux-gnu gnutls-bin krb5-doc krb5-user
#12 4.770   postgresql-doc-17 libssl-doc
#12 4.770 Recommended packages:
#12 4.770   bash-completion libc6-dev | libc-dev libc6-dev libc-dev krb5-locales
#12 4.770   libldap-common publicsuffix libsasl2-modules
#12 5.146 The following NEW packages will be installed:
#12 5.146   binutils binutils-aarch64-linux-gnu binutils-common cpp cpp-14
#12 5.146   cpp-14-aarch64-linux-gnu cpp-aarch64-linux-gnu curl gcc gcc-14
#12 5.146   gcc-14-aarch64-linux-gnu gcc-aarch64-linux-gnu libasan8 libatomic1
#12 5.146   libbinutils libbrotli1 libcc1-0 libcom-err2 libctf-nobfd0 libctf0
#12 5.146   libcurl4t64 libgcc-14-dev libgnutls30t64 libgomp1 libgprofng0
#12 5.146   libgssapi-krb5-2 libhwasan0 libidn2-0 libisl23 libitm1 libjansson4
#12 5.146   libk5crypto3 libkeyutils1 libkrb5-3 libkrb5support0 libldap2 liblsan0
#12 5.146   libmpc3 libmpfr6 libnghttp2-14 libnghttp3-9 libp11-kit0 libpq-dev libpq5
#12 5.147   libpsl5t64 librtmp1 libsasl2-2 libsasl2-modules-db libsframe1 libssh2-1t64
#12 5.147   libssl-dev libtasn1-6 libtsan2 libubsan1 libunistring5
#12 5.230 0 upgraded, 55 newly installed, 0 to remove and 0 not upgraded.
#12 5.230 Need to get 53.6 MB of archives.
#12 5.230 After this operation, 217 MB of additional disk space will be used.
#12 5.230 Get:1 http://deb.debian.org/debian trixie/main arm64 libsframe1 arm64 2.44-3 [77.8 kB]
#12 5.250 Get:2 http://deb.debian.org/debian trixie/main arm64 binutils-common arm64 2.44-3 [2509 kB]
#12 5.363 Get:3 http://deb.debian.org/debian trixie/main arm64 libbinutils arm64 2.44-3 [660 kB]
#12 5.415 Get:4 http://deb.debian.org/debian trixie/main arm64 libgprofng0 arm64 2.44-3 [668 kB]
#12 5.464 Get:5 http://deb.debian.org/debian trixie/main arm64 libctf-nobfd0 arm64 2.44-3 [152 kB]
#12 5.479 Get:6 http://deb.debian.org/debian trixie/main arm64 libctf0 arm64 2.44-3 [84.2 kB]
#12 5.488 Get:7 http://deb.debian.org/debian trixie/main arm64 libjansson4 arm64 2.14-2+b3 [39.2 kB]
#12 5.503 Get:8 http://deb.debian.org/debian trixie/main arm64 binutils-aarch64-linux-gnu arm64 2.44-3 [820 kB]
#12 5.548 Get:9 http://deb.debian.org/debian trixie/main arm64 binutils arm64 2.44-3 [262 kB]
#12 5.577 Get:10 http://deb.debian.org/debian trixie/main arm64 libisl23 arm64 0.27-1 [601 kB]
#12 5.668 Get:11 http://deb.debian.org/debian trixie/main arm64 libmpfr6 arm64 4.2.2-1 [685 kB]
#12 5.735 Get:12 http://deb.debian.org/debian trixie/main arm64 libmpc3 arm64 1.3.1-1+b3 [50.5 kB]
#12 5.740 Get:13 http://deb.debian.org/debian trixie/main arm64 cpp-14-aarch64-linux-gnu arm64 14.2.0-19 [9169 kB]
#12 6.717 Get:14 http://deb.debian.org/debian trixie/main arm64 cpp-14 arm64 14.2.0-19 [1276 B]
#12 6.717 Get:15 http://deb.debian.org/debian trixie/main arm64 cpp-aarch64-linux-gnu arm64 4:14.2.0-1 [4832 B]
#12 6.717 Get:16 http://deb.debian.org/debian trixie/main arm64 cpp arm64 4:14.2.0-1 [1568 B]
#12 6.717 Get:17 http://deb.debian.org/debian trixie/main arm64 libbrotli1 arm64 1.1.0-2+b7 [308 kB]
#12 6.745 Get:18 http://deb.debian.org/debian trixie/main arm64 libkrb5support0 arm64 1.21.3-5+deb13u1 [32.5 kB]
#12 6.749 Get:19 http://deb.debian.org/debian trixie/main arm64 libcom-err2 arm64 1.47.2-3+b11 [24.9 kB]
#12 6.751 Get:20 http://deb.debian.org/debian trixie/main arm64 libk5crypto3 arm64 1.21.3-5+deb13u1 [81.4 kB]
#12 6.759 Get:21 http://deb.debian.org/debian trixie/main arm64 libkeyutils1 arm64 1.6.3-6 [9716 B]
#12 6.759 Get:22 http://deb.debian.org/debian trixie/main arm64 libkrb5-3 arm64 1.21.3-5+deb13u1 [308 kB]
#12 6.793 Get:23 http://deb.debian.org/debian trixie/main arm64 libgssapi-krb5-2 arm64 1.21.3-5+deb13u1 [128 kB]
#12 6.802 Get:24 http://deb.debian.org/debian trixie/main arm64 libunistring5 arm64 1.3-2 [453 kB]
#12 6.845 Get:25 http://deb.debian.org/debian trixie/main arm64 libidn2-0 arm64 2.3.8-2 [107 kB]
#12 6.855 Get:26 http://deb.debian.org/debian trixie/main arm64 libsasl2-modules-db arm64 2.1.28+dfsg1-9 [20.1 kB]
#12 6.856 Get:27 http://deb.debian.org/debian trixie/main arm64 libsasl2-2 arm64 2.1.28+dfsg1-9 [55.6 kB]
#12 6.861 Get:28 http://deb.debian.org/debian trixie/main arm64 libldap2 arm64 2.6.10+dfsg-1 [179 kB]
#12 6.877 Get:29 http://deb.debian.org/debian trixie/main arm64 libnghttp2-14 arm64 1.64.0-1.1+deb13u1 [71.6 kB]
#12 6.887 Get:30 http://deb.debian.org/debian trixie/main arm64 libnghttp3-9 arm64 1.8.0-1 [63.2 kB]
#12 6.888 Get:31 http://deb.debian.org/debian trixie/main arm64 libpsl5t64 arm64 0.21.2-1.1+b1 [57.1 kB]
#12 6.897 Get:32 http://deb.debian.org/debian trixie/main arm64 libp11-kit0 arm64 0.25.5-3 [409 kB]
#12 6.965 Get:33 http://deb.debian.org/debian trixie/main arm64 libtasn1-6 arm64 4.20.0-2+deb13u1 [47.3 kB]
#12 6.974 Get:34 http://deb.debian.org/debian trixie/main arm64 libgnutls30t64 arm64 3.8.9-3+deb13u4 [1379 kB]
#12 7.114 Get:35 http://deb.debian.org/debian trixie/main arm64 librtmp1 arm64 2.4+20151223.gitfa8646d.1-2+b5 [56.8 kB]
#12 7.133 Get:36 http://deb.debian.org/debian trixie/main arm64 libssh2-1t64 arm64 1.11.1-1+deb13u1 [236 kB]
#12 7.160 Get:37 http://deb.debian.org/debian trixie/main arm64 libcurl4t64 arm64 8.14.1-2+deb13u4 [360 kB]
#12 7.206 Get:38 http://deb.debian.org/debian trixie/main arm64 curl arm64 8.14.1-2+deb13u4 [262 kB]
#12 7.225 Get:39 http://deb.debian.org/debian trixie/main arm64 libcc1-0 arm64 14.2.0-19 [42.2 kB]
#12 7.228 Get:40 http://deb.debian.org/debian trixie/main arm64 libgomp1 arm64 14.2.0-19 [124 kB]
#12 7.237 Get:41 http://deb.debian.org/debian trixie/main arm64 libitm1 arm64 14.2.0-19 [24.2 kB]
#12 7.237 Get:42 http://deb.debian.org/debian trixie/main arm64 libatomic1 arm64 14.2.0-19 [10.1 kB]
#12 7.241 Get:43 http://deb.debian.org/debian trixie/main arm64 libasan8 arm64 14.2.0-19 [2578 kB]
#12 7.441 Get:44 http://deb.debian.org/debian trixie/main arm64 liblsan0 arm64 14.2.0-19 [1161 kB]
#12 7.535 Get:45 http://deb.debian.org/debian trixie/main arm64 libtsan2 arm64 14.2.0-19 [2383 kB]
#12 7.790 Get:46 http://deb.debian.org/debian trixie/main arm64 libubsan1 arm64 14.2.0-19 [1039 kB]
#12 7.890 Get:47 http://deb.debian.org/debian trixie/main arm64 libhwasan0 arm64 14.2.0-19 [1442 kB]
#12 8.011 Get:48 http://deb.debian.org/debian trixie/main arm64 libgcc-14-dev arm64 14.2.0-19 [2359 kB]
#12 8.242 Get:49 http://deb.debian.org/debian trixie/main arm64 gcc-14-aarch64-linux-gnu arm64 14.2.0-19 [17.7 MB]
#12 9.863 Get:50 http://deb.debian.org/debian trixie/main arm64 gcc-14 arm64 14.2.0-19 [529 kB]
#12 9.884 Get:51 http://deb.debian.org/debian trixie/main arm64 gcc-aarch64-linux-gnu arm64 4:14.2.0-1 [1440 B]
#12 9.884 Get:52 http://deb.debian.org/debian trixie/main arm64 gcc arm64 4:14.2.0-1 [5136 B]
#12 9.884 Get:53 http://deb.debian.org/debian-security trixie-security/main arm64 libpq5 arm64 17.11-0+deb13u1 [230 kB]
#12 9.900 Get:54 http://deb.debian.org/debian-security trixie-security/main arm64 libssl-dev arm64 3.5.7-1~deb13u2 [3394 kB]
#12 10.17 Get:55 http://deb.debian.org/debian-security trixie-security/main arm64 libpq-dev arm64 17.11-0+deb13u1 [156 kB]
#12 10.36 debconf: unable to initialize frontend: Dialog
#12 10.36 debconf: (TERM is not set, so the dialog frontend is not usable.)
#12 10.36 debconf: falling back to frontend: Readline
#12 10.36 debconf: unable to initialize frontend: Readline
#12 10.36 debconf: (Can't locate Term/ReadLine.pm in @INC (you may need to install the Term::ReadLine module) (@INC entries checked: /etc/perl /usr/local/lib/aarch64-linux-gnu/perl/5.40.1 /usr/local/share/perl/5.40.1 /usr/lib/aarch64-linux-gnu/perl5/5.40 /usr/share/perl5 /usr/lib/aarch64-linux-gnu/perl-base /usr/lib/aarch64-linux-gnu/perl/5.40 /usr/share/perl/5.40 /usr/local/lib/site_perl) at /usr/share/perl5/Debconf/FrontEnd/Readline.pm line 8, <STDIN> line 55.)
#12 10.36 debconf: falling back to frontend: Teletype
#12 10.36 debconf: unable to initialize frontend: Teletype
#12 10.36 debconf: (This frontend requires a controlling tty.)
#12 10.36 debconf: falling back to frontend: Noninteractive
#12 11.45 Fetched 53.6 MB in 5s (10.7 MB/s)
#12 11.46 Selecting previously unselected package libsframe1:arm64.
#12 11.46 (Reading database ... (Reading database ... 5%(Reading database ... 10%(Reading database ... 15%(Reading database ... 20%(Reading database ... 25%(Reading database ... 30%(Reading database ... 35%(Reading database ... 40%(Reading database ... 45%(Reading database ... 50%(Reading database ... 55%(Reading database ... 60%(Reading database ... 65%(Reading database ... 70%(Reading database ... 75%(Reading database ... 80%(Reading database ... 85%(Reading database ... 90%(Reading database ... 95%(Reading database ... 100%(Reading database ... 5649 files and directories currently installed.)
#12 11.46 Preparing to unpack .../00-libsframe1_2.44-3_arm64.deb ...
#12 11.47 Unpacking libsframe1:arm64 (2.44-3) ...
#12 11.48 Selecting previously unselected package binutils-common:arm64.
#12 11.48 Preparing to unpack .../01-binutils-common_2.44-3_arm64.deb ...
#12 11.49 Unpacking binutils-common:arm64 (2.44-3) ...
#12 11.64 Selecting previously unselected package libbinutils:arm64.
#12 11.64 Preparing to unpack .../02-libbinutils_2.44-3_arm64.deb ...
#12 11.64 Unpacking libbinutils:arm64 (2.44-3) ...
#12 11.71 Selecting previously unselected package libgprofng0:arm64.
#12 11.71 Preparing to unpack .../03-libgprofng0_2.44-3_arm64.deb ...
#12 11.71 Unpacking libgprofng0:arm64 (2.44-3) ...
#12 11.76 Selecting previously unselected package libctf-nobfd0:arm64.
#12 11.76 Preparing to unpack .../04-libctf-nobfd0_2.44-3_arm64.deb ...
#12 11.76 Unpacking libctf-nobfd0:arm64 (2.44-3) ...
#12 11.78 Selecting previously unselected package libctf0:arm64.
#12 11.78 Preparing to unpack .../05-libctf0_2.44-3_arm64.deb ...
#12 11.78 Unpacking libctf0:arm64 (2.44-3) ...
#12 11.79 Selecting previously unselected package libjansson4:arm64.
#12 11.80 Preparing to unpack .../06-libjansson4_2.14-2+b3_arm64.deb ...
#12 11.80 Unpacking libjansson4:arm64 (2.14-2+b3) ...
#12 11.81 Selecting previously unselected package binutils-aarch64-linux-gnu.
#12 11.81 Preparing to unpack .../07-binutils-aarch64-linux-gnu_2.44-3_arm64.deb ...
#12 11.81 Unpacking binutils-aarch64-linux-gnu (2.44-3) ...
#12 11.91 Selecting previously unselected package binutils.
#12 11.91 Preparing to unpack .../08-binutils_2.44-3_arm64.deb ...
#12 11.91 Unpacking binutils (2.44-3) ...
#12 11.94 Selecting previously unselected package libisl23:arm64.
#12 11.94 Preparing to unpack .../09-libisl23_0.27-1_arm64.deb ...
#12 11.94 Unpacking libisl23:arm64 (0.27-1) ...
#12 11.99 Selecting previously unselected package libmpfr6:arm64.
#12 11.99 Preparing to unpack .../10-libmpfr6_4.2.2-1_arm64.deb ...
#12 11.99 Unpacking libmpfr6:arm64 (4.2.2-1) ...
#12 12.03 Selecting previously unselected package libmpc3:arm64.
#12 12.03 Preparing to unpack .../11-libmpc3_1.3.1-1+b3_arm64.deb ...
#12 12.03 Unpacking libmpc3:arm64 (1.3.1-1+b3) ...
#12 12.04 Selecting previously unselected package cpp-14-aarch64-linux-gnu.
#12 12.04 Preparing to unpack .../12-cpp-14-aarch64-linux-gnu_14.2.0-19_arm64.deb ...
#12 12.04 Unpacking cpp-14-aarch64-linux-gnu (14.2.0-19) ...
#12 12.47 Selecting previously unselected package cpp-14.
#12 12.47 Preparing to unpack .../13-cpp-14_14.2.0-19_arm64.deb ...
#12 12.47 Unpacking cpp-14 (14.2.0-19) ...
#12 12.48 Selecting previously unselected package cpp-aarch64-linux-gnu.
#12 12.48 Preparing to unpack .../14-cpp-aarch64-linux-gnu_4%3a14.2.0-1_arm64.deb ...
#12 12.48 Unpacking cpp-aarch64-linux-gnu (4:14.2.0-1) ...
#12 12.49 Selecting previously unselected package cpp.
#12 12.50 Preparing to unpack .../15-cpp_4%3a14.2.0-1_arm64.deb ...
#12 12.50 Unpacking cpp (4:14.2.0-1) ...
#12 12.51 Selecting previously unselected package libbrotli1:arm64.
#12 12.51 Preparing to unpack .../16-libbrotli1_1.1.0-2+b7_arm64.deb ...
#12 12.51 Unpacking libbrotli1:arm64 (1.1.0-2+b7) ...
#12 12.55 Selecting previously unselected package libkrb5support0:arm64.
#12 12.55 Preparing to unpack .../17-libkrb5support0_1.21.3-5+deb13u1_arm64.deb ...
#12 12.55 Unpacking libkrb5support0:arm64 (1.21.3-5+deb13u1) ...
#12 12.56 Selecting previously unselected package libcom-err2:arm64.
#12 12.56 Preparing to unpack .../18-libcom-err2_1.47.2-3+b11_arm64.deb ...
#12 12.57 Unpacking libcom-err2:arm64 (1.47.2-3+b11) ...
#12 12.58 Selecting previously unselected package libk5crypto3:arm64.
#12 12.58 Preparing to unpack .../19-libk5crypto3_1.21.3-5+deb13u1_arm64.deb ...
#12 12.58 Unpacking libk5crypto3:arm64 (1.21.3-5+deb13u1) ...
#12 12.60 Selecting previously unselected package libkeyutils1:arm64.
#12 12.60 Preparing to unpack .../20-libkeyutils1_1.6.3-6_arm64.deb ...
#12 12.60 Unpacking libkeyutils1:arm64 (1.6.3-6) ...
#12 12.62 Selecting previously unselected package libkrb5-3:arm64.
#12 12.62 Preparing to unpack .../21-libkrb5-3_1.21.3-5+deb13u1_arm64.deb ...
#12 12.62 Unpacking libkrb5-3:arm64 (1.21.3-5+deb13u1) ...
#12 12.65 Selecting previously unselected package libgssapi-krb5-2:arm64.
#12 12.65 Preparing to unpack .../22-libgssapi-krb5-2_1.21.3-5+deb13u1_arm64.deb ...
#12 12.66 Unpacking libgssapi-krb5-2:arm64 (1.21.3-5+deb13u1) ...
#12 12.68 Selecting previously unselected package libunistring5:arm64.
#12 12.68 Preparing to unpack .../23-libunistring5_1.3-2_arm64.deb ...
#12 12.68 Unpacking libunistring5:arm64 (1.3-2) ...
#12 12.72 Selecting previously unselected package libidn2-0:arm64.
#12 12.73 Preparing to unpack .../24-libidn2-0_2.3.8-2_arm64.deb ...
#12 12.73 Unpacking libidn2-0:arm64 (2.3.8-2) ...
#12 12.74 Selecting previously unselected package libsasl2-modules-db:arm64.
#12 12.74 Preparing to unpack .../25-libsasl2-modules-db_2.1.28+dfsg1-9_arm64.deb ...
#12 12.75 Unpacking libsasl2-modules-db:arm64 (2.1.28+dfsg1-9) ...
#12 12.76 Selecting previously unselected package libsasl2-2:arm64.
#12 12.76 Preparing to unpack .../26-libsasl2-2_2.1.28+dfsg1-9_arm64.deb ...
#12 12.76 Unpacking libsasl2-2:arm64 (2.1.28+dfsg1-9) ...
#12 12.77 Selecting previously unselected package libldap2:arm64.
#12 12.77 Preparing to unpack .../27-libldap2_2.6.10+dfsg-1_arm64.deb ...
#12 12.77 Unpacking libldap2:arm64 (2.6.10+dfsg-1) ...
#12 12.79 Selecting previously unselected package libnghttp2-14:arm64.
#12 12.80 Preparing to unpack .../28-libnghttp2-14_1.64.0-1.1+deb13u1_arm64.deb ...
#12 12.80 Unpacking libnghttp2-14:arm64 (1.64.0-1.1+deb13u1) ...
#12 12.81 Selecting previously unselected package libnghttp3-9:arm64.
#12 12.81 Preparing to unpack .../29-libnghttp3-9_1.8.0-1_arm64.deb ...
#12 12.81 Unpacking libnghttp3-9:arm64 (1.8.0-1) ...
#12 12.82 Selecting previously unselected package libpsl5t64:arm64.
#12 12.83 Preparing to unpack .../30-libpsl5t64_0.21.2-1.1+b1_arm64.deb ...
#12 12.83 Unpacking libpsl5t64:arm64 (0.21.2-1.1+b1) ...
#12 12.84 Selecting previously unselected package libp11-kit0:arm64.
#12 12.84 Preparing to unpack .../31-libp11-kit0_0.25.5-3_arm64.deb ...
#12 12.84 Unpacking libp11-kit0:arm64 (0.25.5-3) ...
#12 12.87 Selecting previously unselected package libtasn1-6:arm64.
#12 12.88 Preparing to unpack .../32-libtasn1-6_4.20.0-2+deb13u1_arm64.deb ...
#12 12.88 Unpacking libtasn1-6:arm64 (4.20.0-2+deb13u1) ...
#12 12.89 Selecting previously unselected package libgnutls30t64:arm64.
#12 12.89 Preparing to unpack .../33-libgnutls30t64_3.8.9-3+deb13u4_arm64.deb ...
#12 12.89 Unpacking libgnutls30t64:arm64 (3.8.9-3+deb13u4) ...
#12 12.95 Selecting previously unselected package librtmp1:arm64.
#12 12.96 Preparing to unpack .../34-librtmp1_2.4+20151223.gitfa8646d.1-2+b5_arm64.deb ...
#12 12.96 Unpacking librtmp1:arm64 (2.4+20151223.gitfa8646d.1-2+b5) ...
#12 12.97 Selecting previously unselected package libssh2-1t64:arm64.
#12 12.97 Preparing to unpack .../35-libssh2-1t64_1.11.1-1+deb13u1_arm64.deb ...
#12 12.97 Unpacking libssh2-1t64:arm64 (1.11.1-1+deb13u1) ...
#12 12.99 Selecting previously unselected package libcurl4t64:arm64.
#12 12.99 Preparing to unpack .../36-libcurl4t64_8.14.1-2+deb13u4_arm64.deb ...
#12 12.99 Unpacking libcurl4t64:arm64 (8.14.1-2+deb13u4) ...
#12 13.02 Selecting previously unselected package curl.
#12 13.02 Preparing to unpack .../37-curl_8.14.1-2+deb13u4_arm64.deb ...
#12 13.02 Unpacking curl (8.14.1-2+deb13u4) ...
#12 13.05 Selecting previously unselected package libcc1-0:arm64.
#12 13.05 Preparing to unpack .../38-libcc1-0_14.2.0-19_arm64.deb ...
#12 13.05 Unpacking libcc1-0:arm64 (14.2.0-19) ...
#12 13.06 Selecting previously unselected package libgomp1:arm64.
#12 13.06 Preparing to unpack .../39-libgomp1_14.2.0-19_arm64.deb ...
#12 13.06 Unpacking libgomp1:arm64 (14.2.0-19) ...
#12 13.08 Selecting previously unselected package libitm1:arm64.
#12 13.08 Preparing to unpack .../40-libitm1_14.2.0-19_arm64.deb ...
#12 13.08 Unpacking libitm1:arm64 (14.2.0-19) ...
#12 13.09 Selecting previously unselected package libatomic1:arm64.
#12 13.10 Preparing to unpack .../41-libatomic1_14.2.0-19_arm64.deb ...
#12 13.10 Unpacking libatomic1:arm64 (14.2.0-19) ...
#12 13.11 Selecting previously unselected package libasan8:arm64.
#12 13.11 Preparing to unpack .../42-libasan8_14.2.0-19_arm64.deb ...
#12 13.11 Unpacking libasan8:arm64 (14.2.0-19) ...
#12 13.26 Selecting previously unselected package liblsan0:arm64.
#12 13.26 Preparing to unpack .../43-liblsan0_14.2.0-19_arm64.deb ...
#12 13.26 Unpacking liblsan0:arm64 (14.2.0-19) ...
#12 13.34 Selecting previously unselected package libtsan2:arm64.
#12 13.34 Preparing to unpack .../44-libtsan2_14.2.0-19_arm64.deb ...
#12 13.34 Unpacking libtsan2:arm64 (14.2.0-19) ...
#12 13.48 Selecting previously unselected package libubsan1:arm64.
#12 13.48 Preparing to unpack .../45-libubsan1_14.2.0-19_arm64.deb ...
#12 13.48 Unpacking libubsan1:arm64 (14.2.0-19) ...
#12 13.54 Selecting previously unselected package libhwasan0:arm64.
#12 13.54 Preparing to unpack .../46-libhwasan0_14.2.0-19_arm64.deb ...
#12 13.55 Unpacking libhwasan0:arm64 (14.2.0-19) ...
#12 13.64 Selecting previously unselected package libgcc-14-dev:arm64.
#12 13.64 Preparing to unpack .../47-libgcc-14-dev_14.2.0-19_arm64.deb ...
#12 13.64 Unpacking libgcc-14-dev:arm64 (14.2.0-19) ...
#12 13.95 Selecting previously unselected package gcc-14-aarch64-linux-gnu.
#12 13.95 Preparing to unpack .../48-gcc-14-aarch64-linux-gnu_14.2.0-19_arm64.deb ...
#12 13.95 Unpacking gcc-14-aarch64-linux-gnu (14.2.0-19) ...
#12 14.48 Selecting previously unselected package gcc-14.
#12 14.48 Preparing to unpack .../49-gcc-14_14.2.0-19_arm64.deb ...
#12 14.48 Unpacking gcc-14 (14.2.0-19) ...
#12 14.51 Selecting previously unselected package gcc-aarch64-linux-gnu.
#12 14.51 Preparing to unpack .../50-gcc-aarch64-linux-gnu_4%3a14.2.0-1_arm64.deb ...
#12 14.51 Unpacking gcc-aarch64-linux-gnu (4:14.2.0-1) ...
#12 14.52 Selecting previously unselected package gcc.
#12 14.52 Preparing to unpack .../51-gcc_4%3a14.2.0-1_arm64.deb ...
#12 14.52 Unpacking gcc (4:14.2.0-1) ...
#12 14.53 Selecting previously unselected package libpq5:arm64.
#12 14.53 Preparing to unpack .../52-libpq5_17.11-0+deb13u1_arm64.deb ...
#12 14.53 Unpacking libpq5:arm64 (17.11-0+deb13u1) ...
#12 14.56 Selecting previously unselected package libssl-dev:arm64.
#12 14.56 Preparing to unpack .../53-libssl-dev_3.5.7-1~deb13u2_arm64.deb ...
#12 14.56 Unpacking libssl-dev:arm64 (3.5.7-1~deb13u2) ...
#12 14.72 Selecting previously unselected package libpq-dev.
#12 14.72 Preparing to unpack .../54-libpq-dev_17.11-0+deb13u1_arm64.deb ...
#12 14.72 Unpacking libpq-dev (17.11-0+deb13u1) ...
#12 14.74 Setting up libkeyutils1:arm64 (1.6.3-6) ...
#12 14.75 Setting up libbrotli1:arm64 (1.1.0-2+b7) ...
#12 14.75 Setting up binutils-common:arm64 (2.44-3) ...
#12 14.75 Setting up libnghttp2-14:arm64 (1.64.0-1.1+deb13u1) ...
#12 14.75 Setting up libctf-nobfd0:arm64 (2.44-3) ...
#12 14.76 Setting up libcom-err2:arm64 (1.47.2-3+b11) ...
#12 14.76 Setting up libgomp1:arm64 (14.2.0-19) ...
#12 14.76 Setting up libsframe1:arm64 (2.44-3) ...
#12 14.76 Setting up libjansson4:arm64 (2.14-2+b3) ...
#12 14.76 Setting up libkrb5support0:arm64 (1.21.3-5+deb13u1) ...
#12 14.77 Setting up libsasl2-modules-db:arm64 (2.1.28+dfsg1-9) ...
#12 14.77 Setting up libmpfr6:arm64 (4.2.2-1) ...
#12 14.77 Setting up libp11-kit0:arm64 (0.25.5-3) ...
#12 14.77 Setting up libunistring5:arm64 (1.3-2) ...
#12 14.78 Setting up libssl-dev:arm64 (3.5.7-1~deb13u2) ...
#12 14.78 Setting up libmpc3:arm64 (1.3.1-1+b3) ...
#12 14.78 Setting up libatomic1:arm64 (14.2.0-19) ...
#12 14.78 Setting up libk5crypto3:arm64 (1.21.3-5+deb13u1) ...
#12 14.78 Setting up libsasl2-2:arm64 (2.1.28+dfsg1-9) ...
#12 14.79 Setting up libnghttp3-9:arm64 (1.8.0-1) ...
#12 14.79 Setting up libubsan1:arm64 (14.2.0-19) ...
#12 14.79 Setting up libhwasan0:arm64 (14.2.0-19) ...
#12 14.79 Setting up libasan8:arm64 (14.2.0-19) ...
#12 14.80 Setting up libtasn1-6:arm64 (4.20.0-2+deb13u1) ...
#12 14.80 Setting up libkrb5-3:arm64 (1.21.3-5+deb13u1) ...
#12 14.80 Setting up libssh2-1t64:arm64 (1.11.1-1+deb13u1) ...
#12 14.80 Setting up libtsan2:arm64 (14.2.0-19) ...
#12 14.80 Setting up libbinutils:arm64 (2.44-3) ...
#12 14.81 Setting up libisl23:arm64 (0.27-1) ...
#12 14.81 Setting up libcc1-0:arm64 (14.2.0-19) ...
#12 14.81 Setting up libldap2:arm64 (2.6.10+dfsg-1) ...
#12 14.82 Setting up liblsan0:arm64 (14.2.0-19) ...
#12 14.82 Setting up libitm1:arm64 (14.2.0-19) ...
#12 14.82 Setting up libctf0:arm64 (2.44-3) ...
#12 14.82 Setting up binutils-aarch64-linux-gnu (2.44-3) ...
#12 14.82 Setting up libidn2-0:arm64 (2.3.8-2) ...
#12 14.83 Setting up libgprofng0:arm64 (2.44-3) ...
#12 14.83 Setting up libgssapi-krb5-2:arm64 (1.21.3-5+deb13u1) ...
#12 14.83 Setting up cpp-14-aarch64-linux-gnu (14.2.0-19) ...
#12 14.84 Setting up libgcc-14-dev:arm64 (14.2.0-19) ...
#12 14.84 Setting up libgnutls30t64:arm64 (3.8.9-3+deb13u4) ...
#12 14.84 Setting up libpsl5t64:arm64 (0.21.2-1.1+b1) ...
#12 14.84 Setting up libpq5:arm64 (17.11-0+deb13u1) ...
#12 14.85 Setting up libpq-dev (17.11-0+deb13u1) ...
#12 14.85 Setting up binutils (2.44-3) ...
#12 14.85 Setting up cpp-aarch64-linux-gnu (4:14.2.0-1) ...
#12 14.85 Setting up librtmp1:arm64 (2.4+20151223.gitfa8646d.1-2+b5) ...
#12 14.86 Setting up cpp-14 (14.2.0-19) ...
#12 14.86 Setting up cpp (4:14.2.0-1) ...
#12 14.86 Setting up gcc-14-aarch64-linux-gnu (14.2.0-19) ...
#12 14.87 Setting up gcc-aarch64-linux-gnu (4:14.2.0-1) ...
#12 14.87 Setting up libcurl4t64:arm64 (8.14.1-2+deb13u4) ...
#12 14.87 Setting up gcc-14 (14.2.0-19) ...
#12 14.87 Setting up curl (8.14.1-2+deb13u4) ...
#12 14.88 Setting up gcc (4:14.2.0-1) ...
#12 14.88 Processing triggers for libc-bin (2.41-12+deb13u3) ...
#12 DONE 15.3s

#15 [frontend 4/5] RUN npm install
#15 ...

#16 [backend 3/6] WORKDIR /app
#16 DONE 0.0s

#17 [backend 4/6] COPY requirements.txt .
#17 DONE 0.0s

#18 [backend 5/6] RUN pip install --no-cache-dir -r requirements.txt
#18 1.314 Collecting django<6.0,>=5.0 (from -r requirements.txt (line 1))
#18 1.372   Downloading django-5.2.17-py3-none-any.whl.metadata (4.1 kB)
#18 1.399 Collecting djangorestframework<4.0,>=3.15 (from -r requirements.txt (line 2))
#18 1.408   Downloading djangorestframework-3.18.1-py3-none-any.whl.metadata (7.8 kB)
#18 1.711 Collecting djangorestframework-simplejwt<6.0,>=5.3 (from -r requirements.txt (line 3))
#18 1.725   Downloading djangorestframework_simplejwt-5.5.1-py3-none-any.whl.metadata (4.6 kB)
#18 1.756 Collecting django-cors-headers<5.0,>=4.3 (from -r requirements.txt (line 4))
#18 1.768   Downloading django_cors_headers-4.9.0-py3-none-any.whl.metadata (16 kB)
#18 1.839 Collecting psycopg2-binary<3.0,>=2.9 (from -r requirements.txt (line 5))
#18 1.850   Downloading psycopg2_binary-2.9.13-cp312-cp312-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl.metadata (4.9 kB)
#18 2.127 Collecting pyairtable<3.0,>=2.3 (from -r requirements.txt (line 6))
#18 2.139   Downloading pyairtable-2.3.7-py2.py3-none-any.whl.metadata (4.5 kB)
#18 2.433 Collecting pytest-django<5.0,>=4.8 (from -r requirements.txt (line 7))
#18 2.442   Downloading pytest_django-4.14.0-py3-none-any.whl.metadata (8.1 kB)
#18 2.479 Collecting pytest<9.0,>=8.0 (from -r requirements.txt (line 8))
#18 2.489   Downloading pytest-8.4.2-py3-none-any.whl.metadata (7.7 kB)
#18 2.507 Collecting asgiref>=3.8.1 (from django<6.0,>=5.0->-r requirements.txt (line 1))
#18 2.514   Downloading asgiref-3.12.1-py3-none-any.whl.metadata (9.4 kB)
#18 2.528 Collecting sqlparse>=0.3.1 (from django<6.0,>=5.0->-r requirements.txt (line 1))
#18 2.538   Downloading sqlparse-0.6.0-py3-none-any.whl.metadata (6.0 kB)
#18 2.583 Collecting pyjwt>=1.7.1 (from djangorestframework-simplejwt<6.0,>=5.3->-r requirements.txt (line 3))
#18 2.592   Downloading pyjwt-2.13.0-py3-none-any.whl.metadata (3.4 kB)
#18 2.608 Collecting inflection (from pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 2.621   Downloading inflection-0.5.1-py2.py3-none-any.whl.metadata (1.7 kB)
#18 2.686 Collecting pydantic (from pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 2.696   Downloading pydantic-2.13.5-py3-none-any.whl.metadata (110 kB)
#18 2.731 Collecting requests>=2.22.0 (from pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 2.741   Downloading requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
#18 2.756 Collecting typing-extensions (from pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 2.765   Downloading typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
#18 2.785 Collecting urllib3>=1.26 (from pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 2.792   Downloading urllib3-2.7.0-py3-none-any.whl.metadata (6.9 kB)
#18 2.811 Collecting iniconfig>=1 (from pytest<9.0,>=8.0->-r requirements.txt (line 8))
#18 2.818   Downloading iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
#18 2.832 Collecting packaging>=20 (from pytest<9.0,>=8.0->-r requirements.txt (line 8))
#18 2.841   Downloading packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
#18 2.853 Collecting pluggy<2,>=1.5 (from pytest<9.0,>=8.0->-r requirements.txt (line 8))
#18 2.860   Downloading pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
#18 2.877 Collecting pygments>=2.7.2 (from pytest<9.0,>=8.0->-r requirements.txt (line 8))
#18 2.884   Downloading pygments-2.21.0-py3-none-any.whl.metadata (2.5 kB)
#18 2.957 Collecting charset_normalizer<4,>=2 (from requests>=2.22.0->pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 2.966   Downloading charset_normalizer-3.5.1-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl.metadata (45 kB)
#18 2.987 Collecting idna<4,>=2.5 (from requests>=2.22.0->pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 2.995   Downloading idna-3.19-py3-none-any.whl.metadata (9.2 kB)
#18 3.018 Collecting certifi>=2023.5.7 (from requests>=2.22.0->pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 3.026   Downloading certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
#18 3.039 Collecting annotated-types>=0.6.0 (from pydantic->pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 3.050   Downloading annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
#18 3.421 Collecting pydantic-core==2.46.5 (from pydantic->pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 3.431   Downloading pydantic_core-2.46.5-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (6.6 kB)
#18 3.444 Collecting typing-inspection>=0.4.2 (from pydantic->pyairtable<3.0,>=2.3->-r requirements.txt (line 6))
#18 3.450   Downloading typing_inspection-0.4.4-py3-none-any.whl.metadata (2.6 kB)
#18 3.467 Downloading django-5.2.17-py3-none-any.whl (8.3 MB)
#18 4.030    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.3/8.3 MB 14.7 MB/s eta 0:00:00
#18 4.044 Downloading djangorestframework-3.18.1-py3-none-any.whl (901 kB)
#18 4.104    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 901.4/901.4 kB 16.1 MB/s eta 0:00:00
#18 4.116 Downloading djangorestframework_simplejwt-5.5.1-py3-none-any.whl (107 kB)
#18 4.129 Downloading django_cors_headers-4.9.0-py3-none-any.whl (12 kB)
#18 4.136 Downloading psycopg2_binary-2.9.13-cp312-cp312-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl (5.9 MB)
#18 4.588    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.9/5.9 MB 13.0 MB/s eta 0:00:00
#18 4.597 Downloading pyairtable-2.3.7-py2.py3-none-any.whl (68 kB)
#18 4.612 Downloading pytest_django-4.14.0-py3-none-any.whl (27 kB)
#18 4.621 Downloading pytest-8.4.2-py3-none-any.whl (365 kB)
#18 4.666 Downloading asgiref-3.12.1-py3-none-any.whl (25 kB)
#18 4.675 Downloading iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
#18 4.686 Downloading packaging-26.3-py3-none-any.whl (129 kB)
#18 4.704 Downloading pluggy-1.6.0-py3-none-any.whl (20 kB)
#18 4.714 Downloading pygments-2.21.0-py3-none-any.whl (1.3 MB)
#18 4.822    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 12.5 MB/s eta 0:00:00
#18 4.836 Downloading pyjwt-2.13.0-py3-none-any.whl (31 kB)
#18 4.844 Downloading requests-2.34.2-py3-none-any.whl (73 kB)
#18 4.858 Downloading sqlparse-0.6.0-py3-none-any.whl (50 kB)
#18 4.870 Downloading urllib3-2.7.0-py3-none-any.whl (131 kB)
#18 4.887 Downloading inflection-0.5.1-py2.py3-none-any.whl (9.5 kB)
#18 4.898 Downloading pydantic-2.13.5-py3-none-any.whl (472 kB)
#18 4.946 Downloading pydantic_core-2.46.5-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (2.0 MB)
#18 5.088    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 13.9 MB/s eta 0:00:00
#18 5.098 Downloading typing_extensions-4.16.0-py3-none-any.whl (45 kB)
#18 5.112 Downloading annotated_types-0.8.0-py3-none-any.whl (13 kB)
#18 5.123 Downloading certifi-2026.7.22-py3-none-any.whl (136 kB)
#18 5.136 Downloading charset_normalizer-3.5.1-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (238 kB)
#18 5.159 Downloading idna-3.19-py3-none-any.whl (68 kB)
#18 5.170 Downloading typing_inspection-0.4.4-py3-none-any.whl (14 kB)
#18 5.271 Installing collected packages: urllib3, typing-extensions, sqlparse, pyjwt, pygments, psycopg2-binary, pluggy, packaging, iniconfig, inflection, idna, charset_normalizer, certifi, asgiref, annotated-types, typing-inspection, requests, pytest, pydantic-core, django, pytest-django, pydantic, djangorestframework, django-cors-headers, pyairtable, djangorestframework-simplejwt
#18 8.141 Successfully installed annotated-types-0.8.0 asgiref-3.12.1 certifi-2026.7.22 charset_normalizer-3.5.1 django-5.2.17 django-cors-headers-4.9.0 djangorestframework-3.18.1 djangorestframework-simplejwt-5.5.1 idna-3.19 inflection-0.5.1 iniconfig-2.3.0 packaging-26.3 pluggy-1.6.0 psycopg2-binary-2.9.13 pyairtable-2.3.7 pydantic-2.13.5 pydantic-core-2.46.5 pygments-2.21.0 pyjwt-2.13.0 pytest-8.4.2 pytest-django-4.14.0 requests-2.34.2 sqlparse-0.6.0 typing-extensions-4.16.0 typing-inspection-0.4.4 urllib3-2.7.0
#18 8.141 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#18 8.226 
#18 8.226 [notice] A new release of pip is available: 25.0.1 -> 26.2.1
#18 8.226 [notice] To update, run: pip install --upgrade pip
#18 DONE 8.5s

#15 [frontend 4/5] RUN npm install
#15 ...

#19 [backend 6/6] COPY . .
#19 DONE 0.1s

#20 [backend] exporting to image
#20 exporting layers
#20 exporting layers 5.4s done
#20 exporting manifest sha256:c11f586e2d787f0f76a94c6679ce2a732bbbb0e2c6ffa3108e3751c7a3ab4cbc done
#20 exporting config sha256:101fda3f9a86e17db5ddf49350374b4dd50a76e301a7276a416972235723469d done
#20 exporting attestation manifest sha256:7d9e3e71a6d06a0285c8dd89f70883eb5e4f3f3961e18a396fe06230a4abc571 0.0s done
#20 exporting manifest list sha256:d67a86cc396aa17e64eece707faa30e46bc5bb749fdcc3edf98ab0dec9495279 done
#20 naming to docker.io/library/q-taskboard-backend:latest done
#20 unpacking to docker.io/library/q-taskboard-backend:latest
#20 ...

#15 [frontend 4/5] RUN npm install
#15 27.16 npm warn deprecated whatwg-encoding@3.1.1: Use @exodus/bytes instead for a more spec-conformant and faster implementation
#15 ...

#20 [backend] exporting to image
#20 unpacking to docker.io/library/q-taskboard-backend:latest 2.9s done
#20 DONE 8.4s

#21 [backend] resolving provenance for metadata file
#21 DONE 0.1s

#15 [frontend 4/5] RUN npm install
#15 30.62 
#15 30.62 added 243 packages, and audited 244 packages in 30s
#15 30.62 
#15 30.62 48 packages are looking for funding
#15 30.62   run `npm fund` for details
#15 30.66 
#15 30.66 7 vulnerabilities (5 moderate, 1 high, 1 critical)
#15 30.66 
#15 30.66 To address all issues (including breaking changes), run:
#15 30.66   npm audit fix --force
#15 30.66 
#15 30.66 Run `npm audit` for details.
#15 30.66 npm notice
#15 30.66 npm notice New major version of npm available! 10.8.2 -> 12.0.2
#15 30.66 npm notice Changelog: https://github.com/npm/cli/releases/tag/v12.0.2
#15 30.66 npm notice To update run: npm install -g npm@12.0.2
#15 30.66 npm notice
#15 DONE 31.1s

#22 [frontend 5/5] COPY . .
#22 DONE 0.1s

#23 [frontend] exporting to image
#23 exporting layers 5.9s done
#23 exporting manifest sha256:3d64d4c43e9a19463acd5de4ffb0f2ce8f18bc351bc1e6ed2ebf161dd8e86869 done
#23 exporting config sha256:f6853dfedb7abeef668aa72522782a22a324fbf84845eeb8f7a82aeaf8358cd2 done
#23 exporting attestation manifest sha256:ec904d1acba50a1d148ca18c567487b50a16486a5e3a4b73faa63f25b793398f done
#23 exporting manifest list sha256:4455404eed9e805fad269ad787fa4226a71befb22ad9e76732e7112294bd67e9 done
#23 naming to docker.io/library/q-taskboard-frontend:latest done
#23 unpacking to docker.io/library/q-taskboard-frontend:latest
#23 unpacking to docker.io/library/q-taskboard-frontend:latest 1.8s done
#23 DONE 7.7s

#24 [frontend] resolving provenance for metadata file
#24 DONE 0.0s
 Image q-taskboard-backend Built 
 Image q-taskboard-frontend Built 
 Volume q-taskboard_frontend_node_modules Creating 
 Volume q-taskboard_pgdata Creating 
 Network q-taskboard_default Creating 
 Volume q-taskboard_frontend_node_modules Creating 
 Network q-taskboard_default Creating 
 Volume q-taskboard_pgdata Creating 
 Volume q-taskboard_frontend_node_modules Created 
 Volume q-taskboard_frontend_node_modules Created 
 Volume q-taskboard_pgdata Created 
 Volume q-taskboard_pgdata Created 
 Network q-taskboard_default Created 
 Network q-taskboard_default Created 
 Container q-taskboard-db-1 Creating 
 Container q-taskboard-db-1 Created 
 Container q-taskboard-backend-1 Creating 
 Container q-taskboard-backend-1 Created 
 Container q-taskboard-frontend-1 Creating 
 Container q-taskboard-frontend-1 Created 
 Container q-taskboard-db-1 Starting 
 Container q-taskboard-db-1 Started 
 Container q-taskboard-backend-1 Starting 
 Container q-taskboard-backend-1 Started 
 Container q-taskboard-frontend-1 Starting 
 Container q-taskboard-frontend-1 Started 
[exit 0]

$ docker compose ps
NAME                     IMAGE                  COMMAND                  SERVICE    CREATED          STATUS         PORTS
q-taskboard-backend-1    q-taskboard-backend    "python manage.py ru…"   backend    10 seconds ago   Up 3 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
q-taskboard-db-1         postgres:16-alpine     "docker-entrypoint.s…"   db         10 seconds ago   Up 8 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
q-taskboard-frontend-1   q-taskboard-frontend   "docker-entrypoint.s…"   frontend   10 seconds ago   Up 3 seconds   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
[exit 0]

$ docker compose logs --tail=20 db backend frontend
backend-1   | Watching for file changes with StatReloader
db-1        | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
db-1        | 
db-1        | waiting for server to shut down....2026-09-11 11:30:36.374 UTC [41] LOG:  received fast shutdown request
db-1        | 2026-09-11 11:30:36.375 UTC [41] LOG:  aborting any active transactions
db-1        | 2026-09-11 11:30:36.376 UTC [41] LOG:  background worker "logical replication launcher" (PID 47) exited with exit code 1
frontend-1  | 
frontend-1  | > taskboard-frontend@1.0.0 dev
frontend-1  | > vite --host 0.0.0.0 --port 3000
frontend-1  | 
frontend-1  | [33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m
frontend-1  | 
frontend-1  |   VITE v5.4.21  ready in 339 ms
frontend-1  | 
frontend-1  |   ➜  Local:   http://localhost:3000/
frontend-1  |   ➜  Network: http://172.18.0.4:3000/
frontend-1  | (node:19) [MODULE_TYPELESS_PACKAGE_JSON] Warning: Module type of file:///app/postcss.config.js is not specified and it doesn't parse as CommonJS.
frontend-1  | Reparsing as ES module because module syntax was detected. This incurs a performance overhead.
frontend-1  | To eliminate this warning, add "type": "module" to /app/package.json.
frontend-1  | (Use `node --trace-warnings ...` to show where the warning was created)
db-1        | 2026-09-11 11:30:36.376 UTC [42] LOG:  shutting down
db-1        | 2026-09-11 11:30:36.377 UTC [42] LOG:  checkpoint starting: shutdown immediate
db-1        | 2026-09-11 11:30:36.426 UTC [42] LOG:  checkpoint complete: wrote 926 buffers (5.7%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.032 s, sync=0.017 s, total=0.051 s; sync files=301, longest=0.005 s, average=0.001 s; distance=4283 kB, estimate=4283 kB; lsn=0/1925D20, redo lsn=0/1925D20
db-1        | 2026-09-11 11:30:36.432 UTC [41] LOG:  database system is shut down
db-1        |  done
db-1        | server stopped
db-1        | 
db-1        | PostgreSQL init process complete; ready for start up.
db-1        | 
db-1        | 2026-09-11 11:30:36.490 UTC [1] LOG:  starting PostgreSQL 16.15 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
db-1        | 2026-09-11 11:30:36.491 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1        | 2026-09-11 11:30:36.491 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1        | 2026-09-11 11:30:36.493 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1        | 2026-09-11 11:30:36.496 UTC [57] LOG:  database system was shut down at 2026-09-11 11:30:36 UTC
db-1        | 2026-09-11 11:30:36.499 UTC [1] LOG:  database system is ready to accept connections
[exit 0]

$ docker compose exec backend python manage.py migrate
Operations to perform:
  Apply all migrations: auth, contenttypes, projects, users
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying users.0001_initial... OK
  Applying projects.0001_initial... OK
[exit 0]

$ docker compose exec backend python manage.py seed
seeding...
seed complete.
login with any of these (password: password123):
  meera@taskboard.dev   — admin on Q3 Launch, Internal Tools
  arjun@taskboard.dev   — admin on Onboarding, member on Q3 Launch
  kavya@example.com     — member on Q3 Launch
  dev@example.com       — viewer on Q3 Launch
  lina@example.com      — member on Onboarding
[exit 0]

$ curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"meera@taskboard.dev","password":"password123"}' | python3 -c 'import sys,json; d=json.load(sys.stdin); print({k:(v[:20]+"..." if isinstance(v,str) and len(v)>40 else v) for k,v in d.items()})'
{'user': {'id': '0928bfa4-39e9-42a8-a60c-c4edae58f9e0', 'email': 'meera@taskboard.dev', 'name': 'Meera Iyer'}, 'token': 'eyJhbGciOiJIUzI1NiIs...'}
[exit 0]

$ curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/projects | python3 -m json.tool
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid"
        }
    ]
}
[exit 0]

$ curl -s -o /dev/null -w 'frontend HTTP %{http_code}
' http://localhost:3000/
frontend HTTP 200
[exit 0]

$ curl -s http://localhost:3000/ | head -15
<!DOCTYPE html>
<html lang="en">
  <head>
    <script type="module">import { injectIntoGlobalHook } from "/@react-refresh";
injectIntoGlobalHook(window);
window.$RefreshReg$ = () => {};
window.$RefreshSig$ = () => (type) => type;</script>

    <script type="module" src="/@vite/client"></script>

    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TaskBoard</title>
  </head>
  <body>
[exit 0]

$ curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/projects | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps([{"id":p["id"],"name":p["name"]} for p in (d if isinstance(d,list) else d.get("results",d))], indent=2))'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
TypeError: string indices must be integers, not 'str'
[exit 1]

$ docker compose exec db psql -U taskboard -d taskboard -c 'select (select count(*) from users_user) as users, (select count(*) from projects_project) as projects, (select count(*) from projects_task) as tasks;'
ERROR:  relation "users_user" does not exist
LINE 1: select (select count(*) from users_user) as users, (select c...
                                     ^
[exit 1]

$ curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/projects | python3 -m json.tool | head -40
{
    "projects": [
        {
            "id": "d35543dc-9350-4a2f-b1a7-05856338d6c1",
            "name": "Internal Tools Cleanup",
            "description": "Retire legacy admin tools and consolidate into the new console.",
            "role": "admin",
            "owner": {
                "id": "0928bfa4-39e9-42a8-a60c-c4edae58f9e0",
                "email": "meera@taskboard.dev",
                "name": "Meera Iyer"
            },
            "taskCount": 0,
            "createdAt": "2026-09-11T11:30:49.386165+00:00"
        },
        {
            "id": "822ec088-4e76-4a35-a79f-4657b43a3eb9",
            "name": "Customer Onboarding Revamp",
            "description": "Reduce time-to-first-value from 9 days to under 3 days.",
            "role": "member",
            "owner": {
                "id": "ad80a344-34e2-45aa-b6cf-ad6b39359273",
                "email": "arjun@taskboard.dev",
                "name": "Arjun Rao"
            },
            "taskCount": 5,
            "createdAt": "2026-09-11T11:30:49.384593+00:00"
        },
        {
            "id": "8ad55b1a-741b-42e4-bac3-62ad83f35681",
            "name": "Q3 Launch",
            "description": "Coordinate the Q3 product launch across engineering, design, and marketing.",
            "role": "admin",
            "owner": {
                "id": "0928bfa4-39e9-42a8-a60c-c4edae58f9e0",
                "email": "meera@taskboard.dev",
                "name": "Meera Iyer"
            },
            "taskCount": 7,
            "createdAt": "2026-09-11T11:30:49.380511+00:00"
[exit 0]

$ docker compose exec db psql -U taskboard -d taskboard -c '\dt'
                  List of relations
 Schema |          Name          | Type  |   Owner   
--------+------------------------+-------+-----------
 public | auth_group             | table | taskboard
 public | auth_group_permissions | table | taskboard
 public | auth_permission        | table | taskboard
 public | django_content_type    | table | taskboard
 public | django_migrations      | table | taskboard
 public | memberships            | table | taskboard
 public | projects               | table | taskboard
 public | tasks                  | table | taskboard
 public | users                  | table | taskboard
(9 rows)

[exit 0]

$ docker compose exec db psql -U taskboard -d taskboard -c 'select (select count(*) from users) as users, (select count(*) from projects) as projects, (select count(*) from memberships) as memberships, (select count(*) from tasks) as tasks;'
 users | projects | memberships | tasks 
-------+----------+-------------+-------
     5 |        3 |           8 |    12
(1 row)

[exit 0]

$ docker compose ps
NAME                     IMAGE                  COMMAND                  SERVICE    CREATED          STATUS          PORTS
q-taskboard-backend-1    q-taskboard-backend    "python manage.py ru…"   backend    42 seconds ago   Up 35 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
q-taskboard-db-1         postgres:16-alpine     "docker-entrypoint.s…"   db         42 seconds ago   Up 40 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
q-taskboard-frontend-1   q-taskboard-frontend   "docker-entrypoint.s…"   frontend   42 seconds ago   Up 35 seconds   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
[exit 0]

$ git status --short
?? CLAUDE.md
?? TERMINAL_LOG.md
[exit 0]

$ git branch --show-current
master
[exit 0]

$ git add CLAUDE.md TERMINAL_LOG.md
