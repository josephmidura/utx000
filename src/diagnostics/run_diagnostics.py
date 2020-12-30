import os
import logging

import pandas as pd
import numpy as np

from datetime import datetime, timedelta

class Diagnostics():

    def __init__(self, single=False, save_dir="~/Projects/utx000/data/raw/bpeace2/beacon/"):
        """
        Checks if we want a single beacon, otherwise runs for all. User can
        download, remove, or run diagnostics.
        """

        # Getting Beacon Numbers
        # ----------------------
        if single:
            self.beacon = input("Enter Beacon Number (0,50): ") # setting to user input
            try:
                self.beacon = [int(self.beacon)] # single beacon number - 0 will be added in run()
            except ValueError:
                print("You must enter a valid number")
                self.terminated()
        else:
            self.beacon = range(0,51) # setting to list of all beacons

        self.save_dir = save_dir # directory to save downloaded data to

        # Commands
        # ------------
        # List of options 
        print("Please choose an option from the list below")
        print("\t1. Update Software")
        print("\t2. Download Data")
        print("\t3. Download and Remove Data")
        print("\t4. Remove Data")
        print("\t5. Run Full Diagnostics")
        op = int(input("\nOption: "))
        # Run diagnostics
        if op == 1:
            fxns = [self.update]
        elif op == 2:
            fxns = [self.downloadData]
        elif op == 3:
            fxns = [self.downloadData, self.removeData]
        elif op == 4:
            fxns = [self.removeData]
        elif op == 5:
            fxns = [self.getUpdates,self.downloadData,self.checkSensors,self.removeData]
        else:
            os.system("clear")
            print("Not a valid choice")
            self.terminated()

        power_op = input("Do you wish to power the device(s) down after (y/n)? ")
        if power_op.lower() in ["y","yes"]:
            fxns.append(self.shutdown)
        else:
            fxns.append(self.reboot)

        self.run(fxns)

    def getUpdates(self, beacon_no):
        """
        Pulls in updates from git
        """
        print("\n\tUpdating from Git:")
        os.system(f'ssh pi@iaq{beacon_no} -o ConnectTimeout=1 "sudo apt-get install -y pigpio python-pigpio python3-pigpio && cd bevo_iaq/Setup/Code && rm *.pyc && git reset --hard && git pull"')
        os.system(f'scp -o ConnectTimeout=1 ~/Projects/utx000/src/diagnostics/test.sh pi@iaq{beacon_no}:/home/pi/test.sh')
        os.system(f'ssh -o ConnectTimeout=1 pi@iaq{beacon_no} "sh /home/pi/test.sh {beacon_no}"')

    def downloadData(self, beacon_no, save_dir="~/Projects/utx000/data/raw/bpeace2/beacon/"):
        """
        Downloads data from specified beacon
        """
        print("\n\tDownloading Data:")
        os.system(f'scp -r -o ConnectTimeout=1 pi@iaq{beacon_no}:/home/pi/DATA/adafruit/ {save_dir}B{beacon_no}/')
        os.system(f'scp -r -o ConnectTimeout=1 pi@iaq{beacon_no}:/home/pi/DATA/sensirion/ {save_dir}B{beacon_no}/')

    def checkSensors(self, beacon_no):
        """
        Checks the operation of the sensors
        """
        print("\n\tChecking Sensor Connection:")
        os.system(f'ssh pi@iaq{beacon_no} -o ConnectTimeout=1 "python3 bevo_iaq/Setup/Code/addresses.py"')

    def removeData(self, beacon_no):
        """
        Removes data from specified beacon
        """
        print("\n\tDeleting Data...")
        #os.system('tput setaf 1; echo REMOVING LOG2/LOG3 DATA; tput sgr 0')
        os.system(f'ssh pi@iaq{beacon_no} -o ConnectTimeout=1 "cd DATA/adafruit/ && sudo rm *.csv && cd ../sensirion/ && sudo rm *.csv"')

    def reboot(self,beacon_no):
        """
        Reboots the system for changes to take effect
        """
        print("\n\tRebooting...")
        os.system(f'ssh pi@iaq{beacon_no} -o ConnectTimeout=1 -o ServerAliveInterval=5 -o ServerAliveCountMax=2 "sudo reboot"')

    def shutdown(self,beacon_no):
        """
        Reboots the system for changes to take effect
        """
        print("\n\tShutting Down...")
        os.system(f'ssh pi@iaq{beacon_no} -o ConnectTimeout=1 -o ServerAliveInterval=5 -o ServerAliveCountMax=2 "sudo shutdown -h now"')

    def run(self,fxns):
        """
        Runs the functions in fxns
        """
        for i in self.beacon:
            if i < 10:
                i = '0' + str(i)
            #print(f"Beacon {i}:")
            os.system(f'tput setaf 1; echo Beacon {i}; tput sgr 0')
            for f in fxns:
                f(i)

    def terminated(self):
        print("User has terminated program.")
        return False

def main():
    logger = logging.getLogger(__name__)
    os.system("clear")

    single = input("Individual Download (y/n)? ")
    if single.lower() in ["y","yes"]:
        d = Diagnostics(True)
    else:
        d = Diagnostics(False)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='diagnostics.log', filemode='w', level=logging.DEBUG, format=log_fmt)

    main()