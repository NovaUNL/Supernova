let map;

let initCampusMap = function (element) {
    map = new CampusMap(element);
};

let initTransportationMap = function (element) {
    map = new TransportationMap(element);
};


panLimiter = function () { // TODO Don't allow the map to go outside its container
    let gutterWidth = 200,
        gutterHeight = 200,
        sizes = this.getSizes(),
        leftLimit = -((sizes.viewBox.x + sizes.viewBox.width) * sizes.realZoom) + gutterWidth,
        rightLimit = sizes.width - gutterWidth - (sizes.viewBox.x * sizes.realZoom),
        topLimit = -((sizes.viewBox.y + sizes.viewBox.height) * sizes.realZoom) + gutterHeight,
        bottomLimit = sizes.height - gutterHeight - (sizes.viewBox.y * sizes.realZoom);
};

class Map {
    constructor(element, clickablePlaces, minZoom = 0.7, maxZoom = 5) {
        this.dom = element.contentDocument;
        this.selectedElement = null;
        this.selectedElementColor = null;
        this._panZoomObj = svgPanZoom(element, {
            zoomEnabled: true,
            controlIconsEnabled: false,
            minZoom: minZoom,
            maxZoom: maxZoom,
            zoomScaleSensitivity: 1.5,
            contain: true,
            center: 1,
            beforePan: panLimiter
        });

        this.elementClick = function (element) {
            console.log("Clicked:" + element.id);
            if (this.selectedElement != null) {
                document.getElementById(this.selectedElement.id).style.display = 'none';
                this.selectedElement.style.fill = this.selectedElementColor;
            }
            this.selectedElement = element;
            this.selectedElementColor = element.style.fill;
            document.getElementById(this.selectedElement.id).style.display = 'block';
            this.selectedElement.style.fill = '#FFF';
        };

        for (let place of clickablePlaces) {
            let element = this.dom.getElementById(place);
            if (element != null) {
                element.onclick = function () {
                    this.elementClick(element);
                };
            } else {
                console.log("Unknown identifier: " + place);
            }
        }

        this.toggleLayerVisibility = function (element) {
            if (element.checked) {
                this.dom.getElementById(element.id).style.display = "inline";
            } else {
                this.dom.getElementById(element.id).style.display = "none";
            }
        };
    }
}

const campusMapDefaultLayers = {
    'background': true,
    'roads': true,
    'parking': false,
    'paths': false,
    'labels': true
};
const campusMapPlaces = [
    'edI', 'edII', 'edIII', 'edIV', 'edV', 'edVI', 'edVII', 'edVIII', 'edIX', 'edX',
    'edDepartamental', 'edCantina', 'edBiblioteca',
    /* TODO enable 'edPortaria',*/ 'edCEA', 'camposDesportivos',
    'edHangI', 'edHangII', 'edHangIII', 'edHangIV',
    /* TODO enable 'eMTS', 'eNW', 'eW', 'eSW', 'eE', 'eSE', 'ePte',*/
    /* TODO enable 'tMTS', 'tTST1', 'tTST2', */
    'sCGD', 'sAbreu', 'sCreche', 'sSolucao', 'sDuplix', 'sAEFCT',
    'sBarMininova', 'barBiblioteca', 'barEspaco', 'barCasa', 'barTia', 'barSpot',
    'barTeresa', 'barLidia', 'barGirassol', 'barUninova', 'barCampus'];


class CampusMap extends Map {
    constructor(element) {
        super(element, campusMapPlaces, 0.7, 5);
        for (let place of campusMapPlaces) {
            let element = this.dom.getElementById(place);
            let clickFuncion = this.elementClick;
            if (element != null) {
                let that = this; // If I only had a cent for every time I hated Javascript...
                element.onclick = function () {
                    clickFuncion.call(that, element);
                };
            } else {
                console.log("Unknown identifier: " + place);
            }
        }
        this.resetLayers = function () {
            for (let layer in campusMapDefaultLayers) {
                element = document.getElementById(layer);
                element.checked = campusMapDefaultLayers[layer];
                this.toggleLayerVisibility(element);
            }
            this._panZoomObj.zoomAtPoint(3, {x: 700, y: 400});
        };
        this.resetLayers();
    }
}

class TransportationMap extends Map {
    constructor(element) {
        super(element, campusMapPlaces, 0.7, 5);
        this._panZoomObj.zoomAtPoint(3, {x: 600, y: 300});
    }
}