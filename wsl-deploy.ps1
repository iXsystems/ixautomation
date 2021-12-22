docker build -t ixautomation -f Dockerfile .
docker export -o ixautomation.tar $(docker run -d ixautomation /bin/true)
wsl --import ixautomation c:\ixautomation ixautomation.tar --version 2
$WSLUSER = Read-Host "Please enter your username"
wsl -d ixautomation useradd $WSLUSER
wsl -d ixautomation passwd $WSLUSER
wsl -d ixautomation usermod -aG sudo $WSLUSER
wsl -d ixautomation echo -e "[user]\ndefault=$WSLUSER" >> /etc/wsl.conf
