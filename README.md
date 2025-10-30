# Software Engineering Project

Team Memebers:
1. Debraj Bose - 895
2. Iman Kalyan Chakraborty - 901
3. Om Chatterjee - 916
4. Prachi Das - 917

# Instructions To Run
__IMPORTANT:__ This code was run using python 3.11.9. Any other version later than that is not recommended.

1. Create a Virtual Environment for Python (For MacOS only, Windows may have slightly different process)

    ``` 
    python3 -m venv venv 
    ```

2. Activate the Virtual Environment

    ``` 
    source venv/bin/activate 
    ```

3. Install the dependencies

    ``` 
    pip install -r requirements.txt 
    ```

4. Run the following 2 commands to setup django

    ``` 
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Create the credentials for the Admin

    ```
    python manage.py createsuperuser
    ```

6. Run the server

    ```
    python manage.py runserver
    ```

    The server will be hosted at __localhost:8000/admin__.

7. Run the GUI

    ```
    python sis_gui.py
    ```

Initially no user will be present in the database. For that, the admin first needs to fill some sample data into the database using the django admin panel. It is recommended to fill the tables in the order mentioned in the file data_adding_order.txt because the tables are dependent on each other. After filling the sample data, the user can login in the sis_gui.py using the reg no filled in the django admin panel. For the first time, the default password is default123. After this, a window will automatically open prompting the user to change their default password. After that, the sis_gui.py can be used normally.

8. (Optional) Run the tests. 

   ```
   pytest
   ```
   
