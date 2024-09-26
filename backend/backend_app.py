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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
