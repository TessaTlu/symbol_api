# symbol_api
symbol_api implements sear for a publication by text query.

Here is a short guide how to up server: 


Firstly, to connect to postgres you have to change some parameters in app.py:

  line 9: pg_user - set it to user, declared in enviroment of server
  
  line 10: pg_host - check host in logs of postgres container and type here
  
  line 11: pg_pwd - set it by password, that you entered in enviroment of server
  
  line 12: pg_port - set by value from enviroment or from logs of postgres container
  
  line 13: csv_file_path - set location for your .csv file with data
  
  
Secondly, you have to change parametres of serving:

  line 137: host, port in args of serve
  
  
Also, to up server using docker or something else remember to install libraries

  terminal: pip install -r requirements.txt
  
  Dockerfile: RUN pip install --no-cache-dir -r requirements.txt
  
  
Finally, run it:

  terminal: python app.py
  
  Dockerfile: CMD ["python", "app.py"]
