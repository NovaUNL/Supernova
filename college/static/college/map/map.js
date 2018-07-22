let initCampusMap = 1;
if (typeof L === 'object') {
// TODO load these dynamically
    let icons = {
        "fablab": L.icon({
            iconUrl: '/static/college/map/fablab.png',
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        }),
        "ctt": L.icon({
            iconUrl: '/static/college/map/ctt.svg',
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        }),
        "mb": L.icon({
            iconUrl: '/static/college/map/mb.svg',
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        }),
        "mts": L.icon({
            iconUrl: '/static/college/map/mts.svg',
            iconSize: [64, 64],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        }),
        "tst": L.icon({
            iconUrl: '/static/college/map/tst.svg',
            iconSize: [64, 64],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        }),
        "aefct": L.icon({
            iconUrl: '/static/college/map/aefct.png',
            iconSize: [100, 40],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        }),
        "ninf": L.icon({
            iconUrl: '/static/college/map/ninf.png',
            iconSize: [64, 20],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        }),
        "neec": L.icon({
            iconUrl: '/static/college/map/neec.png',
            iconSize: [64, 20],
            iconAnchor: [32, 16],
            popupAnchor: [0, -20]
        }),
        "nave": L.icon({
            iconUrl: '/static/college/map/nave.png',
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -20]
        })
    };


    /**
     * Binds popups to geoJSON features
     * @param feature geoJSON feature
     * @param layer leaflet feature layer
     */
    function bindFeaturePopup(feature, layer) {
        if (feature.properties && feature.properties.popupContent) {
            popupContent = "<b>" + feature.properties.popupContent + "</b>";
            layer.bindPopup(popupContent);
        }
    }


    /**
     * creates a layer group from geoJSON features
     * @param geoJSON array of geoJSON features
     */
    function layerFromGeoJSON(geoJSON) {
        let layer = L.featureGroup();
        L.geoJSON(geoJSON, {
            pointToLayer: function (feature, latlng) {
                let iconName = feature.properties.icon;
                if (iconName in icons) {
                    return L.marker(latlng, {icon: icons[iconName]});
                } else {
                    return L.marker(latlng);
                }
            },
            onEachFeature: bindFeaturePopup
        }).addTo(layer);
        return layer;
    }

    initCampusMap = function (element) {
        let campusMap = L.map('campus-map').setView([38.6608, -9.205576], 18);

        let tileSource = L.tileLayer(
            'https://cartodb-basemaps-{s}.global.ssl.fastly.net/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> / <a href="http://cartodb.com/attributions">CartoDB</a>',
                minZoom: 16,
                maxZoom: 19
            });
        tileSource.addTo(campusMap);
        // Draws campus buildings
        L.geoJSON(campus, {
            style: function (feature) {
                return feature.properties && feature.properties.style;
            },
            onEachFeature: bindFeaturePopup
        }).addTo(campusMap);
        let servicesLayer = layerFromGeoJSON(services);
        servicesLayer.addTo(campusMap);

        let overlays = {
            "Serviços": servicesLayer,
            "Associações de estudantes": layerFromGeoJSON(studentAssociations),
        };
        L.control.layers(null, overlays).addTo(campusMap);
    };
}


let initTransportationMap = function (element) {
    let map = svgPanZoom(element, {
        zoomEnabled: true,
        controlIconsEnabled: true,
        minZoom: 2,
        maxZoom: 5,
        zoomScaleSensitivity: 1.5,
        center: 1
    });
    map.contain();
};