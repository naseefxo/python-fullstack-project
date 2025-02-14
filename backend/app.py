import os
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Task  # Ensure Task model has a to_dict() method

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize database and also migration
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# api routes
@app.route("/tasks", methods=["GET"])
def get_tasks():
    search_query = request.args.get("search", "").lower()
    priority_filter = request.args.get("priority", "").lower()

    tasks_query = Task.query
    if search_query:
        tasks_query = tasks_query.filter(Task.title.ilike(f"%{search_query}%"))
    if priority_filter in ["low", "medium", "high"]:
        tasks_query = tasks_query.filter(Task.priority.ilike(priority_filter))
    tasks = tasks_query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    print("Received data:", data)
    try:
        deadline = datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M") if data.get("deadline") else None
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    priority = data.get("priority", "Medium").capitalize()
    new_task = Task(
        title=data["title"],
        completed=False,
        deadline=deadline,
        priority=priority
    )
    db.session.add(new_task)
    db.session.commit()
    print("Task added:", new_task.to_dict())
    return jsonify(new_task.to_dict()), 201

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    data = request.json
    task.completed = data["completed"]
    db.session.commit()
    return jsonify(task.to_dict())

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# Catch-all route to serve the Vue.js application
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue(path):
    # if the requested file exist then serve
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # or serve index
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
