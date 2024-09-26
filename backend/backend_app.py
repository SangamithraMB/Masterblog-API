from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
        Get all posts with optional sorting.

        Query parameters:
        - sort: The field to sort by ('title' or 'content').
        - direction: The sort direction ('asc' or 'desc').

        Returns:
        A JSON array of posts sorted according to the specified parameters.
    """
    sort_by = request.args.get('sort')
    direction = request.args.get('direction')

    if sort_by == "title":
        posts_sorted = sorted(POSTS, key=lambda x: x['title'], reverse=(direction == "desc"))
    elif sort_by == "content":
        posts_sorted = sorted(POSTS, key=lambda x: x['content'], reverse=(direction == "desc"))
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

        Returns:
        The newly created post as JSON with a status code 201 (Created).
        If the title or content is missing, returns a 400 error.
    """
    data = request.get_json()

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Title and content are required"}), 400

    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
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

    Returns:
    The updated post as JSON with a status code 200.
    If the post is not found, returns a 404 error.
    """
    global POSTS
    post_to_update = next((post for post in POSTS if post['id'] == post_id), None)

    if post_to_update is None:
        return jsonify({"message": f"Post with id {post_id} not found."}), 404

    data = request.json
    post_to_update['title'] = data.get('title', post_to_update['title'])
    post_to_update['content'] = data.get('content', post_to_update['content'])

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for posts based on title and content.

    Query parameters:
    - title: A substring to search for in post titles.
    - content: A substring to search for in post content.

    Returns:
    A JSON array of posts matching the search criteria.
    """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    results = [
        post for post in POSTS
        if title_query in post['title'].lower() or content_query in post['content'].lower()
    ]

    return jsonify(results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
