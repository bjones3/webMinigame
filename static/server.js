var Server = function(alertCallback, infoCallback) {
    this.sendToServer = function(endpoint, data, callback) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    response = JSON.parse(this.responseText);
                    if (response.message) {
                        infoCallback(response.message);
                    }
                    if (response.state) {
                        callback(response.state,response.recipes);
                    }
                } else if (this.status == 400) {
                    alertCallback(this.responseText);
                } else if (this.status == 401) {
                    alertCallback(this.responseText);
                    setTimeout(function () {
                        window.location.href = '/';
                    }, 2500);
                } else if (this.status == 403) {
                    alertCallback(this.responseText);
                } else if (this.status == 404) {
                    alertCallback(this.responseText);
                } else if (this.status == 503) {
                    alertCallback("Trouble contacting server");
                } else {
                    infoCallback("Unknown error: %s" % this.status);
                }
            }
        };
        xhttp.open('POST', endpoint, true);
        xhttp.setRequestHeader('Content-type', 'application/json');
        xhttp.send(JSON.stringify(data));
    };

    this.getFromServer = function(endpoint, callback) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
               if (this.status == 200) {
                    callback(JSON.parse(this.responseText));
               } else if (this.status == 400) {
                    alertCallback('Action not allowed.');
               }
            }
        };
        xhttp.open('GET', endpoint, true);
        xhttp.send();
    }
};