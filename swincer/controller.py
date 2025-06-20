import sqlite3

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
import os

from .model import *

# Base session factory
SessionFactory = sessionmaker()

# Scoped session for thread safety
Session = scoped_session(SessionFactory)



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

    def __enter__(self)->Session:
        # Connect to the guild's database
        self.connect_to_guild_database()
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the session
        self.session.close()
        Session.remove()
        return False

class SwinceController:
    def __init__(self, db_name, db_dir="./assets/databases"):
        self.db_name = db_name\

    def add_swince(self, from_user, to_user, date, origin):
        # Create a new Swince object
        new_swince = Swince(date=date, origin=origin)


        with SwinceSession(self.db_name) as session:
            # Add the new Swince object to the session
            session.add(new_swince)
            session.commit()
            try:

                # Create a new Originator object
                originator_list = []
                for user in from_user:
                    originator_list.append(Originator(swince_id=new_swince.id, originator_id=user))
                # Create a new Target object
                target_list = []
                for user in to_user:
                    target_list.append(Target(swince_id=new_swince.id, target_id=user))

                # Add the new Originator object to the session
                for new_originator in originator_list:
                    session.add(new_originator)
                # Add the new Target object to the session
                for new_target in target_list:
                    session.add(new_target)
                # Commit the transaction
                session.commit()
            except Exception as e:
                session.rollback()
                session.delete(new_swince)
                raise e

    def get_swince(self, swince_id):
        # Query the Swince object by ID
        with SwinceSession(self.db_name) as session:
            swince = session.query(Swince).filter(Swince.id == swince_id).first()

        return swince

    def get_all_swince(self):
        # Query all Swince objects
        with SwinceSession(self.db_name) as session:
            swince_list = session.query(Swince).all()
        return swince_list


class UserController :
    def __init__(self, db_name):
        self.db_name = db_name

    def add_user(self, user_id, user_name):
        # Create a new User object
        new_user = User(id=user_id, name=user_name)

        with SwinceSession(self.db_name) as session:
            # Add the new User object to the session
            try :
                session.add(new_user)
                # Commit the transaction
                session.commit()
            except (sqlalchemy.exc.IntegrityError, sqlite3.IntegrityError) as e:
                # Handle the case where the user already exists
                session.rollback()
                print(f"User {user_id} already exists in the database.")



    def get_user(self, user_id):
        # Query the User object by ID
        with SwinceSession(self.db_name) as session:
            user = session.query(User).filter(User.id == user_id).first()

        return user


    def get_all_users(self):
        # Query all User objects
        with SwinceSession(self.db_name) as session:
            user_list = session.query(User).all()
        return user_list


    """This method has two usecases :
        1. At first the global name was used so this method is used to gracefully update the name of the user to its nickname
        2. If the user change its nickname on discord, this method is used to update the name in the database
    """
    def update_user_name(self, user_id, new_name):
        """
        Update the name of a user in the database.

        :param user_id: The ID of the user to update.
        :param new_name: The new name to set for the user.
        :return: None
        """
        with SwinceSession(self.db_name) as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.name = new_name
                session.commit()
            else:
                print(f"User with ID {user_id} not found in the database.")


class MessageController:
    def __init__(self, db_name):
        self.db_name = db_name

    def add_message(self, message_id, content, author):
        # Create a new Message object
        new_message = Message(id=message_id, content=content, author=author)

        with SwinceSession(self.db_name) as session:
            # Add the new Message object to the session
            session.add(new_message)
            # Commit the transaction
            session.commit()

    def get_message(self, message_id):
        # Query the Message object by ID
        with SwinceSession(self.db_name) as session:
            message = session.query(Message).filter(Message.id == message_id).first()

        return message

    def get_all_messages(self):
        # Query all Message objects
        with SwinceSession(self.db_name) as session:
            message_list = session.query(Message).all()
        return message_list


class StatController :
    def __init__(self, db_name):
        self.db_name = db_name

    def get_score_with_session(self, session, userID):
        target_num = session.query(Target).filter(Target.target_id == userID).count()
        origin_num = session.query(Originator).filter(Originator.originator_id == userID).count()

        return target_num,origin_num

    def get_score(self,userID):
        with SwinceSession(self.db_name) as session:
            target_num, origin_num = self.get_score_with_session(session, userID)
        return target_num,origin_num

    """
    scapeGoat and bully cant be done for now as it needs a seamless and intuitive way to represent one to one relations
    between originators and targets in the command which was not found yet
    """

    def get_all_score(self):
        with SwinceSession(self.db_name) as session:
            user_list = session.query(User).all()
            score_list = []
            for user in user_list:
                score = self.get_score_with_session(session, user.id)
                score_list.append((user.name,*score))
        return score_list



