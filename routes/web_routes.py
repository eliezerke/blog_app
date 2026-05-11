from models.models import User, Comment, Post, Like
from app.master import *

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    base = text
    counter = 1
    while Post.query.filter_by(slug=text).first():
        text = f"{base}-{counter}"
        counter += 1
    return text

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('signup'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'error')
            return redirect(url_for('signup'))
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Welcome! Your account has been created.', 'success')
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.password_hash and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out succesfully! Hope you'll be back soon.", "info")
    return redirect(url_for('index'))

@app.route('/auth/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        userinfo = token.get('userinfo')
        if not userinfo:
            flash('Google authentication failed.', 'error')
            return redirect(url_for('login'))

        email = userinfo.get('email', '').lower()
        google_id = userinfo.get('sub')
        name = userinfo.get('name', email.split('@')[0])
        avatar = userinfo.get('picture')

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                avatar=avatar,
                oauth_provider='google',
                oauth_id=google_id
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.avatar = avatar
            user.oauth_id = google_id
            db.session.commit()

        login_user(user)
        return redirect(url_for('index'))
    except Exception as e:
        flash('Google authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    query = Post.query.filter_by(published=True).order_by(Post.created_at.desc())
    if category:
        query = query.filter_by(category=category)
    posts = query.paginate(page=page, per_page=9)
    categories = db.session.query(Post.category).filter(
        Post.published == True, Post.category != None
    ).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('index.html', posts=posts, categories=categories, current_category=category)

@app.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).order_by(Comment.created_at.desc()).all()
    related = Post.query.filter(
        Post.category == post.category,
        Post.id != post.id,
        Post.published == True
    ).limit(3).all()
    return render_template('post_detail.html', post=post, comments=comments, related=related)

@app.route('/api/like/<int:post_id>', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'liked': False, 'count': post.like_count})
    like = Like(user_id=current_user.id, post_id=post_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({'liked': True, 'count': post.like_count})

@app.route('/api/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    if len(content) > 2000:
        return jsonify({'error': 'Comment too long'}), 400
    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'author_name': current_user.name,
        'author_avatar': current_user.avatar,
        'created_at': comment.created_at.strftime('%b %d, %Y'),
        'parent_id': comment.parent_id
    })


@app.route('/api/comment/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    total_likes = db.session.query(db.func.count(Like.id)).scalar()
    total_comments = db.session.query(db.func.count(Comment.id)).scalar()
    total_users = db.session.query(db.func.count(User.id)).scalar()
    return render_template('admin/dashboard.html', posts=posts,
                           total_likes=total_likes, total_comments=total_comments,
                           total_users=total_users)

@app.route('/admin/post/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_new_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        cover_image = request.form.get('cover_image', '').strip()
        category = request.form.get('category', '').strip()
        published = request.form.get('published') == 'on'

        if not title or not content:
            flash('Title and content are required.', 'error')
            return redirect(url_for('admin_new_post'))

        slug = slugify(title)
        post = Post(
            title=title, slug=slug, content=content,
            excerpt=excerpt or content[:200] + '...',
            cover_image=cover_image, category=category or None,
            published=published
        )
        db.session.add(post)
        db.session.commit()
        flash('Post published!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/post_form.html', post=None)

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form.get('title', '').strip()
        post.content = request.form.get('content', '').strip()
        post.excerpt = request.form.get('excerpt', '').strip()
        post.cover_image = request.form.get('cover_image', '').strip()
        post.category = request.form.get('category', '').strip() or None
        post.published = request.form.get('published') == 'on'
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/post_form.html', post=post)


@app.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/users/remove-admin", methods=['POST'])
def remove_admin():
    req = request.get_json()
    user_id = req.get('user_id')
    request_key = req.get('key')
    if request_key != Config.SECRET_KEY:
        abort(401)
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        abort(403)
    user.is_admin = False
    db.session.commit()
    return jsonify({'success': True})

@app.route("/admin/users/make-admin", methods=['POST'])
def make_admin():
    req = request.get_json()
    user_id = req.get('user_id')
    request_key = req.get('key')
    if request_key != Config.SECRET_KEY:
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        abort(403)
    user.is_admin = True
    db.session.commit()
    return jsonify({'success': True})

@app.route("/admin/list/users", methods=['POST'])
def list_users():
    request_key = request.get_json().get('key')
    if request_key != Config.SECRET_KEY:
        abort(401)
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email, 'is_admin': user.is_admin} for user in users])

@app.route("/admin/users/<int:user_id>/delete", methods=['POST'])
def delete_user(user_id):
    req = request.get_json()
    request_key = req.get('key')
    if request_key != Config.SECRET_KEY:
        abort(401)
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'message': 'Unauthorized request'}), 401

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500 