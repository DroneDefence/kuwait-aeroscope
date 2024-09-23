### Kuwait Aeroscope:

- Here we are getting or accepting data from kuwait aeroscope side, Proessing it and sending to the aerotracker.

How to run the file:

- Run Directly (without background process):

``` python3 /home/ubuntu/kuwaitAS/kuwait_aeroscope.py ```

- Currently it is running with "nohup":

``` nohup python3 kuwait_aeroscope.py > output.log 2>&1 & ```

#### To see the running nohup processes:

``` ps aux | grep kuwait_aeroscope.py ```

#### Kill all process which runs kuwait_aeroscope.py

``` pkill -f kuwait_aeroscope.py ```

