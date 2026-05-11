# The Dispatch — Blog Platform

A clean, editorial blog platform built with Flask. Admin posts content, visitors read freely, signed-in users can like and comment.

## Features

- **Public** — Browse and read all posts (no account needed)
- **Members** — Like posts, leave comments and replies
- **Admin** — Create, edit, delete posts; view engagement stats
- **Auth** — Email/password signup + Google OAuth
- **Design** — Dark editorial theme, fully responsive

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Load env vars and run
```bash
# Option A: set vars directly
export SECRET_KEY="your-secret"
export ADMIN_EMAIL="admin@you.com"
export ADMIN_PASSWORD="yourpassword"
python app.py

# Option B: use python-dotenv
pip install python-dotenv
# Add this to the top of app.py:
# from dotenv import load_dotenv; load_dotenv()
python app.py
```

The app creates an admin account on first run and prints the credentials.

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → APIs & Services → Credentials
3. Create OAuth 2.0 Client ID (Web application)
4. Add authorized redirect URI: `http://localhost:5000/auth/google/callback`
5. Copy Client ID and Secret to your `.env`

For production, add your real domain as authorized redirect URI.

## Project Structure

```
blog_app/
├── app.py                    # Main Flask app, routes, models
├── requirements.txt
├── .env.example
├── templates/
│   ├── base.html             # Nav, flash, footer
│   ├── index.html            # Homepage with post grid
│   ├── post_detail.html      # Full article + comments
│   ├── login.html
│   ├── signup.html
│   ├── partials/
│   │   └── comment.html      # Comment component
│   ├── admin/
│   │   ├── dashboard.html    # Post management
│   │   └── post_form.html    # Create/edit post
│   └── errors/
│       ├── 403.html
│       └── 404.html
└── static/
    ├── css/main.css          # Full design system
    └── js/
        ├── main.js           # Nav, animations
        └── post.js           # Likes, comments (AJAX)
```

## Admin Usage

Visit `/admin` after logging in as admin.

- **New Post** — Title, content (HTML supported), excerpt, cover image URL, category, published toggle
- **Edit/Delete** — From the dashboard table
- Posts support full HTML in the content field (headings, links, blockquotes, code blocks)

## Production Checklist

- [ ] Change `SECRET_KEY` to a long random string
- [ ] Change `ADMIN_EMAIL` and `ADMIN_PASSWORD`  
- [ ] Use PostgreSQL instead of SQLite (`DATABASE_URL=postgresql://...`)
- [ ] Set `FLASK_ENV=production`
- [ ] Add HTTPS (required for Google OAuth in production)
- [ ] Update Google OAuth redirect URI to your domain
- [ ] Use gunicorn: `gunicorn app:app`
