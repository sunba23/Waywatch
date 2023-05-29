from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '2f03ef2cc69979cbad9d947ceaee4e84'

cameras = [
    {
        'id': 1,
        'title': 'here goes street name 1',
        'update_date': 'here goes the last update timestamp',
        'description': 'here goes description',
        'image': 'here goes camera image from cv2'
    },
    {
        'id': 2,
        'title': 'here goes street name 2',
        'update_date': 'here goes the last update timestamp',
        'description': 'here goes description',
        'image': 'here goes camera image from cv2'
    }
]

traffic_map = {

}

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', traffic_map=traffic_map, cameras=cameras)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data} successfully', category="success")
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'You are now logged in', category="success")
        return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    app.run(debug=True)