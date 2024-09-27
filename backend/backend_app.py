from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post.", "author": "John Doe", "date": "2023-06-07"},
    {"id": 2, "title": "Second post", "content": "This is the second post.", "author": "Jane Doe",
     "date": "2023-06-08"},
]

SWAGGER_URL = "/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL = "/static/masterblog.json"  # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'  # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
        Get all posts with optional sorting.

        Query parameters:
        - sort: The field to sort by ('title', 'content', 'author', 'date').
        - direction: The sort direction ('asc' or 'desc').

        Returns:
        A JSON array of posts sorted according to the specified parameters.
    """
    sort_by = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    if sort_by == "title":
        posts_sorted = sorted(POSTS, key=lambda x: x['title'], reverse=(direction == "desc"))
    elif sort_by == "content":
        posts_sorted = sorted(POSTS, key=lambda x: x['content'], reverse=(direction == "desc"))
    elif sort_by == "author":
        posts_sorted = sorted(POSTS, key=lambda x: x['author'], reverse=(direction == "desc"))
    elif sort_by == "date":
        posts_sorted = sorted(POSTS, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"),
                              reverse=(direction == "desc"))
    else:
        posts_sorted = POSTS

    return jsonify(posts_sorted)


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
        Add a new post.

        Expects a JSON body with:
        - title: The title of the post.
        - content: The content of the post.
        - author: The author of the post.
        - date: The date of the post (in "YYYY-MM-DD" format).

        Returns:
        The newly created post as JSON with a status code 201 (Created).
        If title, content, author, or date is missing, returns a 400 error.
    """
    data = request.get_json()

    if not data or 'title' not in data or 'content' not in data or 'author' not in data or 'date' not in data:
        return jsonify({"error": "Title, content, author, and date are required"}), 400

    try:
        datetime.strptime(data['date'], "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Date must be in the format YYYY-MM-DD"}), 400

    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content'],
        "author": data['author'],
        "date": data['date']
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a post by its ID.

    Parameters:
    - post_id: The ID of the post to be deleted.

    Returns:
    A message confirming the deletion if successful, or a 404 error if the post was not found.
    """
    global POSTS
    post_to_delete = next((post for post in POSTS if post['id'] == post_id), None)

    if post_to_delete:
        POSTS.remove(post_to_delete)
        return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200
    else:
        return jsonify({"message": f"Post with id {post_id} not found."}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update an existing post.

    Parameters:
    - post_id: The ID of the post to be updated.

    Expects a JSON body with optional fields:
    - title: The new title of the post.
    - content: The new content of the post.
    - author: The new author of the post.
    - date: The new date of the post.

    Returns:
    The updated post as JSON with a status code 200.
    If the post is not found, returns a 404 error.
    """
    global POSTS
    post_to_update = next((post for post in POSTS if post['id'] == post_id), None)

    if post_to_update is None:
        return jsonify({"message": f"Post with id {post_id} not found."}), 404

    data = request.json

    # Validate the date if provided
    if 'date' in data:
        try:
            datetime.strptime(data['date'], "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Date must be in the format YYYY-MM-DD"}), 400

    post_to_update['title'] = data.get('title', post_to_update['title'])
    post_to_update['content'] = data.get('content', post_to_update['content'])
    post_to_update['author'] = data.get('author', post_to_update['author'])
    post_to_update['date'] = data.get('date', post_to_update['date'])

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for posts based on title, content, author, or date.

    Query parameters:
    - title: A substring to search for in post titles.
    - content: A substring to search for in post content.
    - author: A substring to search for in post authors.
    - date: A specific date to search for in the format YYYY-MM-DD.

    Returns:
    A JSON array of posts matching the search criteria.
    """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()
    author_query = request.args.get('author', '').lower()
    date_query = request.args.get('date', '').lower()

    results = [
        post for post in POSTS
        if (title_query in post['title'].lower() or
            content_query in post['content'].lower() or
            author_query in post['author'].lower() or
            date_query in post['date'])
    ]

    return jsonify(results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
