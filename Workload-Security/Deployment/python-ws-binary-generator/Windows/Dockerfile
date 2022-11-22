FROM mcr.microsoft.com/powershell:latest

# Set the working directory to /root
WORKDIR /root

# Download ps1 file
ADD ../app.py /root/app.py
ENV REGION=REGION APIKEY=APIKEY PLATFORM=PLATFORM
RUN app.py --c1region $REGION --apikey $APIKEY --platform $PLATFORM

# Install PS2EXE
RUN pwsh -Command "Install-Module ps2exe -Force"

# Convert ps1 to exe
RUN pwsh -Command "ConvertTo-Exe -Path ws.ps1 -Output ws.exe -Force"