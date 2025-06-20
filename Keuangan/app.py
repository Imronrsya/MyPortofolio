from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import sqlite3
import os
from functools import wraps
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Database setup
def init_db():
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            color TEXT DEFAULT '#3498db',
            icon TEXT DEFAULT '💰'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            period TEXT DEFAULT 'monthly',
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            target_date DATE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert default categories if they don't exist
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        default_categories = [
            # Income categories
            ('Gaji', 'income', '#27ae60', '💼'),
            ('Freelance', 'income', '#2ecc71', '💻'),
            ('Investasi', 'income', '#16a085', '📈'),
            ('Bonus', 'income', '#f39c12', '🎁'),
            
            # Expense categories
            ('Makanan', 'expense', '#e74c3c', '🍽️'),
            ('Transportasi', 'expense', '#3498db', '🚗'),
            ('Belanja', 'expense', '#9b59b6', '🛍️'),
            ('Hiburan', 'expense', '#e67e22', '🎬'),
            ('Kesehatan', 'expense', '#1abc9c', '🏥'),
            ('Tagihan', 'expense', '#34495e', '📄'),
            ('Pendidikan', 'expense', '#f1c40f', '📚'),
        ]
        
        cursor.executemany(
            "INSERT INTO categories (name, type, color, icon) VALUES (?, ?, ?, ?)",
            default_categories
        )
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('finance_manager.db')
    conn.row_factory = sqlite3.Row
    return conn

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username atau email sudah digunakan', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get current month transactions
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Calculate total income and expenses for current month
    total_income = conn.execute('''
        SELECT COALESCE(SUM(t.amount), 0) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.type = 'income'
        AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?
    ''', (user_id, f'{current_month:02d}', str(current_year))).fetchone()['total']
    
    total_expense = conn.execute('''
        SELECT COALESCE(SUM(t.amount), 0) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.type = 'expense'
        AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?
    ''', (user_id, f'{current_month:02d}', str(current_year))).fetchone()['total']
    
    # Get recent transactions
    recent_transactions = conn.execute('''
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.created_at DESC
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    # Get budgets
    budgets = conn.execute('''
        SELECT b.*, c.name as category_name, c.icon as category_icon
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ?
    ''', (user_id,)).fetchall()
    
    # Calculate budget status
    budget_status = []
    for budget in budgets:
        spent = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE user_id = ? AND category_id = ?
            AND date >= ? AND date <= ?
        ''', (user_id, budget['category_id'], budget['start_date'], budget['end_date'])).fetchone()['total']
        
        percentage = (spent / budget['amount'] * 100) if budget['amount'] > 0 else 0
        budget_status.append({
            'budget': dict(budget),
            'spent': spent,
            'percentage': percentage
        })
    
    # Get goals
    goals = conn.execute('''
        SELECT * FROM goals WHERE user_id = ?
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=total_income - total_expense,
                         recent_transactions=recent_transactions,
                         budget_status=budget_status,
                         goals=goals)

@app.route('/transactions')
@login_required
def transactions():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get search parameters
    search_term = request.args.get('search_term', '').strip()
    category_id = request.args.get('search_category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    min_amount = request.args.get('min_amount', '')
    max_amount = request.args.get('max_amount', '')
    transaction_type = request.args.get('search_type', '')
    
    conn = get_db_connection()
    
    # Build query
    query = '''
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    '''
    count_query = '''
        SELECT COUNT(*) as count 
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    '''
    params = [user_id]
    
    # Add search filters
    if search_term:
        query += ' AND (t.description LIKE ? OR c.name LIKE ?)'
        count_query += ' AND (t.description LIKE ? OR c.name LIKE ?)'
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    if category_id:
        query += ' AND t.category_id = ?'
        count_query += ' AND t.category_id = ?'
        params.append(category_id)
    
    if date_from:
        query += ' AND t.date >= ?'
        count_query += ' AND t.date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND t.date <= ?'
        count_query += ' AND t.date <= ?'
        params.append(date_to)
    
    if min_amount:
        try:
            min_amt = float(min_amount)
            query += ' AND t.amount >= ?'
            count_query += ' AND t.amount >= ?'
            params.append(min_amt)
        except ValueError:
            pass
    
    if max_amount:
        try:
            max_amt = float(max_amount)
            query += ' AND t.amount <= ?'
            count_query += ' AND t.amount <= ?'
            params.append(max_amt)
        except ValueError:
            pass
    
    if transaction_type:
        query += ' AND c.type = ?'
        count_query += ' AND c.type = ?'
        params.append(transaction_type)
    
    # Add ordering and pagination
    query += ' ORDER BY t.date DESC, t.created_at DESC LIMIT ? OFFSET ?'
    
    # Execute queries
    transactions = conn.execute(query, params + [per_page, offset]).fetchall()
    total_count = conn.execute(count_query, params).fetchone()['count']
    
    # Get categories
    categories = conn.execute('SELECT * FROM categories ORDER BY type, name').fetchall()
    
    conn.close()
    
    # Simple pagination object
    class Pagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
    
    pagination = Pagination(page, per_page, total_count, transactions)
    
    return render_template('transactions.html', transactions=pagination, categories=categories)

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    user_id = session['user_id']
    
    try:
        # Validate input
        category_id = request.form.get('category_id')
        amount = request.form.get('amount')
        description = request.form.get('description', '')
        date_str = request.form.get('date')
        
        if not category_id or not amount or not date_str:
            flash('Semua field wajib harus diisi!', 'error')
            return redirect(url_for('transactions'))
        
        amount = float(amount)
        if amount <= 0:
            flash('Jumlah harus lebih besar dari 0!', 'error')
            return redirect(url_for('transactions'))
        
        # Validate date
        datetime.strptime(date_str, '%Y-%m-%d')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO transactions (user_id, category_id, amount, description, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            int(category_id),
            amount,
            description,
            date_str
        ))
        conn.commit()
        conn.close()
        
        flash('Transaksi berhasil ditambahkan!', 'success')
    except ValueError as e:
        flash('Format data tidak valid!', 'error')
    except Exception as e:
        flash('Terjadi kesalahan saat menyimpan transaksi!', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/budgets')
@login_required
def budgets():
    user_id = session['user_id']
    conn = get_db_connection()
    
    budgets = conn.execute('''
        SELECT b.*, c.name as category_name, c.icon as category_icon
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ?
    ''', (user_id,)).fetchall()
    
    categories = conn.execute('''
        SELECT * FROM categories WHERE type = 'expense' ORDER BY name
    ''').fetchall()
    
    conn.close()
    
    return render_template('budgets.html', budgets=budgets, categories=categories)

@app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    user_id = session['user_id']
    
    try:
        # Validate input
        category_id = request.form.get('category_id')
        amount = request.form.get('amount')
        period = request.form.get('period')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if not all([category_id, amount, period, start_date, end_date]):
            flash('Semua field wajib harus diisi!', 'error')
            return redirect(url_for('budgets'))
        
        amount = float(amount)
        if amount <= 0:
            flash('Jumlah budget harus lebih besar dari 0!', 'error')
            return redirect(url_for('budgets'))
        
        # Validate dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj >= end_date_obj:
            flash('Tanggal selesai harus setelah tanggal mulai!', 'error')
            return redirect(url_for('budgets'))
        
        # Validate period
        if period not in ['weekly', 'monthly', 'yearly']:
            flash('Periode tidak valid!', 'error')
            return redirect(url_for('budgets'))
        
        conn = get_db_connection()
        
        # Check if category exists and is expense type
        category = conn.execute('''
            SELECT id, type FROM categories WHERE id = ? AND type = 'expense'
        ''', (category_id,)).fetchone()
        
        if not category:
            flash('Kategori tidak valid!', 'error')
            conn.close()
            return redirect(url_for('budgets'))
        
        # Check if budget already exists for this category and period
        existing_budget = conn.execute('''
            SELECT id FROM budgets 
            WHERE user_id = ? AND category_id = ? 
            AND ((start_date <= ? AND end_date >= ?) OR (start_date <= ? AND end_date >= ?))
        ''', (user_id, category_id, start_date, start_date, end_date, end_date)).fetchone()
        
        if existing_budget:
            flash('Budget untuk kategori ini sudah ada pada periode tersebut!', 'error')
            conn.close()
            return redirect(url_for('budgets'))
        
        conn.execute('''
            INSERT INTO budgets (user_id, category_id, amount, period, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            int(category_id),
            amount,
            period,
            start_date,
            end_date
        ))
        conn.commit()
        conn.close()
        
        flash('Budget berhasil ditambahkan!', 'success')
        return redirect(url_for('budgets'))
        
    except ValueError as e:
        flash('Data tidak valid! Pastikan format angka dan tanggal benar.', 'error')
        return redirect(url_for('budgets'))
    except Exception as e:
        flash('Terjadi kesalahan saat menambahkan budget.', 'error')
        return redirect(url_for('budgets'))

@app.route('/goals')
@login_required
def goals():
    user_id = session['user_id']
    conn = get_db_connection()
    
    goals = conn.execute('''
        SELECT * FROM goals WHERE user_id = ?
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template('goals.html', goals=goals)

@app.route('/add_goal', methods=['POST'])
@login_required
def add_goal():
    user_id = session['user_id']
    
    try:
        # Validate input
        name = request.form.get('name', '').strip()
        target_amount = request.form.get('target_amount')
        target_date = request.form.get('target_date')
        description = request.form.get('description', '').strip()
        
        if not all([name, target_amount, target_date]):
            flash('Nama, jumlah target, dan tanggal target harus diisi!', 'error')
            return redirect(url_for('goals'))
        
        if len(name) < 3:
            flash('Nama target minimal 3 karakter!', 'error')
            return redirect(url_for('goals'))
        
        target_amount = float(target_amount)
        if target_amount <= 0:
            flash('Jumlah target harus lebih besar dari 0!', 'error')
            return redirect(url_for('goals'))
        
        # Validate target date
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        today = date.today()
        
        if target_date_obj <= today:
            flash('Tanggal target harus di masa depan!', 'error')
            return redirect(url_for('goals'))
        
        # Check if goal with same name already exists
        conn = get_db_connection()
        existing_goal = conn.execute('''
            SELECT id FROM goals WHERE user_id = ? AND LOWER(name) = LOWER(?)
        ''', (user_id, name)).fetchone()
        
        if existing_goal:
            flash('Goal dengan nama tersebut sudah ada!', 'error')
            conn.close()
            return redirect(url_for('goals'))
        
        conn.execute('''
            INSERT INTO goals (user_id, name, target_amount, target_date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            name,
            target_amount,
            target_date,
            description
        ))
        conn.commit()
        conn.close()
        
        flash('Goal berhasil ditambahkan!', 'success')
        return redirect(url_for('goals'))
        
    except ValueError as e:
        flash('Data tidak valid! Pastikan format angka dan tanggal benar.', 'error')
        return redirect(url_for('goals'))
    except Exception as e:
        flash('Terjadi kesalahan saat menambahkan goal.', 'error')
        return redirect(url_for('goals'))

@app.route('/reports')
@login_required
def reports():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get expense data by category for pie chart
    expense_data = conn.execute('''
        SELECT c.name, SUM(t.amount) as total, c.color
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.type = 'expense'
        GROUP BY c.id
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template('reports.html', expense_data=expense_data)

@app.route('/api/chart_data')
@login_required
def chart_data():
    user_id = session['user_id']
    chart_type = request.args.get('type', 'expense_pie')
    conn = get_db_connection()
    
    if chart_type == 'expense_pie':
        data = conn.execute('''
            SELECT c.name, SUM(t.amount) as total, c.color
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND c.type = 'expense'
            GROUP BY c.id
        ''', (user_id,)).fetchall()
        
        chart_data = {
            'labels': [row['name'] for row in data],
            'values': [float(row['total']) for row in data],
            'colors': [row['color'] for row in data]
        }
        
    elif chart_type == 'monthly_trend':
        data = conn.execute('''
            SELECT 
                strftime('%Y-%m', t.date) as month,
                c.type,
                SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            GROUP BY strftime('%Y-%m', t.date), c.type
            ORDER BY month
        ''', (user_id,)).fetchall()
        
        # Process data for chart
        months = set()
        monthly_totals = {}
        
        for row in data:
            month = row['month']
            months.add(month)
            if month not in monthly_totals:
                monthly_totals[month] = {'income': 0, 'expense': 0}
            monthly_totals[month][row['type']] = float(row['total'])
        
        sorted_months = sorted(months)
        income_data = [monthly_totals.get(month, {}).get('income', 0) for month in sorted_months]
        expense_data = [monthly_totals.get(month, {}).get('expense', 0) for month in sorted_months]
        
        chart_data = {
            'labels': sorted_months,
            'income': income_data,
            'expense': expense_data
        }
    
    conn.close()
    return jsonify(chart_data)

# Edit and Delete routes for Transactions
@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Update transaction
        conn.execute('''
            UPDATE transactions 
            SET category_id = ?, amount = ?, description = ?, date = ?
            WHERE id = ? AND user_id = ?
        ''', (
            request.form['category_id'],
            float(request.form['amount']),
            request.form['description'],
            request.form['date'],
            transaction_id,
            user_id
        ))
        conn.commit()
        conn.close()
        
        flash('Transaksi berhasil diupdate!', 'success')
        return redirect(url_for('transactions'))
    
    # Get transaction data
    transaction = conn.execute('''
        SELECT t.*, c.name as category_name, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.id = ? AND t.user_id = ?
    ''', (transaction_id, user_id)).fetchone()
    
    if not transaction:
        flash('Transaksi tidak ditemukan!', 'error')
        conn.close()
        return redirect(url_for('transactions'))
    
    # Get categories
    categories = conn.execute('SELECT * FROM categories ORDER BY type, name').fetchall()
    conn.close()
    
    return jsonify({
        'id': transaction['id'],
        'category_id': transaction['category_id'],
        'amount': transaction['amount'],
        'description': transaction['description'],
        'date': transaction['date']
    })

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Check if transaction belongs to user
    transaction = conn.execute('''
        SELECT id FROM transactions WHERE id = ? AND user_id = ?
    ''', (transaction_id, user_id)).fetchone()
    
    if not transaction:
        flash('Transaksi tidak ditemukan!', 'error')
        conn.close()
        return redirect(url_for('transactions'))
    
    # Delete transaction
    conn.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, user_id))
    conn.commit()
    conn.close()
    
    flash('Transaksi berhasil dihapus!', 'success')
    return redirect(url_for('transactions'))

# Edit and Delete routes for Budgets
@app.route('/edit_budget/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        try:
            # Validate input
            category_id = request.form.get('category_id')
            amount = request.form.get('amount')
            period = request.form.get('period')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            if not all([category_id, amount, period, start_date, end_date]):
                flash('Semua field wajib harus diisi!', 'error')
                conn.close()
                return redirect(url_for('budgets'))
            
            amount = float(amount)
            if amount <= 0:
                flash('Jumlah budget harus lebih besar dari 0!', 'error')
                conn.close()
                return redirect(url_for('budgets'))
            
            # Validate dates
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start_date_obj >= end_date_obj:
                flash('Tanggal selesai harus setelah tanggal mulai!', 'error')
                conn.close()
                return redirect(url_for('budgets'))
            
            # Validate period
            if period not in ['weekly', 'monthly', 'yearly']:
                flash('Periode tidak valid!', 'error')
                conn.close()
                return redirect(url_for('budgets'))
            
            # Check if category exists and is expense type
            category = conn.execute('''
                SELECT id, type FROM categories WHERE id = ? AND type = 'expense'
            ''', (category_id,)).fetchone()
            
            if not category:
                flash('Kategori tidak valid!', 'error')
                conn.close()
                return redirect(url_for('budgets'))
            
            # Update budget
            conn.execute('''
                UPDATE budgets 
                SET category_id = ?, amount = ?, period = ?, start_date = ?, end_date = ?
                WHERE id = ? AND user_id = ?
            ''', (
                int(category_id),
                amount,
                period,
                start_date,
                end_date,
                budget_id,
                user_id
            ))
            conn.commit()
            conn.close()
            
            flash('Budget berhasil diupdate!', 'success')
            return redirect(url_for('budgets'))
            
        except ValueError as e:
            flash('Data tidak valid! Pastikan format angka dan tanggal benar.', 'error')
            conn.close()
            return redirect(url_for('budgets'))
        except Exception as e:
            flash('Terjadi kesalahan saat mengupdate budget.', 'error')
            conn.close()
            return redirect(url_for('budgets'))
    
    # Get budget data
    budget = conn.execute('''
        SELECT b.*, c.name as category_name
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ? AND b.user_id = ?
    ''', (budget_id, user_id)).fetchone()
    
    if not budget:
        flash('Budget tidak ditemukan!', 'error')
        conn.close()
        return redirect(url_for('budgets'))
    
    conn.close()
    
    return jsonify({
        'id': budget['id'],
        'category_id': budget['category_id'],
        'amount': budget['amount'],
        'period': budget['period'],
        'start_date': budget['start_date'],
        'end_date': budget['end_date']
    })

@app.route('/delete_budget/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Check if budget belongs to user
    budget = conn.execute('''
        SELECT id FROM budgets WHERE id = ? AND user_id = ?
    ''', (budget_id, user_id)).fetchone()
    
    if not budget:
        flash('Budget tidak ditemukan!', 'error')
        conn.close()
        return redirect(url_for('budgets'))
    
    # Delete budget
    conn.execute('DELETE FROM budgets WHERE id = ? AND user_id = ?', (budget_id, user_id))
    conn.commit()
    conn.close()
    
    flash('Budget berhasil dihapus!', 'success')
    return redirect(url_for('budgets'))

# Edit and Delete routes for Goals
@app.route('/edit_goal/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Update goal
        conn.execute('''
            UPDATE goals 
            SET name = ?, target_amount = ?, target_date = ?, description = ?
            WHERE id = ? AND user_id = ?
        ''', (
            request.form['name'],
            float(request.form['target_amount']),
            request.form['target_date'],
            request.form['description'],
            goal_id,
            user_id
        ))
        conn.commit()
        conn.close()
        
        flash('Target berhasil diupdate!', 'success')
        return redirect(url_for('goals'))
    
    # Get goal data
    goal = conn.execute('''
        SELECT * FROM goals WHERE id = ? AND user_id = ?
    ''', (goal_id, user_id)).fetchone()
    
    if not goal:
        flash('Target tidak ditemukan!', 'error')
        conn.close()
        return redirect(url_for('goals'))
    
    conn.close()
    
    return jsonify({
        'id': goal['id'],
        'name': goal['name'],
        'target_amount': goal['target_amount'],
        'target_date': goal['target_date'],
        'description': goal['description']
    })

@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Check if goal belongs to user
    goal = conn.execute('''
        SELECT id FROM goals WHERE id = ? AND user_id = ?
    ''', (goal_id, user_id)).fetchone()
    
    if not goal:
        flash('Target tidak ditemukan!', 'error')
        conn.close()
        return redirect(url_for('goals'))
    
    # Delete goal
    conn.execute('DELETE FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
    conn.commit()
    conn.close()
    
    flash('Target berhasil dihapus!', 'success')
    return redirect(url_for('goals'))

# Route to update goal progress
@app.route('/update_goal_progress/<int:goal_id>', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    user_id = session['user_id']
    amount = float(request.form['amount'])
    
    conn = get_db_connection()
    
    # Check if goal belongs to user
    goal = conn.execute('''
        SELECT current_amount FROM goals WHERE id = ? AND user_id = ?
    ''', (goal_id, user_id)).fetchone()
    
    if not goal:
        flash('Target tidak ditemukan!', 'error')
        conn.close()
        return redirect(url_for('goals'))
    
    # Update goal progress
    new_amount = goal['current_amount'] + amount
    conn.execute('''
        UPDATE goals SET current_amount = ? WHERE id = ? AND user_id = ?
    ''', (new_amount, goal_id, user_id))
    conn.commit()
    conn.close()
    
    flash('Progress target berhasil diupdate!', 'success')
    return redirect(url_for('goals'))

# Export routes
@app.route('/export_transactions')
@login_required
def export_transactions():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get all transactions for the user
    transactions = conn.execute('''
        SELECT t.date, c.name as category, c.type, t.amount, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    # Create CSV content
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Tanggal', 'Kategori', 'Tipe', 'Jumlah', 'Deskripsi'])
    
    # Write data
    for transaction in transactions:
        writer.writerow([
            transaction['date'],
            transaction['category'],
            transaction['type'],
            transaction['amount'],
            transaction['description'] or ''
        ])
    
    output.seek(0)
      # Return as downloadable file
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=transaksi.csv'
        }
    )

@app.route('/export_budgets')
@login_required
def export_budgets():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get all budgets for the user
    budgets = conn.execute('''
        SELECT b.*, c.name as category
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    # Create CSV content
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Kategori', 'Jumlah Budget', 'Periode', 'Tanggal Mulai', 'Tanggal Selesai'])
    
    # Write data
    for budget in budgets:
        writer.writerow([
            budget['category'],
            budget['amount'],
            budget['period'],
            budget['start_date'],
            budget['end_date']
        ])
    
    output.seek(0)
      # Return as downloadable file
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=budget.csv'
        }
    )

@app.route('/api/budget_alerts')
@login_required
def budget_alerts():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get budgets with their spending
    budgets = conn.execute('''
        SELECT b.*, c.name as category_name, c.icon as category_icon
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ?
    ''', (user_id,)).fetchall()
    
    alerts = []
    current_date = date.today()
    
    for budget in budgets:
        # Only check active budgets
        if budget['start_date'] <= str(current_date) <= budget['end_date']:
            spent = conn.execute('''
                SELECT COALESCE(SUM(amount), 0) as total
                FROM transactions
                WHERE user_id = ? AND category_id = ?
                AND date >= ? AND date <= ?
            ''', (user_id, budget['category_id'], budget['start_date'], budget['end_date'])).fetchone()['total']
            
            percentage = (spent / budget['amount'] * 100) if budget['amount'] > 0 else 0
            
            # Alert if budget is 70% or more used
            if percentage >= 70:
                alerts.append({
                    'category_name': budget['category_name'],
                    'budget': budget['amount'],
                    'spent': spent,
                    'percentage': percentage
                })
    
    conn.close()
    return jsonify({'alerts': alerts})

@app.route('/api/search_transactions')
@login_required
def search_transactions():
    user_id = session['user_id']
    
    # Get search parameters
    search_term = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    min_amount = request.args.get('min_amount', '')
    max_amount = request.args.get('max_amount', '')
    transaction_type = request.args.get('type', '')  # 'income' or 'expense'
    
    conn = get_db_connection()
    
    # Build query
    query = '''
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    '''
    params = [user_id]
    
    # Add search term filter
    if search_term:
        query += ' AND (t.description LIKE ? OR c.name LIKE ?)'
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    # Add category filter
    if category_id:
        query += ' AND t.category_id = ?'
        params.append(category_id)
    
    # Add date range filter
    if date_from:
        query += ' AND t.date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND t.date <= ?'
        params.append(date_to)
    
    # Add amount range filter
    if min_amount:
        query += ' AND t.amount >= ?'
        params.append(float(min_amount))
    
    if max_amount:
        query += ' AND t.amount <= ?'
        params.append(float(max_amount))
    
    # Add transaction type filter
    if transaction_type:
        query += ' AND c.type = ?'
        params.append(transaction_type)
    
    query += ' ORDER BY t.date DESC, t.created_at DESC'
    
    transactions = conn.execute(query, params).fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    result = []
    for transaction in transactions:
        result.append({
            'id': transaction['id'],
            'amount': transaction['amount'],
            'description': transaction['description'],
            'date': transaction['date'],
            'category_name': transaction['category_name'],
            'category_icon': transaction['category_icon'],
            'category_type': transaction['category_type']
        })
    
    return jsonify({'transactions': result})

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    
    user = conn.execute('''
        SELECT id, username, email, created_at FROM users WHERE id = ?
    ''', (user_id,)).fetchone()
    
    # Get user statistics
    total_transactions = conn.execute('''
        SELECT COUNT(*) as count FROM transactions WHERE user_id = ?
    ''', (user_id,)).fetchone()['count']
    
    total_budgets = conn.execute('''
        SELECT COUNT(*) as count FROM budgets WHERE user_id = ?
    ''', (user_id,)).fetchone()['count']
    
    total_goals = conn.execute('''
        SELECT COUNT(*) as count FROM goals WHERE user_id = ?
    ''', (user_id,)).fetchone()['count']
    
    # Get financial summary
    total_income = conn.execute('''
        SELECT COALESCE(SUM(t.amount), 0) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.type = 'income'
    ''', (user_id,)).fetchone()['total']
    
    total_expense = conn.execute('''
        SELECT COALESCE(SUM(t.amount), 0) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.type = 'expense'
    ''', (user_id,)).fetchone()['total']
    
    conn.close()
    
    stats = {
        'total_transactions': total_transactions,
        'total_budgets': total_budgets,
        'total_goals': total_goals,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': total_income - total_expense
    }
    
    return render_template('profile.html', user=user, stats=stats)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user_id = session['user_id']
    
    try:
        # Validate input
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email:
            flash('Username dan email harus diisi!', 'error')
            return redirect(url_for('profile'))
        
        if len(username) < 3:
            flash('Username minimal 3 karakter!', 'error')
            return redirect(url_for('profile'))
        
        # Validate email format (basic validation)
        if '@' not in email or '.' not in email:
            flash('Format email tidak valid!', 'error')
            return redirect(url_for('profile'))
        
        conn = get_db_connection()
        
        # Check if username or email already exists (excluding current user)
        existing_user = conn.execute('''
            SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?
        ''', (username, email, user_id)).fetchone()
        
        if existing_user:
            flash('Username atau email sudah digunakan!', 'error')
            conn.close()
            return redirect(url_for('profile'))
        
        # If password change is requested
        if new_password:
            if not current_password:
                flash('Password saat ini harus diisi untuk mengubah password!', 'error')
                conn.close()
                return redirect(url_for('profile'))
            
            # Verify current password
            user = conn.execute('''
                SELECT password_hash FROM users WHERE id = ?
            ''', (user_id,)).fetchone()
            
            if not check_password_hash(user['password_hash'], current_password):
                flash('Password saat ini salah!', 'error')
                conn.close()
                return redirect(url_for('profile'))
            
            if len(new_password) < 6:
                flash('Password baru minimal 6 karakter!', 'error')
                conn.close()
                return redirect(url_for('profile'))
            
            if new_password != confirm_password:
                flash('Konfirmasi password tidak sesuai!', 'error')
                conn.close()
                return redirect(url_for('profile'))
            
            # Update with new password
            password_hash = generate_password_hash(new_password)
            conn.execute('''
                UPDATE users SET username = ?, email = ?, password_hash = ?
                WHERE id = ?
            ''', (username, email, password_hash, user_id))
            
            flash('Profil dan password berhasil diupdate!', 'success')
        else:
            # Update without password change
            conn.execute('''
                UPDATE users SET username = ?, email = ?
                WHERE id = ?
            ''', (username, email, user_id))
            
            flash('Profil berhasil diupdate!', 'success')
        
        conn.commit()
        conn.close()
        
        # Update session with new username
        session['username'] = username
        
        return redirect(url_for('profile'))
        
    except Exception as e:
        flash('Terjadi kesalahan saat mengupdate profil.', 'error')
        return redirect(url_for('profile'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
