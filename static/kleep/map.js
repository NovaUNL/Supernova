let mapObject;
let mapDom;
let selectedElement = null;
let selectedElementColor = null;

function reset() {
    mapObject.zoomAtPoint(3, {x: 700, y: 400});
    resetLayers();
}

const defaultLayers = {
    'background': true,
    'roads': true,
    'parking': false,
    'paths': false,
    'labels': true
};

const places = [
    'edI', 'edII', 'edIII', 'edIV', 'edV', 'edVI', 'edVII', 'edVIII', 'edIX', 'edX',
    'edDepartamental', 'edCantina', 'edBiblioteca',
    /* TODO enable 'edPortaria',*/ 'edCEA', 'camposDesportivos',
    'edHangI', 'edHangII', 'edHangIII', 'edHangIV',
    /* TODO enable 'eMTS', 'eNW', 'eW', 'eSW', 'eE', 'eSE', 'ePte',*/
    /* TODO enable 'tMTS', 'tTST1', 'tTST2', */
    'sCGD', 'sAbreu', 'sCreche', 'sSolucao', 'sDuplix', 'sAEFCT',
    'sBarMininova', 'barBiblioteca', 'barEspaco', 'barCasa', 'barTia', 'barSpot',
    'barTeresa', 'barLidia', 'barGirassol', 'barUninova', 'barCampus'];

function toggleVisibility(layer) {
    if (document.getElementById(layer).checked) {
        mapDom.getElementById(layer).style.display = "inline";
    } else {
        mapDom.getElementById(layer).style.display = "none";
    }
}

function resetLayers() {
    for (let layer in defaultLayers) {
        document.getElementById(layer).checked = defaultLayers[layer];
        toggleVisibility(layer);
    }
}

function elementClick(element) {
    console.log("Clicked:" + element.id);
    if (selectedElement != null) {
        document.getElementById(selectedElement.id).style.display = 'none';
        selectedElement.style.fill = selectedElementColor;
    }
    selectedElement = element;
    selectedElementColor = element.style.fill;
    document.getElementById(selectedElement.id).style.display = 'block';
    selectedElement.style.fill = '#FFF';
}

function mapInit() {
    mapDom = document.getElementById("map").contentDocument;
    let beforePan;

    beforePan = function (oldPan, newPan) {
        var gutterWidth = 200,
            gutterHeight = 200,
            sizes = this.getSizes(),
            leftLimit = -((sizes.viewBox.x + sizes.viewBox.width) * sizes.realZoom) + gutterWidth,
            rightLimit = sizes.width - gutterWidth - (sizes.viewBox.x * sizes.realZoom),
            topLimit = -((sizes.viewBox.y + sizes.viewBox.height) * sizes.realZoom) + gutterHeight,
            bottomLimit = sizes.height - gutterHeight - (sizes.viewBox.y * sizes.realZoom);
        customPan = {};
        customPan.x = Math.max(leftLimit, Math.min(rightLimit, newPan.x));
        customPan.y = Math.max(topLimit, Math.min(bottomLimit, newPan.y));
        return customPan
    };

    for (let place of places) {
        let element = mapDom.getElementById(place);
        if (element != null) {
            element.onclick = function () {
                elementClick(element);
            };
        } else {
            console.log("Unknown identifier: " + place);
        }
    }

    mapObject = svgPanZoom('#map', {
        zoomEnabled: true,
        controlIconsEnabled: false,
        minZoom: 0.7,
        maxZoom: 5,
        zoomScaleSensitivity: 1.5,
        contain: true,
        center: 1,
        beforePan: beforePan
    });

    document.getElementById("map").style.display = 'inline-block';
    document.getElementById("layers").style.display = 'inline-block';
    reset();
}