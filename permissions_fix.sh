#! /bin/bash

# /etc sudoers file edited to allow user 
# admin to run sudo command without password prompt
# admin ALL=(ALL) NOPASSWD:/Users/admin/Scripts/_Disney_DIVA_API_Object_Restore/

cd $1
sudo -u admin chflags nouchg ./
sudo chmod -R 777 ./
sudo chmod -RN ./
# sudo chown -R 40006:50004 ./
sudo xattr -rc ./

# sudo -u admin -H sh -c "sh /path/to/myscript.sh"

# sudo -u admin chflags -R nouchg ./
# sudo chmod -R 777 ./
# sudo chmod -RN ./
# sudo chown -R admin:staff ./
# sudo xattr -rc ./