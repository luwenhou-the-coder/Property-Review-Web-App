var map;
var infowindow;
var markers=[];
var pyrmont;
function initMap() {
   pyrmont = {lat: parseFloat(latitude), lng: parseFloat(longitude)};

  map = new google.maps.Map(document.getElementById('map'), {
    center: pyrmont,
    zoom: 15
  });

  infowindow = new google.maps.InfoWindow();

  var selfMarker = new google.maps.Marker({
    map: map,
    position: pyrmont,
    icon:"http://maps.google.com/mapfiles/ms/icons/green-dot.png"
  });
  selfMarker.setMap(map);
}

function callback(results, status) {
  setMapOnAll(null);
  markers=[];
  if (status === google.maps.places.PlacesServiceStatus.OK) {
    for (var i = 0; i < results.length; i++) {
      createMarker(results[i]);
    }
  }
  setMapOnAll(map);
}

function createMarker(place) {
  var placeLoc = place.geometry.location;
  var marker = new google.maps.Marker({
    map: map,
    position: place.geometry.location
  });

  google.maps.event.addListener(marker, 'click', function() {
    infowindow.setContent(place.name);
    infowindow.open(map, this);
  });
  markers.push(marker);
}

function setMapOnAll(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

function getNearbyStores(){
  var service = new google.maps.places.PlacesService(map);
  service.nearbySearch({
    location: pyrmont,        
    radius: 1000,
    types: ['store']
  }, callback);
}
function getNearbyRestaurants(){
  var service = new google.maps.places.PlacesService(map);
  service.nearbySearch({
    location: pyrmont,        
    radius: 1000,
    types: ['restaurant']
  }, callback);
}
function getNearbyUniversities(){
  var service = new google.maps.places.PlacesService(map);
  service.nearbySearch({
    location: pyrmont,        
    radius: 1000,
    types: ['university']
  }, callback);
}
