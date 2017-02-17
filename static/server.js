var sendToServer = function(endpoint, data, callback) {
    var handleResponse = function(event) {
	    var xhr = event.target;
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
			    callback(JSON.parse(xhr.responseText));
            } else if (xhr.status == 400) {
                console.log(xhr.responseText);
                alert('Action not allowed.');
            } else if (xhr.status == 401) {
                console.log(xhr.responseText);
                alert('Invalid Password.');
                window.location.href = '/';
            }
        }
    };
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = handleResponse;
    xhr.open('POST', endpoint, true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.send(JSON.stringify(data));
};