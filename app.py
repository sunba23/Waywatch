from flask import Flask, render_template, url_for

app = Flask(__name__)

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
def index():
    return render_template('home.html', traffic_map=traffic_map, cameras=cameras)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)