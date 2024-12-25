from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from flask import Flask, render_template, request, jsonify
from chat import get_chat_response
from sklearn.model_selection import train_test_split

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

# Load the dataset
data = pd.read_csv("testpcosval.csv")
X = data.drop(columns=['PCOS (Y/N)'])
y = data['PCOS (Y/N)']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = GradientBoostingClassifier(random_state=42)
model.fit(X_train, y_train)

# Train the model
model = GradientBoostingClassifier()
model.fit(X, y)

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['name'] = user.name
            session['email'] = user.email
            session['password'] = user.password
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid user')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'name' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# Main application routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Collect and validate input features
        try:
            input_features = [
                int(request.form['Age (yrs)']),
                float(request.form['Weight (Kg)']),
                float(request.form['Height(Cm)']),
                float(request.form['BMI']),
                int(request.form['Blood Group']),
                int(request.form['Pulse rate(bpm)']),
                int(request.form['RR (breaths/min)']),
                float(request.form['Hb(g/dl)']),
                int(request.form['Cycle(R/I)']),
                int(request.form['Cycle length(days)']),
                int(request.form['Pregnant(Y/N)']),
                int(request.form['No. of abortions']),
                int(request.form['Hip(inch)']),
                int(request.form['Waist(inch)']),
                float(request.form['RBS(mg/dl)']),
                int(request.form['Weight gain(Y/N)']),
                int(request.form['hair growth(Y/N)']),
                int(request.form['Skin darkening (Y/N)']),
                int(request.form['Hair loss(Y/N)']),
                int(request.form['Pimples(Y/N)']),
                int(request.form['Reg.Exercise(Y/N)']),
                int(request.form['BP _Systolic (mmHg)']),
                int(request.form['BP _Diastolic (mmHg)']),
                int(request.form['Follicle No. (L)']),
                int(request.form['Follicle No. (R)']),
                float(request.form['Avg. F size (L) (mm)']),
                float(request.form['Avg. F size (R) (mm)']),
                float(request.form['Endometrium (mm)'])
            ]
        except ValueError:
            return render_template('error.html', error="Invalid input data")

        # Predict PCOS
        prediction = model.predict([input_features])

        # Render the result
        prediction_text = "Yes" if prediction[0] == 1 else "No"
        return render_template('result.html', prediction=prediction_text)

@app.route('/index')
def index():
    if 'name' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('index.html', user=user)
    return redirect(url_for('login'))

@app.route('/prevention')
def prevention():
    return render_template('prevention.html')

@app.route('/diet')
def diet():
    return render_template('diet.html')

@app.route('/exercise')
def exercise():
    return render_template('exercise.html')

@app.route('/base')
def base():
    return render_template('base.html')




@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    if user_message:
        response = get_chat_response(user_message)
        return jsonify({'response': response})
    return jsonify({'response': 'No message provided'})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
