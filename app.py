import logging
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from markupsafe import Markup, escape
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import secrets
import subprocess
import tempfile
from sqlalchemy import text  # Import the text() function

app = Flask(__name__)
# Explicitly set the SECRET_KEY.  Use a hardcoded value for testing, but
# generate a random, secure one for production!
app.config['SECRET_KEY'] = "VERY_SECRET_KEY_FOR_TESTING"  # Replace this!
# In a production environment, use:
# app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'

# VULNERABLE FILE UPLOAD CONFIGURATION - FOR DEMO PURPOSES ONLY
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'js', 'html', 'php', 'exe', 'sh', 'bat'}

# Create upload directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<Post {self.title}>'

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('replies', lazy=True))
    post = db.relationship('Post', backref=db.backref('replies', lazy=True))

    def __repr__(self):
        return f'<Reply {self.content}>'

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            admin = User(username='admin', password=generate_password_hash('adminpass', method='pbkdf2:sha256'), role='admin')
            user1 = User(username='tech_enthusiast', password=generate_password_hash('techpass', method='pbkdf2:sha256'))
            user2 = User(username='movie_buff', password=generate_password_hash('moviepass', method='pbkdf2:sha256'))
            user3 = User(username='bookworm', password=generate_password_hash('bookpass', method='pbkdf2:sha256'))
            user4 = User(username='gamer_pro', password=generate_password_hash('gamerpass', method='pbkdf2:sha256'))
            user5 = User(username='travel_lover', password=generate_password_hash('travelpass', method='pbkdf2:sha256'))
            user6 = User(username='foodie_fan', password=generate_password_hash('foodiepass', method='pbkdf2:sha256'))
            db.session.add_all([admin, user1, user2, user3, user4, user5, user6])
            db.session.commit()
            posts = [
                Post(title='Welcome to the Tech Forum!', content='Discuss the latest tech trends here.', user_id=1),
                Post(title='Best Programming Languages?', content='What are your favorite programming languages and why?', user_id=2),
                Post(title='Upcoming Movie Releases', content='Excited for any upcoming movies? Let\'s discuss!', user_id=3),
                Post(title='Book Recommendations for Sci-Fi Fans', content='Looking for good sci-fi books to read.', user_id=4),
                Post(title='Gaming News and Reviews', content='Share your thoughts on the latest video games.', user_id=5),
                Post(title='Travel Destinations for 2024', content='Planning any trips for next year? Share your ideas!', user_id=6),
                Post(title='Delicious Food Recipes', content='Post your favorite recipes here.', user_id=1),
                Post(title='DIY Home Improvement Tips', content='Share your DIY projects and tips.', user_id=2),
                Post(title='Art and Creative Projects', content='Showcase your artistic creations.', user_id=3),
                Post(title='Science and Technology Updates', content='Discuss recent scientific discoveries.', user_id=4),
                Post(title='History and Historical Events', content='Let\'s talk about historical events and figures.', user_id=5),
                Post(title='XSS Test', content='<script>alert("XSS");</script>', user_id=6),
                Post(title='SQL Test', content='\' or 1=1; --', user_id=1),
                Post(title='Favorite tech gadgets', content= 'What are your favorite tech gadgets?', user_id=2),
                Post(title='Best gaming console', content= 'Which is the best gaming console?', user_id=3)
            ]
            db.session.add_all(posts)
            db.session.commit()

init_db()

# Configure logging (optional, but recommended)
logging.basicConfig(level=logging.DEBUG)  # Or logging.INFO, etc.
logger = logging.getLogger(__name__)

# HTML Templates (as strings to be written to files)
index_template = """
<!DOCTYPE html>
<html>
<head><title>Forum</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
    <div class="container">
        {% if show_alert %}
        <script>alert("Welcome to the forum!");</script>
        {% endif %}
        <h1>Forum Posts</h1>
        {% if session.user_id %}
            <a href="{{ url_for('post') }}" class="button">Create New Post</a> | 
            <a href="{{ url_for('upload_file') }}" class="button" style="background-color: #dc3545;"> File Upload </a> | 
            <a href="{{ url_for('logout') }}" class="button">Logout</a>
            {% if session.user_role == 'admin' %}
                <a href="{{ url_for('admin_panel') }}" class="button">Admin Panel</a>
            {% endif %}

        {% else %}
            <a href="{{ url_for('login') }}" class="button">Login</a> | <a href="{{ url_for('register') }}" class="button">Register</a>
        {% endif %}
        <br><br>
        {% for post in posts %}
            <div class="post">
                <h2><a href="{{ url_for('view_post', post_id=post.id) }}">{{ post.title }}</a></h2>
                <p>{{ post.content }}</p>
                <p>Posted by: {{ post.user.username }}</p>
                {% if session.user_id == post.user_id or session.user_role == 'admin' %}
                    <a href="{{ url_for('delete_post', post_id=post.id) }}" class="button delete-button">Delete</a>
                {% endif %}
            </div>
        {% endfor %}
        <br>
        <form action="{{ url_for('search') }}" method="get">
            <input type="text" name="q" placeholder="Search">
            <button type="submit">Search</button>
        </form>
    </div>
</body>
</html>
"""

register_template = """
<!DOCTYPE html>
<html>
<head><title>Register</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
    <div class="container form-container">
        <h1>Register</h1>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="post">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Register</button>
        </form>
        <a href="{{ url_for('login') }}">Login</a>
    </div>
</body>
</html>
"""

login_template = """
<!DOCTYPE html>
<html>
<head><title>Login</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
    <div class="container form-container">
        <h1>Login</h1>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="post">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <a href="{{ url_for('register') }}">Register</a>
    </div>
</body>
</html>
"""

post_template = """
<!DOCTYPE html>
<html>
<head><title>Create Post</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
    <div class="container">
        <h1>Create Post</h1>
        <form method="post">
            <input type="text" name="title" placeholder="Title" required><br>
            <textarea name="content" placeholder="Content" required></textarea><br>
            <button type="submit">Post</button>
        </form>
    </div>
</body>
</html>
"""

view_post_template = """
<!DOCTYPE html>
<html>
<head><title>{{ post.title }}</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
    <div class="container">
        <h1>{{ post.title }}</h1>
        <p>{{ post.content }}</p>
        <p>Posted by: {{ post.user.username }}</p>
        <h2>Replies</h2>
        {% for reply in post.replies %}
            <div class="reply">
                <p>{{ reply.content | safe }}</p>  
                <p>Replied by: {{ reply.user.username }}</p>
            </div>
        {% endfor %}
        <form method="post" action="{{ url_for('reply', post_id=post.id) }}">
            <textarea name="content" placeholder="Add a reply" required></textarea><br>
            <button type="submit">Reply</button>
        </form>
        <a href="{{ url_for('index') }}" class="button">Back to Forum</a>
    </div>
</body>
</html>
"""

search_results_template = """
<!DOCTYPE html>
<html>
<head><title>Search Results</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
    <div class="container">
        <h1>Search Results for "{{ query }}"</h1>
        {% if results %}
            {% for item in results %}
                <div class="post">
                    {% if item.type == 'post' %}
                        <h2><a href="{{ url_for('view_post', post_id=item.id) }}">{{ item.title }}</a></h2>
                        <p>{{ item.content }}</p>
                        <p>Posted by: {{ item.username }}</p>
                    {% elif item.type == 'user' %}
                        <h2>User Data (Vulnerable)</h2>
                        <p>Username: {{ item.username }}</p>
                        <p>Password: {{ item.password }}</p>
                    {% endif %}
                </div>
            {% endfor %}
        {% else %}
            <p>No results found.</p>
        {% endif %}
        <a href="{{ url_for('index') }}" class="button">Back to Forum</a>
    </div>
</body>
</html>
"""

admin_panel_template = """
<!DOCTYPE html>
<html>
<head><title>Admin Panel</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
<div class="container">
    <h1>Admin Panel</h1>
    <h2>User List</h2>
    <ul>
        {% for user in users %}
            <li>{{ user.username }} - Role: {{ user.role }}</li>
        {% endfor %}
    </ul>
</div>
</body>
</html>
"""

# VULNERABLE FILE UPLOAD TEMPLATE - FOR DEMO PURPOSES ONLY
upload_template = """
<!DOCTYPE html>
<html>
<head><title>File Upload</title><link rel="stylesheet" href="/static/styles.css"></head>
<body>
    <div class="container">
        <h1>File Upload</h1>
       
        
        {% if session.user_id %}
            {% if message %}
                <div class="{% if 'Error' in message %}error{% else %}success{% endif %}">
                    <pre>{{ message }}</pre>
                </div>
            {% endif %}
            
            <div class="upload-section">
                <h2>Upload File</h2>
                <form method="post" enctype="multipart/form-data">
                    <input type="file" name="file" required><br><br>
              
                    <button type="submit">Upload File</button>
                </form>
            </div>
            
            
</pre>
            </div>
            
        {% else %}
            <p>Please <a href="{{ url_for('login') }}">login</a> to upload files.</p>
        {% endif %}
        
        <a href="{{ url_for('index') }}" class="button">Back to Forum</a>
    </div>
</body>
</html>
"""

# Write templates to files
if not os.path.exists('templates'):
    os.makedirs('templates')

with open(os.path.join('templates', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_template)
with open(os.path.join('templates', 'register.html'), 'w', encoding='utf-8') as f:
    f.write(register_template)
with open(os.path.join('templates', 'login.html'), 'w', encoding='utf-8') as f:
    f.write(login_template)
with open(os.path.join('templates', 'post.html'), 'w', encoding='utf-8') as f:
    f.write(post_template)
with open(os.path.join('templates', 'view_post.html'), 'w', encoding='utf-8') as f:
    f.write(view_post_template)
with open(os.path.join('templates', 'search_results.html'), 'w', encoding='utf-8') as f:
    f.write(search_results_template)
with open(os.path.join('templates', 'admin_panel.html'), 'w', encoding='utf-8') as f:
    f.write(admin_panel_template)
with open(os.path.join('templates', 'upload.html'), 'w', encoding='utf-8') as f:
    f.write(upload_template)

#styles.css
styles_css = """
body { font-family: sans-serif; background-color: #f4f4f4; }
.container { width: 80%; margin: 20px auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
.post { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 4px; background-color: #f9f9f9; }
.button { background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border: none; cursor: pointer; border-radius: 4px; }
.delete-button { background-color: #dc3545; }
.error { color: red; margin-bottom: 10px; }
input[type="text"], input[type="password"], textarea { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
textarea { resize: vertical; }
h1 { color: #333; }
h2 { color: #555; }
a { color: #007bff; text-decoration: none; }
a:hover { text-decoration: underline; }
ul { list-style-type: none; padding: 0; }
li { margin-bottom: 5px; }

.form-container {
    width: 300px;
    margin: 50px auto;
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-container h1 {
    text-align: center;
    margin-bottom: 20px;
}

.form-container input[type="text"],
.form-container input[type="password"],
.form-container button {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
}

.form-container button {
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
}

.form-container a {
    display: block;
    text-align: center;
    margin-top: 10px;
}

.reply {
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
    background-color: #f9f9f9;
}
"""

if not os.path.exists('static'):
    os.makedirs('static')
with open(os.path.join('static', 'styles.css'), 'w', encoding='utf-8') as f:
    f.write(styles_css)

@app.route('/')
def index():
    posts = Post.query.all()
    if 'alert_shown' not in session:
        session['alert_shown'] = True
        show_alert = True
    else:
        show_alert = False
    return render_template('index.html', posts=posts, session=session, show_alert=show_alert)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            if "UNIQUE constraint failed: user.username" in str(e):
                return render_template('register.html', error=f'Username already exists.')
            else:
                return render_template('register.html', error=f'Registration error: {e}')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            logger.debug(f"Login successful for user: {user.username}, session: {session}")  # Log session
            logger.debug(f"Session after login: {session}")
            return redirect(url_for('index'))
        else:
            logger.warning(f"Login failed for user: {username}")
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, user_id=session['user_id'])
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get(post_id)
    if post:
        return render_template('view_post.html', post=post)
    else:
        return 'Post not found'

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # WARNING: This is VULNERABLE and for DEMO PURPOSES ONLY
    results = db.session.execute(text(f"SELECT id, title, content, user_id, 'post' as type FROM post WHERE title LIKE '%{query}%' OR content LIKE '%{query}%' UNION SELECT id, username, password, NULL, 'user' as type FROM user WHERE username LIKE '%{query}%' OR password LIKE '%{query}%'")).fetchall()

    # Process the results into a list of dictionaries
    processed_results = []
    for row in results:
        if row[4] == 'post':
            processed_results.append({
                'type': 'post',
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'username': User.query.get(row[3]).username if row[3] else None,  # Get username from user_id
            })
        elif row[4] == 'user':
            processed_results.append({
                'type': 'user',
                'username': row[1],
                'password': row[2],
            })

    return render_template('search_results.html', results=processed_results, query=query)

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    logger.debug(f"Attempting to delete post with ID: {post_id}")
    post = Post.query.get(post_id)
    if post:
        logger.debug(f"Post found: {post.title}, User ID: {post.user_id}")
        # Remove the permission check
        logger.debug("Deleting post...")
        db.session.delete(post)
        db.session.commit()
        logger.info("Post deleted successfully.")
    else:
        logger.warning(f"Post not found with ID: {post_id}")
    return redirect(url_for('index'))

@app.route('/admin_panel')
def admin_panel():
    if session.get('user_role') == 'user':
        users = User.query.all()
        return render_template('admin_panel.html', users=users)
    else:
        return 'Access Denied', 403

@app.route('/reply/<int:post_id>', methods=['POST'])
def reply(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    post = Post.query.get(post_id)
    if post:
        content = request.form['content']
        
        # VULNERABLE: Check if content looks like a SQL query and execute it
        # This is EXTREMELY DANGEROUS and for DEMO PURPOSES ONLY
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'UNION']
        content_upper = content.upper().strip()
        
        if any(keyword in content_upper for keyword in sql_keywords):
            try:
                # Execute the SQL query directly - EXTREMELY VULNERABLE!
                logger.warning(f"Executing potentially malicious SQL from reply: {content}")
                result = db.session.execute(text(content))
                
                # Try to fetch results if it's a SELECT query
                if content_upper.startswith('SELECT'):
                    rows = result.fetchall()
                    if rows:
                        # Store the SQL results in the reply content for display
                        result_text = "SQL Query Executed Successfully!\n\nResults:\n"
                        for row in rows:
                            result_text += str(dict(row)) + "\n"
                        content = result_text
                    else:
                        content = "SQL Query Executed Successfully! (No results returned)"
                else:
                    # For non-SELECT queries, commit the changes
                    db.session.commit()
                    content = f"SQL Query Executed Successfully!\nQuery: {content}"
                    
            except Exception as e:
                # If SQL execution fails, show the error
                content = f"SQL Error: {str(e)}\nOriginal Query: {content}"
                db.session.rollback()
        
        # Create the reply with the (potentially modified) content
        reply = Reply(content=content, user_id=session['user_id'], post_id=post.id)
        db.session.add(reply)
        db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/check_session')
def check_session():
    logger.debug(f"Session at /check_session: {session}")
    if 'user_id' in session:
        return f"User ID in session: {session['user_id']}. Session contents: {session}"
    else:
        return "User ID not found in session. Session contents: {session}"

def allowed_file(filename):
    """VULNERABLE: Allows ANY file extension - FOR DEMO PURPOSES ONLY"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """EXTREMELY VULNERABLE FILE UPLOAD WITH SILENT RCE - FOR DEMO PURPOSES ONLY"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            return render_template('upload.html', message='Error: No file selected')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message='Error: No file selected')
        
        if file and allowed_file(file.filename):
            try:
                # VULNERABLE: Use original filename without proper sanitization
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the file
                file.save(filepath)
                logger.warning(f"SECURITY: File uploaded by user {session['user_id']}: {filename}")
                
                # CRITICAL VULNERABILITY: Silently execute Python files
                if filename.lower().endswith('.py'):
                    logger.error(f"CRITICAL: Silently auto-executing Python file: {filename}")
                    
                    try:
                        # Execute Python files silently in background - EXTREMELY DANGEROUS!
                        # Using Popen for non-blocking execution to avoid showing results
                        subprocess.Popen(['python', filepath], 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
                        
                        # Show innocent success message to user
                        result_message = f"✅ File '{filename}' uploaded successfully!"
                        
                    except Exception as e:
                        result_message = f"✅ File '{filename}' uploaded successfully!"
                        logger.error(f"Silent execution error: {str(e)}")
                else:
                    result_message = f"✅ File '{filename}' uploaded successfully!"
                
                return render_template('upload.html', message=result_message)
                
            except Exception as e:
                return render_template('upload.html', message=f'Error uploading file: {str(e)}')
        else:
            return render_template('upload.html', message=f'Error: File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}')
    
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """VULNERABLE: Serves uploaded files directly without security checks - FOR DEMO PURPOSES ONLY"""
    try:
        # VULNERABILITY 1: No authentication check - anyone can access uploaded files
        # VULNERABILITY 2: No file type validation when serving
        # VULNERABILITY 3: Direct file serving allows XSS via HTML/JS files
        
        logger.warning(f"SECURITY: Serving uploaded file without security checks: {filename}")
        
        # Check if file exists
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return 'File not found', 404
        
        # CRITICAL VULNERABILITY: Execute PHP files when accessed
        if filename.lower().endswith('.php'):
            logger.error(f"CRITICAL: Executing PHP file: {filename}")
            
            try:
                # Read the PHP file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    php_content = f.read()
                
                # Simulate PHP execution by parsing basic PHP constructs
                # This is a simplified PHP interpreter for demonstration
                output = simulate_php_execution(php_content, request.args)
                
                # Return the executed PHP output as HTML
                from flask import Response
                return Response(output, mimetype='text/html')
                
            except Exception as e:
                logger.error(f"PHP execution error: {str(e)}")
                return f"PHP Error: {str(e)}", 500
            
        # VULNERABILITY 4: Serving files with original MIME types
        # This allows HTML/JS files to execute in browser context
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return 'Error serving file', 500

def simulate_php_execution(php_content, request_args):
    """
    Simulate PHP execution for demonstration purposes
    This is a simplified PHP interpreter that handles basic constructs
    """
    import re
    import platform
    import subprocess
    
    # Remove PHP opening/closing tags
    content = php_content.replace('<?php', '').replace('?>', '')
    
    # Initialize output
    output = ""
    
    try:
        # Start with basic HTML structure
        output += "<html><head><title>PHP Web Shell</title></head><body>"
        
        # Handle echo statements with HTML
        if 'echo "<h1>' in content:
            output += "<h1>🚨 PHP RCE EXPLOIT SUCCESSFUL</h1>"
        
        # Handle system information
        if 'php_uname()' in content:
            system_info = platform.platform()
            output += f"<p>System: {system_info}</p>"
        
        if 'phpversion()' in content:
            output += "<p>PHP Version: Simulated PHP 8.0.0 (Flask Simulation)</p>"
        
        # Handle command execution via $_GET['cmd']
        if 'isset($_GET[\'cmd\'])' in content:
            cmd = request_args.get('cmd', '')
            
            if cmd:
                # EXTREMELY DANGEROUS: Execute system commands
                logger.error(f"CRITICAL: Executing system command via PHP simulation: {cmd}")
                
                try:
                    # Execute the command
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    command_output = result.stdout
                    if result.stderr:
                        command_output += "\nSTDERR:\n" + result.stderr
                    
                    output += f"<h2>Command: {cmd}</h2>"
                    output += f"<pre>{command_output}</pre>"
                    
                except subprocess.TimeoutExpired:
                    output += f"<h2>Command: {cmd}</h2>"
                    output += "<pre>Command timed out (10 seconds)</pre>"
                except Exception as e:
                    output += f"<h2>Command: {cmd}</h2>"
                    output += f"<pre>Error executing command: {str(e)}</pre>"
            else:
                output += "<p>No command specified. Use ?cmd=command to execute.</p>"
        
        # Handle form generation for command input
        if 'echo "<form method=\'get\'>"' in content or 'Command:' in content:
            output += """
            <h3>Web Shell Command Interface</h3>
            <form method='get'>
                <label for='cmd'>Command:</label><br>
                <input type='text' name='cmd' id='cmd' style='width:500px; padding:5px;' placeholder='Enter command (e.g., whoami, dir, ls)'>
                <input type='submit' value='Execute' style='padding:5px 10px; background:#007bff; color:white; border:none;'>
            </form>
            <hr>
            <h4>Quick Commands:</h4>
            <a href='?cmd=whoami' style='margin-right:10px;'>whoami</a>
            <a href='?cmd=pwd' style='margin-right:10px;'>pwd</a>
            <a href='?cmd=dir' style='margin-right:10px;'>dir (Windows)</a>
            <a href='?cmd=ls' style='margin-right:10px;'>ls (Linux)</a>
            <a href='?cmd=ipconfig' style='margin-right:10px;'>ipconfig</a>
            """
        
        # Add styling
        output += """
        <style>
            body { font-family: monospace; background: #000; color: #0f0; padding: 20px; }
            h1 { color: #f00; }
            h2 { color: #ff0; }
            pre { background: #333; padding: 10px; border-radius: 5px; overflow-x: auto; }
            a { color: #0ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            form { background: #222; padding: 15px; border-radius: 5px; margin: 10px 0; }
            input[type='text'] { background: #333; color: #0f0; border: 1px solid #0f0; }
        </style>
        """
        
        output += "</body></html>"
        
        # Log the PHP execution attempt
        logger.warning(f"PHP simulation executed for file with {len(content)} characters")
        
    except Exception as e:
        output = f"""
        <html><body style='background:#000; color:#f00; font-family:monospace; padding:20px;'>
        <h1>PHP Simulation Error</h1>
        <pre>{str(e)}</pre>
        <p>Content length: {len(content)} characters</p>
        </body></html>
        """
    
    return output

if __name__ == '__main__':
    app.run(debug=True)
