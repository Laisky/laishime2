if(top.location != self.location){
    top.location.replace(self.location);
}

// document.getElementById("test_footer").onmousedown = initWindow;
window.onload = initWindow;

function initWindow() {
    var req = new XMLHttpRequest();
    // var req = createCORSRequest("GET", "http://laishime.sinaapp.com/tweets?source=twitter&topic=py");
    req.open(
            "GET",
            "http://laishime.sinaapp.com/tweets?source=twitter&topic=py",
            false
    );
    req.send(null);

    alert(req.responseText);
    document.write(req.responseText);
}
