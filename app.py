from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from models import db, User, Scan  # db'yi models modülünden içe aktarın

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Veritabanı ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://docker_user:docker_user@localhost:5433/DbScanner'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # db'yi uygulama ile başlatın
migrate = Migrate(app, db)

# Flask-Mail ayarları
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
mail = Mail(app)

# Ana sayfa (karşılama ekranı)
@app.route('/')
def index():
    return render_template('index.html')

# Kayıt sayfası (GET)
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# Kayıt işlemi (POST)
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Kullanıcı adı ve e-posta kontrolü
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        flash('Bu kullanıcı adı veya e-posta zaten mevcut.')
        return redirect(url_for('register_page'))

    # Şifre güvenliği kontrolü
    if not is_strong_password(password):
        flash('Şifre en az 8 karakter, bir büyük harf ve bir rakam içermelidir.')
        return redirect(url_for('register_page'))

    # Yeni kullanıcı oluştur
    new_user = User(username=username, email=email, password=generate_password_hash(password))
    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Kayıt başarılı! Giriş yapabilirsiniz.')
        return redirect(url_for('login_page'))
    except Exception as e:
        db.session.rollback()
        flash('Kayıt sırasında bir hata oluştu: {}'.format(str(e)))
        return redirect(url_for('register_page'))

def is_strong_password(password):
    return (len(password) >= 8 and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password))

# Giriş sayfası (GET)
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        flash('Giriş başarılı!')
        return redirect(url_for('dashboard', username=user.username))  # Kullanıcı ismini gönder
    else:
        flash('Kullanıcı adı veya şifre yanlış.')
        return redirect(url_for('login_page'))  # Hatalı girişte login sayfasına geri dön

# Kullanıcı paneli (giriş yapan kullanıcı için)
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)
    return redirect(url_for('index'))

# Çıkış yapma
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Çıkış yapıldı.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluştur
    app.run(debug=True)
