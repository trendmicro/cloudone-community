# How to create a Cloud One Workload Security binary from a bash Script

## [Optional] Run the build yourself

```bash
docker build -t wsbinaryexport .
```

## Run the container to generate the binary

Replace the name for any name of your preference and replate the tenantid and token as well.

```bash
docker run --name wsbinaryexport -e TENANTID=TENANTID -e TOKEN=TOKEN ghcr.io/felipecosta09/wsbinaryexport
```

## Export the id to a variable

```bash

export CONTAINERID=(`docker ps -aqf "name=wsbinaryexport"`)
```

## Copy the binary to local folder

```bash
docker cp $CONTAINERID:/root/CloudOne .
```