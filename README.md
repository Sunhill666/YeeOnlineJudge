# 部署

 1. Clone项目到本地

    ```Shell
    git clone https://github.com/Sunhill666/YeeOnlineJudge.git
    ```

 2. 移步至项目文件夹

    ```Shell
    cd ./YeeOnlineJudge
    ```

 3. 安装Virtualenv

    ```Shell
    pip install virtualenv
    ```

 4. 创建虚拟环境

    ```Shell
    virtualenv venv
    ```

 5. 激活虚拟环境

    **Windows执行**

    ```Shell
    source ./venv/Scripts/active
    ```

    **Linux执行**

    ```Shell
    source ./venv/bin/active
    ```

 6. 安装依赖

    > 注意python-psycopg2版本问题，详见[此处](https://blog.csdn.net/z120379372/article/details/78899175)

    ```Shell
    apt install libpq-dev python-psycopg2
    pip install -r requirements.txt
    ```

 7. 启动服务

    ```Shell
    python manage.py runserver 127.0.0.1:8000
    ```
