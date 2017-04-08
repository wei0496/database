# Flask INstallations
## FLASK
The first step in the process is to install flask. You can install flask with pip. To install the
packages using pip open the terminal and type the following command:</br>
 - (For python 2.*) sudo pip install Flask</br>
 - (For python 3.*) sudo pip3 install Flask</br>
 - (For anaconda) conda install -c anaconda flask=0.11.1</br>
-FLASK MYSQL</br>
After installing Flask, you must also install the MySQL flask extension with pip. You can
install it using the following command:</br>
 - (For python 2.*) sudo pip install flask-mysql</br>
 - (For python 3.*) sudo pip3 install flask-mysql</br>
 - (For anaconda) conda install -c auto flask-mysql=1.2</br>
Extra Notes:</br>
- If you would like, you can use a virtual environment to set up this project too.</br>
- If for some reason you do not have pip you can install it by downloading the following script and running the script with your preferred version of python. Once this script has finished running, you can install the packages.</br>
 - https://bootstrap.pypa.io/get-pip.py</br>
- If you still can not install the packages please email me or refer to the additional documentation.</br>

## USING FLASK WITH PYTHON
Once Flask has been installed for python, it can be imported into python code. Example code can
be found on the lab website, under Labs 3 and 4. </br>

## RUNNING FLASK PYTHON APPLICATION
To run the python script as a flask application You must complete the following steps:</br>
1, Navigate to the directory that contains your python script and enter the following command
into a terminal:</br>
 - (for Mac/Linux) export FLASK_APP=<filename.py> </br>
 - (For Windows) set FLASK_APP=<filename.py> </br>
Replace <filename.py> with the python script where you are writing your code. Make sure
you are in the directory where your script is before executing the export command</br>
2, To start your server and run your script enter the following command into a terminal:
 - flask run
Run this command any time you want to view your site. This will start the server for the
application and will provide you with a link to view your site. If you are running your site on
your local machine the site will be:
 http://127.0.0.1:5000/
3, You can enter this address into your web browser to use your site. To stop your server enter
CTRL-C</br>
HOSTING ONLINE (Optional)</br>
There are many ways to perform this step but an easy method is to use pythonanywhere. If you
go to https://www.pythonanywhere.com/ and create an account, it will provide you with a tutorial
on how to set up a web application.</br>
Because you will still need to install the flask-mysql package, the easiest method to do this is to
create a virtual environment for your code. There are detailed instructions on how to do this on
pythonanywhere. </br>
ADDITIONAL DOCUMENTATION</br>
http://flask.pocoo.org/docs/0.11/installation/
https://www.pythonanywhere.com/
