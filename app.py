
from flask import Flask, render_template, url_for, request, redirect
from selenium.webdriver.support.wait import WebDriverWait
import sqlite3
from utils.database_connection import DatabaseConnection
from database_operations import DBOperations
import re
from web_search import WebSearch
import time
from threading import Thread
from database_operations import DBOperations
import os

# Set custom browser path
# os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.getenv("PLAYWRIGHT_BROWSERS_PATH", ".")

display_info = {
    "search_results": [],
    "media_info_all": [],
    "collection_list": [],
    "media_info": [],
    "search_results_keywords": []
}
app = Flask(__name__)



def get_media_info(search_results):
    global media_info_all
    web_search = WebSearch()
    media_info_all = web_search.extract_media_info(search_results)



def get_movie_by_id(id, search_results):
    return next((movie for movie in search_results if movie['id'] == int(id)))



def get_keyword_by_id(id, search_results_keywords):
    return next((keyword for keyword in search_results_keywords if
          keyword['id'] == int(id)))



@app.route('/')
def home():
    return render_template('home.jinja2')



@app.route('/web_search', methods = ['POST', 'GET'])
def web_search():
    global display_info
    try:
        if request.method == 'POST':
            if 'search-button' in request.form:
                if request.form.get("search-by") == 'title':
                    display_info["search_results"] = WebSearch().text_box_search_titles_playwrite(request.form.get('search-value'))
                    return render_template('search_result_by_title.jinja2', search_results=display_info["search_results"], media_info=display_info["media_info"])

                elif request.form.get("search-by") == 'keyword':
                    display_info["search_results_keywords"] = WebSearch().text_box_search_keywords_playwrite(request.form.get('search-value'))
                    return render_template('search_result_by_keyword.jinja2', search_results_keywords=display_info["search_results_keywords"],
                                           media_info=display_info["media_info"])

            if "search-button-keyword" in request.form:
                keyword_details = get_keyword_by_id(request.form.get("search-button-keyword"), display_info["search_results_keywords"])
                display_info["search_results"] = WebSearch().get_movie_titles_for_keyword_playwrite(keyword_details["url"])
                return render_template('search_result_by_title.jinja2',
                                       search_results=display_info["search_results"],
                                       media_info=display_info["media_info"])

            try:
                if 'add-to-collection' in request.form:
                    id = request.form.get('add-to-collection')
                    DBOperations().add_movie(display_info["search_results"], id)
                    return render_template('more_info.jinja2', search_results=display_info["search_results"], media_info=display_info["media_info"])
            except Exception as e:
                print(f"Exception while adding movie to collection: {e}")

            if 'more-info' in request.form:
                try:
                    display_info["media_info"] = [WebSearch().get_media_info_playwrite(get_movie_by_id(request.form.get('more-info'), display_info["search_results"]))]
                    # return render_template('more_info.jinja2', search_results=display_info["search_results"], media_info=display_info["media_info"])
                    return redirect(url_for('movie_details'))
                except Exception as e:
                    print(f"Exception while extracting media info: {e}")

            if 'analyze-button' in request.form:
                try:
                    result = WebSearch().analyze_movie(get_movie_by_id(request.form.get('analyze-button')))
                except Exception as e:
                    print(f"Exception while processing analyze-button: {e}")
    except Exception as e:
        print(f'Error during form submission in web search page: {e}')
    return render_template('web_search.jinja2', search_results=display_info["search_results"])



@app.route('/view_collection', methods = ['POST', 'GET'])
def view_collection():
    if request.method == 'POST':
        if 'search-button' in request.form:
            collection_list = DBOperations().view_collection()
            return render_template('view_collection.jinja2', collection_list=collection_list)
        if 'update-collection-button' in request.form:
            movie_id = request.form.get('update-collection-button')
            print(f"Updating for {movie_id}")
            return redirect(url_for('update_collection', movie_id=movie_id))
    print(f"Value in search text box: {request.form.get('search-value')}")
    collection_list = DBOperations().view_collection()
    return render_template('view_collection.jinja2', collection_list=collection_list)



@app.route('/update_collection/<string:movie_id>', methods = ['POST', 'GET'])
def update_collection(movie_id):
    updated = 0
    if request.method == 'POST':
        if 'submit-button' in request.form:
            DBOperations().update_collection(movie_id)
            updated = 1
    return render_template('update_collection.jinja2', updated=updated)



@app.route('/movie_details/')
def movie_details():
    return render_template('movie_details.jinja2', media_info=display_info["media_info"])



if __name__  == '__main__':
    app.run(debug=False)


