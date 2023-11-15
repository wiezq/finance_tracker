Installation:
1. Docker needs to be installed version 3 and higher
2. delete ```platform: linux/amd64``` in Docker/docker-compose.yml (`for x86_64 pcs`)
3. run ```docker-compose up``` in project directory it will start mysql container on `port 6033` and phpmyqsladmin on `port 8081` (GUI for MySQL)
4. Activate virtual enviroment inside project dir (optional)
5. Then run `python3 -m pip install -r requirements.txt` to install required packages (might be problems with mysql-client)
6. Then run `python app.py`
7. visit http://127.0.0.1:5000/ to test
