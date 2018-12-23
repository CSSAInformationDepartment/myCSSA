# myCSSA 
This is the next-gen online services platform for Chinese Students and Scholars Association @ Unimelb <br>
Proundly developed and supported by the Department of Information Technology, CSSAUnimelb
## Prerequisites
You MUST have these packages/tools installed on your local machine before playing with this project
1. Docker-CE (Community Edition)
2. Python >= 3.6
3. Lastest stable version of Pipenv (Optional but recommended)
## Additional Notice for Windows Users
Currently the ALICE bootloader (alice-bootloader.sh) is added as an entry point for myCSSA container. However, due to the difference in EOL between Windows and UNIX-based systems, the bootloader could be not executed properly in Windows environment. If you see the error " exec user process caused 'no such file or directory'", please use Notepad++ or something equivlent to modified the EOL of alice-bootloader.sh to UNIX style.
## Quick Start Guide
1. Clone this repo to your local machine by running: 
```
git clone https://github.com/ShepherdMOZ/myCSSA.git
```
2. Use Terminal in Mac/Linux/Unix or PowerShell in Windows
3. Navigate to the repo folder
4. Run following command:
```
cd CSSANet
docker-compose up --build 
```
5. Access the page at: http://[Your Computers IP]:8000
6. To access Admin Pages, use this account:
 <br> email: testadmin@cssa.com
 <br> password: test1234

## To be a Contributor
Welcome to join us by contacting: information@cssaunimelb.com

## Project Info
Project Manager and Lead Engineer: Josh.Le.Lu (joshlubox@gmail.com)
