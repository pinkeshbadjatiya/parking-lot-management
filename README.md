# Software Engineering project: Parking Lot

Set up environment:

    ```
    Dependencies:
        >> sudo apt-get install build-essential libssl-dev libffi-dev python-dev
        >> pip install -r requirements.txt
    ```

Run the app:
    
    NOTE: You have to be in the home folder of the repository to execute these commands
    --> To run the server
        >> export FLASK_APP=ParkingLotServer
        >> flask run

    --> To run the client
        >> export FLASK_APP=ParkingLotClient
        >> flask run

=============================================================

Database commands:

    ```
    1. To initialize the database run:
            >> flask db init
        NOTE: You do not have to initializa the database now. (Pinkesh has done it).
              You just have to run the below commands whenever you make changes in model

    2. After you make changes in the models.py file or add a new one run the following commands:
            >> flask db migrate
            >> flask db upgrade
    This will create migrations and update them on the server.
    NOTE: Do not keep the app running while running this command

