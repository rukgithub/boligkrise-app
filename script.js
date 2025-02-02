function initMap() {
  var mapOptions = {
    center: { lat: 55.6761, lng: 12.5683 },
    zoom: 12 // 20% tættere på end, hvis standard var 10
  };
  var map = new google.maps.Map(document.getElementById('map'), mapOptions);
}

window.addEventListener('load', initMap); 