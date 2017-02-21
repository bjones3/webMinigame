var sendToServer = function(endpoint, data, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
			    callback(JSON.parse(this.responseText));
            } else if (this.status == 400) {
                console.log(this.responseText);
                alert('Action not allowed.');
            } else if (this.status == 401) {
                console.log(this.responseText);
                alert('Invalid Password.');
                window.location.href = '/';
            } else if (this.status == 403) {
                console.log(this.responseText);
                alert('Username already taken.');
                window.location.href = '/';
            }
        }
    };
    xhttp.open('POST', endpoint, true);
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.send(JSON.stringify(data));
};

var getFromServer = function(endpoint, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
           if (this.status == 200) {
			    callback(JSON.parse(this.responseText));
           } else if (this.status == 400) {
                alert('Action not allowed.');
           }
        }
    };
    xhttp.open('GET', endpoint, true);
    xhttp.send();
};