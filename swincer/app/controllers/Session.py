class SwinceSession:
    def __init__(self, db_name):
        # Create a new session for the database
        self.db_name = db_name

    def connect_to_guild_database(self):
        # Get MySQL connection details from environment variables
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        root_password = os.getenv("MYSQL_ROOT_PASSWORD")
        host = os.getenv("MYSQL_HOST")
        port = os.getenv("MYSQL_PORT", 3306)

        # Create a new engine for the guild's database
        mysql_engine = create_engine(
            f"mysql+pymysql://{username}:{password}@db/"
        )
        with mysql_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS guild_{self.db_name}"))  # create db
            connection.execute(text(f"USE guild_{self.db_name}"))  # use db

        engine = create_engine(f"mysql+pymysql://root:{root_password}@db:{port}/guild_{self.db_name}")
        # Bind the session factory to the engine
        SessionFactory.configure(bind=engine)

        Base.metadata.create_all(engine)