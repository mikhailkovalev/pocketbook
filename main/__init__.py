try:
    # todo: узнать, нужно ли это на проде для
    #  подключения к MySQL
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
