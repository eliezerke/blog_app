from routes import web_routes
from models.models import *
from app.master import *
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin():
    """Create default admin if none exists."""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    if not User.query.filter_by(is_admin=True).first():
        admin = User(name='Admin', email=admin_email, is_admin=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin created: {admin_email} / {admin_password}")

app = app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()

    app.run(debug=True, host="0.0.0.0", port=7000)