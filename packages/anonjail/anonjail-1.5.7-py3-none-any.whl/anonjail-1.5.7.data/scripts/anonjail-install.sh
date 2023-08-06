sudo apt-get -y update
sudo apt-get -y install bc tor firejail
sudo systemctl enable tor --now
sudo systemctl enable apparmor --now
sudo sed -i 's/restricted-network yes/restricted-network no/g' /etc/firejail/firejail.config
sudo git clone https://github.com/annoyinganongurl/kali-firejail-profiles.git
sudo cp -R kali-firejail-profiles/* /etc/firejail/
sudo rm -rf kali-firejail-profiles
sudo cd ../torjail
sudo make install