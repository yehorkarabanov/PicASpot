import { StyleSheet } from 'react-native'

export const styles = StyleSheet.create({
  map: {
    flex: 1,
  },
})

export const DARK_MAP = [
  {
    elementType: "geometry",
    stylers: [
      { color: "#242f3e" },
    ],
  },
  {
    elementType: "geometry.fill",
    stylers: [
      { saturation: -5 },
      { lightness: -5 },
    ],
  },
  {
    elementType: "labels.text.fill",
    stylers: [
      { color: "#a5a5a5" },
    ],
  },
  {
    elementType: "labels.text.stroke",
    stylers: [
      { color: "#242f3e" },
    ],
  },
  {
    elementType: "labels.icon",
    stylers: [
      { visibility: "off" },
    ],
  },
  {
    featureType: "administrative",
    elementType: "geometry",
    stylers: [
      { color: "#757575" },
    ],
  },
  {
    featureType: "administrative.land_parcel",
    stylers: [
      { visibility: "on" },
    ],
  },
  {
    "featureType": "transit.station",
    "elementType": "labels",
    "stylers": [
      { "visibility": "off" }
    ]
  },
  {
    featureType: "poi",
    elementType: "geometry",
    stylers: [
      { visibility: "on" },
    ],
  },
  {
    "featureType": "poi",
    "elementType": "labels",
    "stylers": [
      { "visibility": "off" }
    ]
  },
  {
    featureType: "poi.business",
    stylers: [
      { visibility: "off" },
    ],
  },
  {
    featureType: "poi.park",
    elementType: "geometry",
    stylers: [
      { color: "#37423d" },
    ],
  },
  {
    featureType: "landscape.man_made.building",
    elementType: "geometry",
    stylers: [
      { color: "#2e3948" },
    ],
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [
      { color: "#38414e" },
    ],
  },
  {
    featureType: "road",
    elementType: "geometry.fill",
    stylers: [
      { color: "#38414e" },
    ],
  },
  {
    featureType: "road.arterial",
    elementType: "geometry",
    stylers: [
      { color: "#373737" },
    ],
  },
  {
    featureType: "road.highway",
    elementType: "geometry",
    stylers: [
      { color: "#373737" },
    ],
  },
  {
    featureType: "road.highway.controlled_access",
    elementType: "geometry",
    stylers: [
      { color: "#4e4e4e" },
    ],
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [
      { color: "#17263c" },
    ],
  },
  {
    featureType: "water",
    elementType: "labels.text.fill",
    stylers: [
      { color: "#515c6d" },
    ],
  },
  {
    featureType: "administrative.country",
    elementType: "labels",
    stylers: [
      { visibility: "on" }
    ],
  },
  {
    featureType: "administrative.country",
    elementType: "labels.text.fill",
    stylers: [
      { color: "#9E9E9E" },
    ],
  },
  {
    featureType: "administrative.locality",
    elementType: "labels",
    stylers: [
      { visibility: "on" }
    ],
  },
  {
    featureType: "administrative.locality",
    elementType: "labels.text.fill",
    stylers: [
      { color: "#BDBDBD" },
    ],
  },
{
    "featureType": "road.highway",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "road.arterial",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "road.local",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  }
];

export const LIGHT_MAP = [
  {
    "featureType": "transit.station",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "geometry",
    "stylers": [
      {
        "visibility": "on"
      }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "road.highway",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "road.arterial",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "road.local",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  }
];
