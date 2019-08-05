# myCSSA 
This is the online services platform for Chinese Students and Scholars Association @ Unimelb <br>
Proundly developed and supported by the Department of Information Technology, CSSAUnimelb
## Prerequisites
You MUST have these packages/tools installed on your local machine before playing with this project
1. Docker-CE (Community Edition)
2. Python == 3.7.2
3. Lastest stable version of Pipenv (Optional but recommended)
4. PostgesSQL Server == 10.6 (Optional for who wants to test code outside the Docker container)
## Additional Note for Windows Users
Currently the ALICE bootloader (alice-bootloader.sh) is added as an entry point for myCSSA container. Due to the difference in EOL between Windows and UNIX-based systems, the bootloader could be not executed properly in Windows environment. If you see the error " exec user process caused 'no such file or directory'", please use Notepad++ or something equivlent to modify the EOL of alice-bootloader.sh to UNIX style.
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
5. Access the page at: http://localhost:8000
6. To access Admin Pages, use this account:
 <br> email: testadmin@cssa.com
 <br> password: test1234
 
## Note for Configuring pylint for the project
Since CSSANet is set to be running in a Docker Containter, the file structures is a bit different from an usual pipenv configuration. In some cases, especially when you use IDE with IntelliSense technology (e.g. VSCode), this could cause problems in importing project's app. Please following the steps below to resolve the issue:
1. Under the directory 'your/path/to/myCSSA/CSSANet/code', run:
```
pipenv install -r ../requirements.txt --python=3.7.2
```
2. then, switch to the virtual environment, run the command: 
```
pipenv shell
```
3. In VSCode, open the 'code' folder as a __new workspace__, then select your venv python as the interpreter and enable pylint.

## To be a Contributor
Welcome to join us by contacting: information@cssaunimelb.com

## Major Contributor
Project Manager and Lead Engineer: Le (Josh). Lu (joshlubox@gmail.com)

UI / UX Designer and Lead Front-end Developer : Mengyu (Caitlin) Jiang (icesymeng@gmail.com)

Communication System Developer: Shenhai (Howie). Chen

Content Managament System Developer: Maoting (Brook). Zuo
