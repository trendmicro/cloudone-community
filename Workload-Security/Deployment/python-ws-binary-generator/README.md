# How to create a Cloud One Workload Security binary from a Script

## Windows

On windows you must have Administrator Access and a recent version of powershell that enable to install modules. To generate the `exe` file, follow the steps below:

- Generate the deployment script from Workload Security and save in a file in a Windows Machine

- Go to <https://github.com/MScholtes/PS2EXE> and follow the instructions to install the powershell module, use the newest version of powershell or a recent version to avoid dependencies issues and execute the powershell as admin.

  - Open the powershell as an Administrator and execute the following:

  - To install the module => `Install-Module ps2exe`

  - Replace the ws.ps1 as your powershell script name and run the tool

    ```powershell
    ps2exe -inputFile .\ws.ps1 -outputFile .\CloudOne.exe -version 20.0.0 -requireAdmin -product CloudOne -MTA
    ```

The `exe` will show in the local folder.

## Linux

### [Optional] Run the build yourself

```bash
docker build -t wsbinaryexport .
```

### Run the container to generate the binary

Replace the name for any name of your preference and replace the tenantid and token as well.

```bash
docker run --name wsbinaryexport -e TENANTID=TENANTID -e TOKEN=TOKEN ghcr.io/felipecosta09/wsbinaryexport
```

### Export the id to a variable

```bash

export CONTAINERID=(`docker ps -aqf "name=wsbinaryexport"`)
```

### Copy the binary to local folder

```bash
docker cp $CONTAINERID:/root/CloudOne .
```

The `elf` will show in the local folder.
