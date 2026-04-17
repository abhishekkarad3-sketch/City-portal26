from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, hashlib, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'city_portal_2024_secret'
DB = 'city_portal.db'

# ── helpers ──────────────────────────────────────────────────────────────────
def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def hsh(p): return hashlib.sha256(p.encode()).hexdigest()

def current_user():
    if 'user_id' not in session: return None
    con = db()
    u = con.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    con.close(); return u

# ── init db ───────────────────────────────────────────────────────────────────
def init_db():
    con = db(); c = con.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            phone TEXT, password TEXT NOT NULL,
            role TEXT DEFAULT "user",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

        CREATE TABLE IF NOT EXISTS technicians(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, specialization TEXT NOT NULL,
            phone TEXT, email TEXT, bio TEXT,
            experience INTEGER DEFAULT 1,
            rating REAL DEFAULT 0, review_count INTEGER DEFAULT 0,
            available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, technician_id INTEGER NOT NULL,
            service_date TEXT NOT NULL, service_time TEXT NOT NULL,
            address TEXT, notes TEXT,
            status TEXT DEFAULT "pending",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(technician_id) REFERENCES technicians(id));

        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            sender TEXT NOT NULL, content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(booking_id) REFERENCES bookings(id));

        CREATE TABLE IF NOT EXISTS ratings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER UNIQUE NOT NULL,
            user_id INTEGER NOT NULL, technician_id INTEGER NOT NULL,
            stars INTEGER NOT NULL, feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    ''')
    # admin
    c.execute("INSERT OR IGNORE INTO users(name,email,phone,password,role) VALUES(?,?,?,?,?)",
              ('Admin','admin@cityportal.com','0000000000',hsh('admin123'),'admin'))
    c.execute("INSERT OR IGNORE INTO users(name,email,phone,password,role) VALUES(?,?,?,?,?)",
              ('Demo User','demo@city.com','9876543210',hsh('demo123'),'user'))
    # technicians
    techs = [
        ('Arjun Sharma','Electrician','9811001100','arjun@tech.com',
         'Licensed electrician with 10 years experience in residential & commercial wiring.',10,4.8,124,1),
        ('Priya Patel','Plumber','9822002200','priya@tech.com',
         'Expert plumber specializing in pipe fitting, leak repair, and bathroom installations.',7,4.6,98,1),
        ('Ravi Kumar','Internet Technician','9833003300','ravi@tech.com',
         'Certified network engineer handling broadband, fiber optics, and Wi-Fi setup.',5,4.7,76,1),
        ('Sneha Desai','Computer Repair','9844004400','sneha@tech.com',
         'Hardware/software specialist with expertise in laptops, desktops, and data recovery.',8,4.9,145,1),
        ('Vikram Singh','CCTV Installation','9855005500','vikram@tech.com',
         'Security systems expert with experience in home and office CCTV installation & monitoring.',6,4.5,63,1),
        ('Meera Joshi','Electrician','9866006600','meera@tech.com',
         'Specialist in solar panel installation and smart home electrical systems.',4,4.7,42,1),
        ('Suresh Nair','Plumber','9877007700','suresh@tech.com',
         'Expert in underground pipe repair, drainage systems, and water heater installation.',9,4.4,87,1),
        ('Kavita Rao','Internet Technician','9888008800','kavita@tech.com',
         'Telecom engineer with expertise in fiber optic installation and network troubleshooting.',3,4.6,35,1),
    ]
    for t in techs:
        c.execute("INSERT OR IGNORE INTO technicians(name,specialization,phone,email,bio,experience,rating,review_count,available) VALUES(?,?,?,?,?,?,?,?,?)", t)
    con.commit(); con.close()

init_db()

# ── auth ─────────────────────────────────────────────────────────────────────
@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = hsh(request.form['password'])
        con = db()
        u = con.execute('SELECT * FROM users WHERE email=? AND password=?',(email,password)).fetchone()
        con.close()
        if u:
            session['user_id'] = u['id']
            session['user_name'] = u['name']
            session['user_role'] = u['role']
            return redirect(url_for('admin_panel') if u['role']=='admin' else url_for('dashboard'))
        error = 'Invalid email or password'
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        name  = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        pwd   = hsh(request.form['password'])
        try:
            con = db()
            con.execute('INSERT INTO users(name,email,phone,password) VALUES(?,?,?,?)',(name,email,phone,pwd))
            con.commit()
            u = con.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
            con.close()
            session['user_id'] = u['id']
            session['user_name'] = u['name']
            session['user_role'] = u['role']
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            error = 'Email already registered'
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

# ── dashboard ─────────────────────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    con = db()
    techs = con.execute('SELECT * FROM technicians ORDER BY rating DESC').fetchall()
    bookings = con.execute('''SELECT b.*,t.name as tech_name,t.specialization
                              FROM bookings b JOIN technicians t ON b.technician_id=t.id
                              WHERE b.user_id=? ORDER BY b.created_at DESC LIMIT 5''',
                           (session['user_id'],)).fetchall()
    stats = {
        'total': con.execute('SELECT COUNT(*) FROM bookings WHERE user_id=?',(session['user_id'],)).fetchone()[0],
        'pending': con.execute("SELECT COUNT(*) FROM bookings WHERE user_id=? AND status='pending'",(session['user_id'],)).fetchone()[0],
        'completed': con.execute("SELECT COUNT(*) FROM bookings WHERE user_id=? AND status='completed'",(session['user_id'],)).fetchone()[0],
    }
    con.close()
    return render_template('dashboard.html', techs=techs, bookings=bookings, stats=stats, user=current_user())

# ── technicians ───────────────────────────────────────────────────────────────
@app.route('/services')
def services():
    if 'user_id' not in session: return redirect(url_for('login'))
    q = request.args.get('q','')
    cat = request.args.get('cat','')
    sort = request.args.get('sort','rating')
    con = db()
    query = 'SELECT * FROM technicians WHERE available=1'
    params = []
    if q:
        query += ' AND (name LIKE ? OR specialization LIKE ? OR bio LIKE ?)'
        params += [f'%{q}%',f'%{q}%',f'%{q}%']
    if cat:
        query += ' AND specialization=?'; params.append(cat)
    order = {'rating':'rating DESC','name':'name ASC','exp':'experience DESC'}.get(sort,'rating DESC')
    query += f' ORDER BY {order}'
    techs = con.execute(query, params).fetchall()
    cats = [r[0] for r in con.execute('SELECT DISTINCT specialization FROM technicians').fetchall()]
    con.close()
    return render_template('services.html', techs=techs, cats=cats, q=q, cat=cat, sort=sort, user=current_user())

# ── booking ───────────────────────────────────────────────────────────────────
@app.route('/book/<int:tech_id>', methods=['GET','POST'])
def book(tech_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    con = db()
    tech = con.execute('SELECT * FROM technicians WHERE id=?',(tech_id,)).fetchone()
    if not tech:
        con.close(); return redirect(url_for('services'))
    success = None
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        addr = request.form['address']
        notes= request.form.get('notes','')
        con.execute('INSERT INTO bookings(user_id,technician_id,service_date,service_time,address,notes) VALUES(?,?,?,?,?,?)',
                    (session['user_id'],tech_id,date,time,addr,notes))
        bid = con.execute('SELECT last_insert_rowid()').fetchone()[0]
        con.execute("INSERT INTO messages(booking_id,sender,content) VALUES(?,?,?)",
                    (bid,'system',f'Booking confirmed for {date} at {time}. Technician {tech["name"]} will visit you at the given address.'))
        con.commit()
        success = bid
    con.close()
    return render_template('book.html', tech=tech, success=success, user=current_user())

# ── my bookings ───────────────────────────────────────────────────────────────
@app.route('/bookings')
def bookings():
    if 'user_id' not in session: return redirect(url_for('login'))
    con = db()
    bks = con.execute('''SELECT b.*,t.name as tech_name,t.specialization,t.phone as tech_phone
                         FROM bookings b JOIN technicians t ON b.technician_id=t.id
                         WHERE b.user_id=? ORDER BY b.created_at DESC''',(session['user_id'],)).fetchall()
    rated = {r['booking_id'] for r in con.execute('SELECT booking_id FROM ratings WHERE user_id=?',(session['user_id'],)).fetchall()}
    con.close()
    return render_template('bookings.html', bookings=bks, rated=rated, user=current_user())

# ── messages ──────────────────────────────────────────────────────────────────
@app.route('/messages/<int:booking_id>')
def messages(booking_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    con = db()
    bk = con.execute('''SELECT b.*,t.name as tech_name FROM bookings b
                        JOIN technicians t ON b.technician_id=t.id WHERE b.id=?''',(booking_id,)).fetchone()
    if not bk or bk['user_id'] != session['user_id']:
        con.close(); return redirect(url_for('bookings'))
    msgs = con.execute('SELECT * FROM messages WHERE booking_id=? ORDER BY created_at',(booking_id,)).fetchall()
    con.close()
    return render_template('messages.html', booking=bk, msgs=msgs, user=current_user())

# ── rating ────────────────────────────────────────────────────────────────────
@app.route('/rate/<int:booking_id>', methods=['GET','POST'])
def rate(booking_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    con = db()
    bk = con.execute('''SELECT b.*,t.name as tech_name FROM bookings b
                        JOIN technicians t ON b.technician_id=t.id WHERE b.id=?''',(booking_id,)).fetchone()
    existing = con.execute('SELECT * FROM ratings WHERE booking_id=?',(booking_id,)).fetchone()
    if request.method == 'POST' and not existing:
        stars = int(request.form['stars'])
        feedback = request.form.get('feedback','')
        con.execute('INSERT INTO ratings(booking_id,user_id,technician_id,stars,feedback) VALUES(?,?,?,?,?)',
                    (booking_id,session['user_id'],bk['technician_id'],stars,feedback))
        # update technician avg rating
        avg = con.execute('SELECT AVG(stars),COUNT(*) FROM ratings WHERE technician_id=?',(bk['technician_id'],)).fetchone()
        con.execute('UPDATE technicians SET rating=?,review_count=? WHERE id=?',(round(avg[0],1),avg[1],bk['technician_id']))
        con.commit(); con.close()
        return redirect(url_for('bookings'))
    con.close()
    return render_template('rate.html', booking=bk, existing=existing, user=current_user())

# ── profile ───────────────────────────────────────────────────────────────────
@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    con = db()
    u = con.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone()
    success = None
    if request.method == 'POST':
        name  = request.form['name'].strip()
        phone = request.form['phone'].strip()
        con.execute('UPDATE users SET name=?,phone=? WHERE id=?',(name,phone,session['user_id']))
        con.commit()
        session['user_name'] = name
        success = True
        u = con.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone()
    history = con.execute('''SELECT b.*,t.name as tech_name,t.specialization
                             FROM bookings b JOIN technicians t ON b.technician_id=t.id
                             WHERE b.user_id=? ORDER BY b.created_at DESC''',(session['user_id'],)).fetchall()
    con.close()
    return render_template('profile.html', u=u, history=history, success=success, user=current_user())

# ── admin ─────────────────────────────────────────────────────────────────────
@app.route('/admin')
def admin_panel():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    con = db()
    techs = con.execute('SELECT * FROM technicians ORDER BY id').fetchall()
    users = con.execute("SELECT * FROM users WHERE role='user' ORDER BY id").fetchall()
    bookings = con.execute('''SELECT b.*,u.name as user_name,t.name as tech_name,t.specialization
                              FROM bookings b JOIN users u ON b.user_id=u.id
                              JOIN technicians t ON b.technician_id=t.id
                              ORDER BY b.created_at DESC''').fetchall()
    ratings = con.execute('''SELECT r.*,u.name as user_name,t.name as tech_name
                             FROM ratings r JOIN users u ON r.user_id=u.id
                             JOIN technicians t ON r.technician_id=t.id
                             ORDER BY r.created_at DESC''').fetchall()
    stats = {
        'users': con.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0],
        'techs': con.execute('SELECT COUNT(*) FROM technicians').fetchone()[0],
        'bookings': con.execute('SELECT COUNT(*) FROM bookings').fetchone()[0],
        'pending': con.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'").fetchone()[0],
    }
    con.close()
    return render_template('admin.html', techs=techs, users=users, bookings=bookings, ratings=ratings, stats=stats)

@app.route('/admin/add_tech', methods=['POST'])
def add_tech():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    con = db()
    con.execute('INSERT INTO technicians(name,specialization,phone,email,bio,experience) VALUES(?,?,?,?,?,?)',
                (request.form['name'],request.form['spec'],request.form['phone'],
                 request.form['email'],request.form['bio'],int(request.form['exp'])))
    con.commit(); con.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/update_booking', methods=['POST'])
def update_booking():
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    bid = request.form['booking_id']
    status = request.form['status']
    con = db()
    con.execute('UPDATE bookings SET status=? WHERE id=?',(status,bid))
    con.execute("INSERT INTO messages(booking_id,sender,content) VALUES(?,?,?)",
                (bid,'technician',f'Your booking status has been updated to: {status.upper()}'))
    con.commit(); con.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_tech/<int:tid>')
def delete_tech(tid):
    if session.get('user_role') != 'admin': return redirect(url_for('login'))
    con = db(); con.execute('DELETE FROM technicians WHERE id=?',(tid,)); con.commit(); con.close()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)