// image and canvas
var image = new Image();
var canvas = document.getElementById("paint");
image.onload = function () {

    canvas.width = image.width;
    canvas.height = image.height;
};
image.src = '/static/temp/background.png';
var ctx = canvas.getContext("2d");
ctx.font = "22px Verdana";
var width = $("/static/temp/background.png").width();
var height = $("/static/temp/background.png").height();
var hold = false;
ctx.lineWidth = 2;
ctx.strokeStyle = '#00000FF';
ctx.fillStyle = '#0000FF';
var fill_value = true;
var stroke_value = false;
var brushRadius = 8;
var eraserOn1 = false;

var colors = ['#0000FF', '#00FF00', '#00FFFF', '#FF0000', '#FF00FF', '#FFFF00'];

function eraser(isOn) {
    if (isOn == true)
        eraserOn1 = true;
    if (isOn == false)
        eraserOn1 = false;
}

function color(color_value) {
        ctx.strokeStyle = color_value;
        ctx.fillStyle = color_value;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    LoadLayer(color_value);
    repaint(curves);
    repaint(curves1);
}

function add_pixel() {
    ctx.lineWidth += 1;
}

function reduce_pixel() {
    if (ctx.lineWidth == 1) {
        ctx.lineWidth = 1;
    }
    else {
        ctx.lineWidth -= 1;
    }
}

function restoreLayer() {

}

function fill() {
    fill_value = true;
    stroke_value = false;
}

function outline() {
    fill_value = false;
    stroke_value = true;
}

function LoadLayer(color_value) {
    var img1 = new Image();
    var currentLayer = new Image();
    currentLayer.onload = function () {
        ctx.drawImage(currentLayer, 0, 0);
    };
    switch (color_value) {  
        case '#0000FF':
            img1.src = '/static/temp/edit_salinity.png';
            img1.onload = function () { currentLayer.src = '/static/temp/edit_salinity.png'; };
            img1.onerror = function () { currentLayer.src = '/static/temp/layer_salinity.png'; };
            break;
        case '#00FF00':

            img1.src = '/static/temp/edit_corrosion.png';
            img1.onload = function () { currentLayer.src = '/static/temp/edit_corrosion.png'; };
            img1.onerror = function () { currentLayer.src = '/static/temp/layer_corrosion.png'; };
            break;
        case '#00FFFF':

            img1.src = '/static/temp/edit_pitting.png';
            img1.onload = function () { currentLayer.src = '/static/temp/edit_pitting.png'; };
            img1.onerror = function () { currentLayer.src = '/static/temp/layer_pitting.png'; };
            break;
        case '#FF0000':

            img1.src = '/static/temp/edit_oil.png';
            img1.onload = function () { currentLayer.src = '/static/temp/edit_oil.png'; };
            img1.onerror = function () { currentLayer.src = '/static/temp/layer_oil.png'; };
            break;
        case '#FF00FF':

            img1.src = '/static/temp/edit_recess.png';
            img1.onload = function () { currentLayer.src = '/static/temp/edit_recess.png'; };
            img1.onerror = function () { currentLayer.src = '/static/temp/layer_recess.png'; };
            break;
        case '#FFFF00':

            img1.src = '/static/temp/edit_ext_recess.png';
            img1.onload = function () { currentLayer.src = '/static/temp/edit_ext_recess.png'; };
            img1.onerror = function () { currentLayer.src = '/static/temp/layer_ext_recess.png'; };
            break;
        default:
            break;
    }
}

function pencil() {
    var default_color = '#0000FF';
    ctx.strokeStyle = default_color;
    ctx.fillStyle = default_color;
    LoadLayer(default_color);

    var curves = [];
    function makePoint(x, y) {
        return [x, y];
    };

    canvas.addEventListener("mousedown", event => {

        const curve = [];
        curve.eraserOn = false;
        if (eraserOn1 == true)
            curve.eraserOn = true;
        curve.color = ctx.strokeStyle;
        curve.lineWidth = ctx.lineWidth;
        curve.push(makePoint(event.offsetX, event.offsetY));
        
        curves.push(curve);

        hold = true;
    });

    canvas.addEventListener("mousemove", event => {                       
        if (hold) {
            const point = makePoint(event.offsetX, event.offsetY)
            curves[curves.length - 1].push(point);
            repaint(curves);
        }
    });

    canvas.addEventListener("mouseup", event => {
        hold = false;
    });

    canvas.addEventListener("mouseleave", event => {
        hold = false;
    });
}

function repaint(curves1) {

    curves1.forEach((curve) => {

        if (ctx.strokeStyle == curve.color) {
            ctx.lineWidth = curve.lineWidth;
       
            circle(curve[0]);
            smoothCurve(curve, curve.eraserOn, curve.color);
        }
    });
}

function circle(point) {

    ctx.beginPath();
    ctx.arc(...point, brushRadius / 2, 0, 2 * Math.PI);
    ctx.fill();
}

function smoothCurveBetween(p1, p2) {

    const cp = p1.map((coord, idx) => (coord + p2[idx]) / 2);
    ctx.quadraticCurveTo(...p1, ...cp);
}

function smoothCurve(points, isEraser, color) {

    ctx.beginPath();
    ctx.lineWidth = brushRadius;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    ctx.moveTo(...points[0]);

   
    for (let i = 1; i < points.length - 1; i++) {
        smoothCurveBetween(points[i], points[i + 1]);
        }
    if (isEraser == true) {
        ctx.globalCompositeOperation = "destination-out";
        ctx.strokeStyle = "rgba(255,255,255,1)";
    }
    if (isEraser == false) {
        ctx.globalCompositeOperation = "source-over";
        ctx.strokeStyle = color;
    }
    ctx.stroke();
    ctx.globalCompositeOperation = "source-over";
    ctx.strokeStyle = color;
    
}

function save() {
        document.getElementById("canvasimg").value = canvas.toDataURL();
}
