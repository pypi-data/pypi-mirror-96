apt-get -y update
apt-get -y install bc tor firejail
systemctl enable tor --now
systemctl enable apparmor --now
sed -i 's/restricted-network yes/restricted-network no/g' /etc/firejail/firejail.config
git clone https://github.com/annoyinganongurl/kali-firejail-profiles.git
cp -R kali-firejail-profiles/* /etc/firejail/
rm -rf kali-firejail-profiles
cd ../torjail
make install