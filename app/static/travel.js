let map, directionsService, directionsRenderer
let sourceAutoComplete, destinationAutoComplete
function initMap(){
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 39.50, lng: -98.35},
        zoom: 4,
        styles: [
          {elementType: 'geometry', stylers: [{color: '#242f3e'}]},
          {elementType: 'labels.text.stroke', stylers: [{color: '#242f3e'}]},
          {elementType: 'labels.text.fill', stylers: [{color: '#746855'}]},
          {
            featureType: 'administrative.locality',
            elementType: 'labels.text.fill',
            stylers: [{color: '#d59563'}]
          },
          {
            featureType: 'poi',
            elementType: 'labels.text.fill',
            stylers: [{color: '#d59563'}]
          },
          {
            featureType: 'poi.park',
            elementType: 'geometry',
            stylers: [{color: '#263c3f'}]
          },
          {
            featureType: 'poi.park',
            elementType: 'labels.text.fill',
            stylers: [{color: '#6b9a76'}]
          },
          {
            featureType: 'road',
            elementType: 'geometry',
            stylers: [{color: '#38414e'}]
          },
          {
            featureType: 'road',
            elementType: 'geometry.stroke',
            stylers: [{color: '#212a37'}]
          },
          {
            featureType: 'road',
            elementType: 'labels.text.fill',
            stylers: [{color: '#9ca5b3'}]
          },
          {
            featureType: 'road.highway',
            elementType: 'geometry',
            stylers: [{color: '#746855'}]
          },
          {
            featureType: 'road.highway',
            elementType: 'geometry.stroke',
            stylers: [{color: '#1f2835'}]
          },
          {
            featureType: 'road.highway',
            elementType: 'labels.text.fill',
            stylers: [{color: '#f3d19c'}]
          },
          {
            featureType: 'transit',
            elementType: 'geometry',
            stylers: [{color: '#2f3948'}]
          },
          {
            featureType: 'transit.station',
            elementType: 'labels.text.fill',
            stylers: [{color: '#d59563'}]
          },
          {
            featureType: 'water',
            elementType: 'geometry',
            stylers: [{color: '#17263c'}]
          },
          {
            featureType: 'water',
            elementType: 'labels.text.fill',
            stylers: [{color: '#515c6d'}]
          },
          {
            featureType: 'water',
            elementType: 'labels.text.stroke',
            stylers: [{color: '#17263c'}]
          }
        ]
    });
    google.maps.event.addListener(map, 'click', function(event) {
        this.setOptions({scrollwheel:true});
    });
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);
    sourceAutoComplete = new google.maps.places.Autocomplete(document.getElementById('starting_point'));
    destinationAutoComplete = new google.maps.places.Autocomplete(document.getElementById('destination'));
}

function calcRoute(event, cameras){
    event.preventDefault();
    var starting_point = document.getElementById('starting_point').value;
    var destination = document.getElementById('destination').value;
    var request = {
        origin: starting_point,
        destination: destination,
        travelMode: 'DRIVING'
    };
    directionsService.route(request, function(result, status){
        if(status == 'OK'){
            directionsRenderer.setDirections(result);
            showCamerasNearRoute(result, cameras, distranceThresholdKm=10)
        }
    });
}

function showCamerasNearRoute(result, cameras, distanceThresholdKm) {
  const route = result.routes[0];
  const routePath = route.overview_path;

  cameras.forEach(function (camera) {
    const cameraLatLng = new google.maps.LatLng(camera.latitude, camera.longitude);

    const isNearRoute = routePath.some(function (pathLatLng, i) {
      if (i === routePath.length - 1) {
        return false;
      }

      const startLatLng = pathLatLng;
      const endLatLng = routePath[i + 1];
      const distance = google.maps.geometry.spherical.computeDistanceBetween(
        cameraLatLng,
        startLatLng
      ) + google.maps.geometry.spherical.computeDistanceBetween(
        cameraLatLng,
        endLatLng
      ) / 2;

      return distance <= distanceThresholdKm * 1000;
    });

    if (isNearRoute) {

      const marker = new google.maps.Marker({
        position: cameraLatLng,
        map: map,
        title: camera.name
      });
      
      const content = `<a href="/cameras/${camera.id}" target="_blank">Camera ${camera.title}</a>`;

      const infoWindow = new google.maps.InfoWindow({
        content: content
      });

      marker.addListener('click', function () {
        infoWindow.open(map, marker);
      });
    }
  });
}