import sqlite3

class DatabaseConnection:
    def __init__(self, host): #The init method runs immediately when the class is called.
        #In this case, it is  storing the host name inside the self.
        self.host = host

    def __enter__(self): #the __enter__ method defines what the  program  should do when it
        # enters the block. Here it is  creating a connection object and returning it.
        self.connection = sqlite3.connect(self.host)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb): #the __exit__ method defines what the
        # program should do when it leaves the block. Here it is committing and closing the connection object.

        if exc_type or exc_val or exc_tb: #We are check if any of these exception variables holds
            #any value. If it does, we would  only close the connection without committing.
            self.connection.close()
        else:
            self.connection.commit()
            self.connection.close()