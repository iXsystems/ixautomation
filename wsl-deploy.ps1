docker build -t ixautomation -f Dockerfile .
docker export -o ixautomation.tar $(docker run -d ixautomation /bin/true)
wsl --import ixautomation c:\ixautomation ixautomation.tar --version 2
