from flask import (Blueprint, render_template, url_for,
                   flash, redirect, request, current_app)
from flask_login import current_user, login_required
import folium
from app.cameras.forms import TravelForm
from app.models import Camera

cameras_bp = Blueprint('cameras', __name__)


@cameras_bp.route('/cameras/<int:camera_id>')
@login_required
def camera(camera_id):
    camera = Camera.query.get_or_404(camera_id)
    return render_template(
        'camera.html', 
        title=camera.title, 
        camera=camera)


@cameras_bp.route('/cameras')
@login_required
def cameras():
    user = current_user
    fav_cameras = user.favorite_cameras
    return render_template('cameras.html',
                           title='Cameras',
                           cameras=fav_cameras)


@cameras_bp.route('/map')
def map():
    if current_user.is_authenticated:
        cameras = current_user.favorite_cameras
        m = folium.Map(location=[39.50, -98.35], zoom_start=4)
        folium.TileLayer('cartodbdark_matter').add_to(m)

        for camera in cameras:
            link_url = url_for('cameras.camera', camera_id=camera.id)
            link_content = (
                            f'<a href="{link_url}" target="_blank">'
                            f'Camera {camera.title}'
                            f'</a>'
                        )
            popup = folium.Popup(link_content, max_width=300)
            folium.Marker([camera.latitude, camera.longitude],
                          popup=popup).add_to(m)

        m = m._repr_html_()
        return render_template('map.html', map=m, title='Map')
    else:
        next_page = request.args.get('next')
        flash('You must be logged in to view this page', category="info")
        return redirect(url_for('users.login', next=next_page))


@cameras_bp.route('/travel', methods=['GET', 'POST'])
@login_required
def travel():
    if current_user.is_premium:
        form = TravelForm()
        maps_api_key = current_app.config['GOOGLE_MAPS_API']
        if form.validate_on_submit():
            return render_template('travel.html',
                                title='Travel',
                                form=form,
                                maps_api_key=maps_api_key,
                                cameras=[camera.to_dict()
                                         for camera in Camera.query.all()])
        else:
            return render_template('travel.html',
                                 title='Travel',
                                 form=form,
                                 maps_api_key=maps_api_key,
                                 cameras=[camera.to_dict()
                                          for camera in Camera.query.all()])
    else:
        flash('You need to be a premium user to access this page.',
              category="warning")
        return redirect(url_for('main.home'))
