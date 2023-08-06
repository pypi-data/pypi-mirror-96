Anonjail
=======

[![pyversions](https://img.shields.io/badge/python-3.3%2B-blue.svg)](https://pypi.org/project/anonjail/)

anonjail is a tool to integrate [Firejail + Tor](https://firejail.wordpress.com/)
sandboxing in the Linux desktop. Enable anonjail for an application and enjoy a
more private and more secure desktop.

Those are the real coders behind this code, i've only made some brainless tweaks:
=======

https://github.com/orjail/orjail & https://github.com/rahiel/firectl


## Install

Automatic anonjail install with pip (debian10 based distros running GNOME only for naw. I know im so sorry):
``` bash
sudo pip3 install anonjail --install-option="--autoinstall=y"
```


Install anonjail and do other steps separately:
``` bash
sudo pip3 install anonjail
```

## Dependencies
``` bash
sudo apt-get -y update
sudo apt-get -y install bc tor firejail python3-pip
```

## Extra steps (Enabling services and FireJail networking)
``` bash
sudo systemctl enable tor --now
sudo systemctl enable apparmor --now
sudo sed -i 's/restricted-network yes/restricted-network no/g' /etc/firejail/firejail.config
```

## If you r running Kali
``` bash
git clone https://github.com/annoyinganongurl/kali-firejail-profiles.git
cp -R kali-firejail-profiles/* /etc/firejail/
rm -rf kali-firejail-profiles
```

## Uninstall

To uninstall anonjail:
``` bash
sudo pip3 uninstall anonjail
```

# Usage

To see which applications owning a personal FJ profile you can enable and current config infos:
``` bash
anonjail status
```

To see which applications with no personal FJ profile you can enable:
``` bash
anonjail showapps
```

To enable firejail for a program:
``` bash
sudo anonjail enable [name]
ex : sudo anonjail enable firefox
```

To disable firejail for a program:
``` bash
sudo anonjail disable [name]
ex : sudo anonjail disable firefox
```

To enable tor + firejail for all program:
``` bash
sudo anonjail enable --all --tor
```

To enable tor + firejail anonjail for a program:
``` bash
sudo anonjail enable [name] --tor
ex : sudo anonjail enable firefox --tor
```