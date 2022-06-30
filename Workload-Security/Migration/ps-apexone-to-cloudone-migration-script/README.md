# C1_migration

> This project requires external files that will not be included in the repo, please see instructions below. 

You need to include all these files in the SAME folder/directory in order for this PowerShell script to work.
- Requires Cloud One deployment script (Windows deployments ONLY).
- Requires the SCUT tool (SCUT.exe & SCUT.exe.config) to remove Apex One.
- **Requires admin privileges.**

> :warning: Warning: **This script will force a restart on the machine if the SCUT.exe tool executes successfully.**

The PowerShell script will automatically determine if Apex One is present and if it's not, it will install Cloud One. If Cloud one is already installed, it will stop. This script is designed to be placed in a startup script or task scheduler on Windows but can also just be executed manually.

## Script Workflow:

- Running the script once, removes Trend Micro Apex and forces restart. 

- Run script again after restart and it will install Cloud One. 

You can't break anything with this because it's already programmed to handle any situation on its own.


### Notes : 

> Line 24 contains the SCUT.exe that is being called in the PowerShell script. It should always be called "SCUT.exe", even with your own copy, but in case the name changes please make sure they match here.

> Line 47 is the name of your Cloud One script to trigger installation of the Cloud One agent. Please re-name your deployment script file like the one shown here "C1_install.ps1" or change the name here to the filename of your Cloud One deployment script.

> The script automatically dumps the log file into the directory its running out of in case of errors.
