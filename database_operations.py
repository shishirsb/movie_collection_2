
import re
from flask import request
from utils.database_connection import DatabaseConnection

class DBOperations:
    def __init__(self):
        pass


    def add_movie(self, search_results, id):
        self.create_movies_table()
        result = next((search_result for search_result in search_results if search_result['id'] == int(id)), None)
        if result:
            try:
                with DatabaseConnection('data.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute('INSERT INTO movies VALUES(?, ?, ?, ?, ?, ?)', (
                        int(id), result['title'], ' - '.join(result['other_details']), "Not updated", "Not updated", "Not updated"))
                print(f"{result['title']} has been added to Database")
            except Exception as e:
                print(f"Exception while adding movie to collection: {e}")
        elif result is None or result == "":
            raise ValueError("Value not available")


    @staticmethod
    def update_collection(movie_id):
        viewed = request.form.get('viewed')
        user_notes = request.form.get('user-notes')
        user_rating = request.form.get('user-rating')
        try:
            with DatabaseConnection('data.db') as connection:
                cursor = connection.cursor()
                cursor.execute("""UPDATE movies
                                SET read = ?, user_notes = ?, user_rating = ?
                                WHERE id = ?""",
                               (viewed, user_notes, user_rating, movie_id))
                if cursor.rowcount > 0:
                    print(f"Successfully updated {cursor.rowcount} row(s)")
                else:
                    print("No matching rows found - nothing was updated")
        except Exception as e:
            print(f'Unknown error: {e}')



    def create_movies_table(self):
        try:
            with DatabaseConnection(
                    'data.db') as connection:  # DatabaseConnection is a class which returns a connection object.
                # What the class should do when we enter and exit is defined within the class.
                cursor = connection.cursor()  # We are using the connection object returned

                cursor.execute(
                    'CREATE TABLE IF NOT EXISTS movies (id INTEGER primary key, title TEXT ,other_details TEXT, read INTEGER, user_notes TEXT, user_rating INTEGER)')
        except Exception as e:
            print(f"An unknown exception while creating table: {str(e)}")



    @staticmethod
    def view_collection():
        collection_list = []
        search_query = request.form.get('search-value')

        with DatabaseConnection('data.db') as connection:
            cursor = connection.cursor()
            if search_query is None:
                cursor.execute('SELECT * FROM movies')
            elif search_query.strip() == "":
                cursor.execute('SELECT * FROM movies')
            elif (search_query is not None) and (search_query.strip() != "") :
                search_value = f"%{request.form.get('search-value').lower()}%"
                cursor.execute('SELECT * FROM movies WHERE LOWER(title) LIKE ?', (search_value,))
            movies = cursor.fetchall()
            collection_list = [{'id': row[0], 'title': row[1], 'other_details': row[2], 'viewed': row[3], 'user_notes': row[4],
                                'user_rating': row[5]} for row in movies]

        print(collection_list)
        return collection_list

