
# from jproperties import Properties
from mysql.connector import pooling

def createsysdbConnectionPooling():
    try:
        # configs = Properties()
        # with open('/opt/Solartis_Python_11/Gunicorn/dbData.properties', 'rb') as config_file:
        #     configs.load(config_file)
        configs = {
            "pool_size": 20,
            "db_host": "10.101.4.13",
            "db_port": "3401",
            "db_user": "usquoperationuser",
            "db_cred": "USQUat*23jKla!kLq65",
            "dbname": "solartissysconfigdbV3"
        }
        sysdb_pooling_object = pooling.MySQLConnectionPool(pool_name="sysconfigdbV3",
                                                        pool_size=int(configs["pool_size"]),
                                                        pool_reset_session=True,
                                                        host=configs["db_host"],
                                                        port=int(configs["db_port"]),
                                                        user=configs["db_user"],
                                                        password=configs["db_cred"],
                                                        database=configs["dbname"],
                                                        auth_plugin='mysql_native_password',
                                                        ssl_disabled=True,
                                                        buffered=True)
        return sysdb_pooling_object
    except Exception as exception:
        raise exception("Error while getting createsysdbConnectionPooling")
    
    