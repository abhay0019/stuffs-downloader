# stuffs-downloader
A Python Script to Download TV Series / Movies with Variety of Options .. 

NOTE : This script is only for UBUNTU users

Get python-2 from website http://www.python.org/getit/. 
Install python in your system .

If having trouble installing python follow link :-               
http://askubuntu.com/questions/101591/how-do-i-install-python-2-7-2-on-ubuntu

Install pip :-

sudo apt-get install python-pip                                                 (It will be usefull for future module installations )

Install all modules needed :-

1) sudo pip install selenium

and others if not present in your system by similar syntax : sudo pip install module_name 

Keep this entire project directory in :-
/home/user_name/Desktop/py

In download.conf file enter the full path to the directory , you want your downloads to save to .

(proxy switch is not enable for now so leave proxy.conf as it as!!)

Open terminal in the stuffs-downloader directory and enter command:-

python stuff_downloader.py

A well Informative Session will start , User can follow it very easily ..

 


New Commit :- Added extra feature for downloading movies too .

Information for using updates :-

Update the download_movie.conf by entering the complete path to the  directory , you want your download to be stored .. 

Added shell script file (download) should be copied to ~/bin directory for easier download-procedure :-

Instructions to add shell script file (download) :-

1)Copy the download file to ~/bin directory
2)Give it execute permission (use command :- chmod +x ~/bin/download) 
3)Set PATH variable (export PATH=$PATH:~/bin)
4)Now you can easily execute the script from any location by just typing the command :-  download




