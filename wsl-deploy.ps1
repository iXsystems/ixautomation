docker build -t ixautomation -f Dockerfile .
docker export -o ixautomation.tar $(docker run -d ixautomation /bin/true)
wsl --import ixautomation c:\ixautomation ixautomation.tar --version 2
$WSLUSER = Read-Host "Please enter your username"
wsl -d ixautomation adduser $WSLUSER
wsl -d ixautomation usermod -aG sudo $WSLUSER
wsl -d ixautomation echo -e "[user]\ndefault=$WSLUSER" >> wsl.conf
wsl -d ixautomation mv wsl.conf /etc/wsl.conf
