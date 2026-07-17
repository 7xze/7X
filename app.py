#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""7X — Flask CMS with Admin Panel (Arabic/English)"""

import os
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, g
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "7x-syria-secret-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------- Database Models --------------------

class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value_ar = db.Column(db.Text, nullable=False, default="")
    value_en = db.Column(db.Text, nullable=False, default="")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), default="")
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# -------------------- Default Content --------------------

DEFAULT_CONTENT = {
    "hero_title": {
        "ar": "7X",
        "en": "7X"
    },
    "hero_subtitle": {
        "ar": "بناء تقنية آمنة ومفتوحة المصدر لسوريا والعالم",
        "en": "Building secure, open-source technology for Syria and beyond"
    },
    "hero_badge": {
        "ar": "نواة الهندسة الذكية",
        "en": "Engineering Intelligence Core"
    },
    "about_title": {
        "ar": "مَهندس. مؤسس. صاحب رؤية",
        "en": "Engineer. Founder. Visionary."
    },
    "about_text": {
        "ar": "أنا مؤسس <strong>7X Syria Ltd.</strong> — شركة تقنية سورية مكرّسة لبناء أدوات تواصل آمنة ومفتوحة المصدر. أركز على تطبيقات Android المشفّرة وبروتوكول Matrix.",
        "en": "I am the founder of <strong>7X Syria Ltd.</strong> — a Syrian technology company dedicated to building secure, open-source communication tools."
    },
    "company_title": {
        "ar": "شركة 7X سوريا",
        "en": "7X Syria Ltd."
    },
    "company_desc": {
        "ar": "نواة الهندسة الذكية — نبني تقنية آمنة لمستقبل متصل.",
        "en": "Engineering Intelligence Core — Building secure technology for a connected future."
    },
    "footer_text": {
        "ar": "7X Syria Ltd. — صنع في سوريا",
        "en": "7X Syria Ltd. — Made in Syria"
    },
    "contact_email": {
        "ar": "contact@7xsyria.com",
        "en": "contact@7xsyria.com"
    },
    "contact_matrix": {
        "ar": "@7x:matrix.org",
        "en": "@7x:matrix.org"
    },
    "contact_github": {
        "ar": "github.com/7xze",
        "en": "github.com/7xze"
    },
}

def init_content():
    for key, vals in DEFAULT_CONTENT.items():
        existing = SiteContent.query.get(key)
        if not existing:
            db.session.add(SiteContent(
                key=key,
                value_ar=vals["ar"],
                value_en=vals["en"]
            ))
    db.session.commit()

def init_admin():
    if not AdminUser.query.first():
        db.session.add(AdminUser(
            username="admin",
            password_hash=generate_password_hash("admin123")
        ))
        db.session.commit()

# -------------------- Helpers --------------------

def get_content(key):
    c = SiteContent.query.get(key)
    if c:
        return c
    vals = DEFAULT_CONTENT.get(key, {"ar": "", "en": ""})
    return SiteContent(key=key, value_ar=vals["ar"], value_en=vals["en"])

def get_lang():
    return session.get("lang", "ar")

def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*a, **kw)
    return wrapper

# -------------------- Routes: Site --------------------

@app.route("/")
def index():
    lang = get_lang()
    site = {k: get_content(k) for k in DEFAULT_CONTENT}
    return render_template("index.html", lang=lang, site=site)

@app.route("/set-lang/<lang>")
def set_lang(lang):
    if lang in ("ar", "en"):
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    body = request.form.get("message", "").strip()

    if not name or not email or not body:
        flash("يرجى ملء جميع الحقول المطلوبة" if get_lang() == "ar" else "Please fill all required fields", "error")
        return redirect(url_for("index"))

    msg = Message(name=name, email=email, subject=subject, body=body)
    db.session.add(msg)
    db.session.commit()

    flash("تم إرسال رسالتك بنجاح!" if get_lang() == "ar" else "Your message has been sent!", "success")
    return redirect(url_for("index"))

# -------------------- Routes: Admin --------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = AdminUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        flash("اسم مستخدم أو كلمة مرور خاطئة" if get_lang() == "ar" else "Invalid username or password", "error")
    return render_template("admin/login.html", lang=get_lang())

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    unread = sum(1 for m in messages if not m.read)
    return render_template("admin/dashboard.html", lang=get_lang(),
                           messages=messages, unread=unread)

@app.route("/admin/messages")
@admin_required
def admin_messages():
    msgs = Message.query.order_by(Message.created_at.desc()).all()
    return render_template("admin/messages.html", lang=get_lang(), messages=msgs)

@app.route("/admin/message/<int:mid>/read", methods=["POST"])
@admin_required
def mark_read(mid):
    msg = Message.query.get_or_404(mid)
    msg.read = True
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/admin/message/<int:mid>/delete", methods=["POST"])
@admin_required
def delete_message(mid):
    msg = Message.query.get_or_404(mid)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/admin/content", methods=["GET", "POST"])
@admin_required
def admin_content():
    if request.method == "POST":
        for key in DEFAULT_CONTENT:
            ar_val = request.form.get(f"{key}_ar", "")
            en_val = request.form.get(f"{key}_en", "")
            c = SiteContent.query.get(key)
            if c:
                c.value_ar = ar_val
                c.value_en = en_val
        db.session.commit()
        flash("تم حفظ المحتوى!" if get_lang() == "ar" else "Content saved!", "success")
        return redirect(url_for("admin_content"))

    contents = {k: get_content(k) for k in DEFAULT_CONTENT}
    return render_template("admin/content.html", lang=get_lang(), contents=contents)

# -------------------- Init --------------------

with app.app_context():
    db.create_all()
    init_content()
    init_admin()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
