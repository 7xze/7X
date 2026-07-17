#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""7X — Local Admin Panel"""

import os
import json
import subprocess
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__, template_folder="admin_templates")
app.secret_key = "7x-admin-secret-key"

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_FILE = os.path.join(REPO_DIR, "content.json")
ADMIN_PASS = "admin123"

CONTENT_KEYS = {
    "hero_title": {"ar": "عنوان الرئيسية", "en": "Hero Title"},
    "hero_badge": {"ar": "الشارة", "en": "Hero Badge"},
    "hero_subtitle": {"ar": "الوصف", "en": "Hero Subtitle"},
    "about_title": {"ar": "عنوان من أنا", "en": "About Title"},
    "about_text": {"ar": "نص من أنا", "en": "About Text"},
    "company_title": {"ar": "عنوان الشركة", "en": "Company Title"},
    "company_desc": {"ar": "وصف الشركة", "en": "Company Description"},
    "footer_text": {"ar": "نص التذييل", "en": "Footer Text"},
}


def load_content():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_content(data):
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("كلمة مرور خاطئة" if session.get("lang", "ar") == "ar" else "Wrong password", "error")
    return render_template("login.html", lang=session.get("lang", "ar"))


@app.route("/admin/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/admin/set-lang/<lang>")
def set_lang(lang):
    if lang in ("ar", "en"):
        session["lang"] = lang
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/admin")
@admin_required
def dashboard():
    return render_template("dashboard.html", lang=session.get("lang", "ar"))


@app.route("/admin/content", methods=["GET", "POST"])
@admin_required
def content():
    lang = session.get("lang", "ar")
    if request.method == "POST":
        data = load_content()
        for key in CONTENT_KEYS:
            ar_val = request.form.get(f"{key}_ar", "").strip()
            en_val = request.form.get(f"{key}_en", "").strip()
            if ar_val or en_val:
                data[key] = {"ar": ar_val, "en": en_val}
        save_content(data)
        flash("تم حفظ المحتوى!" if lang == "ar" else "Content saved!", "success")
        return redirect(url_for("content"))

    data = load_content()
    return render_template("content.html", lang=lang, content=data, keys=CONTENT_KEYS)


@app.route("/admin/publish")
@admin_required
def publish():
    lang = session.get("lang", "ar")
    try:
        subprocess.run(["git", "add", "content.json", "index.html"], cwd=REPO_DIR, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Update site content via admin panel"], cwd=REPO_DIR, capture_output=True)
        result = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            flash("تم النشر! الموقع محدّث." if lang == "ar" else "Published! Site is updated.", "success")
        else:
            flash(f"خطأ في النشر: {result.stderr[:200]}" if lang == "ar" else f"Publish error: {result.stderr[:200]}", "error")
    except Exception as e:
        flash(f"خطأ: {str(e)[:200]}", "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  [7X Admin Panel] http://localhost:{port}/admin")
    print(f"  Password: {ADMIN_PASS}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
