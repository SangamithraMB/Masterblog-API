from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc').lower()

    if sort_field not in [None, 'title', 'content']:
        return jsonify({"message": "Invalid sort field. Use 'title' or 'content'."}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({"message": "Invalid sort direction. Use 'asc' or 'desc'."}), 400

    if sort_field:
        POSTS.sort(key=lambda x: x[sort_field].lower(), reverse=(sort_direction == 'desc'))

    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Error handling: Check if both title and content are provided
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Title and content are required"}), 400

    # Generate a new unique ID for the new post
    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

    # Create the new post
    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }

    # Add the new post to the list
    POSTS.append(new_post)

    # Return the new post with status code 201 Created
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS  # Use global to modify the POSTS list
    # Find the post by ID
    post_to_delete = next((post for post in POSTS if post['id'] == post_id), None)

    if post_to_delete:
        POSTS.remove(post_to_delete)  # Remove the post from the list
        return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200
    else:
        return jsonify({"message": f"Post with id {post_id} not found."}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    global POSTS
    post_to_update = next((post for post in POSTS if post['id'] == post_id), None)

    if post_to_update is None:
        return jsonify({"message": f"Post with id {post_id} not found."}), 404

    data = request.json
    # Update the title and content if provided
    post_to_update['title'] = data.get('title', post_to_update['title'])
    post_to_update['content'] = data.get('content', post_to_update['content'])

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filter posts based on the search criteria
    results = [
        post for post in POSTS
        if title_query in post['title'].lower() or content_query in post['content'].lower()
    ]

    return jsonify(results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
