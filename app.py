from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

# Dummy user
users = {"admin": "admin123"}



# Dummy bookings
bookings = []

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET','POST'])
def login():
    if 'user' in session:
        return redirect(url_for('search'))
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname in users and users[uname] == pwd:
            session['user'] = uname
            return redirect(url_for('search'))  # Login ke baad search page
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- SEARCH ----------
@app.route('/search', methods=['GET','POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))

    trains = []
    if request.method == 'POST':
        from_station = request.form['from']
        to_station = request.form['to']
        date = request.form['date']

        
        return render_template('predict.html')
    return render_template('search.html', user=session['user'], trains=trains)

# ---------- PREDICT ----------
@app.route('/predict/<train_no>')
def predict(train_no):
    if 'user' not in session:
        return redirect(url_for('login'))

    train = next((t for t in trains_db if t['train_no']==train_no), None)
    if not train:
        return redirect(url_for('search'))

    
    return render_template('predict.html', user=session['user'], train=train, prediction=prediction)

# ---------- MY BOOKINGS ----------
@app.route('/mybookings')
def mybookings():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_bookings = [b for b in bookings if b['user']==session['user']]
    return render_template('mybookings.html', user=session['user'], bookings=user_bookings)

# ---------- FARE TREND ----------
@app.route('/faretrend')
def faretrend():
    if 'user' not in session:
        return redirect(url_for('login'))

    trends = [
        {"train_no": "12345", "fare": "₹1200"},
        {"train_no": "67890", "fare": "₹1300"}
    ]
    return render_template('faretrend.html', user=session['user'], trends=trends)

# ---------- SUMMARY ----------
@app.route('/summary')
def summary():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('summary.html', user=session['user'], bookings=bookings)

if __name__ == "__main__":
    app.run(debug=True)
