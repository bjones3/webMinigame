var GAME_CONFIG = null;

var state = null;

var getFromServer = function(endpoint, callback) {
    var handleResponse = function(event) {
	    var xhr = event.target;
        if (xhr.readyState == 4) {
           if (xhr.status == 200) {
			    callback(JSON.parse(xhr.responseText));
           } else if (xhr.status == 400) {
                alert('Action not allowed.');
           }
        }
    };
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = handleResponse;
    xhr.open('GET', endpoint, true);
    xhr.send();
};

var sendToServer = function(endpoint, data, callback) {
    var handleResponse = function(event) {
	    var xhr = event.target;
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
			    callback(JSON.parse(xhr.responseText));
            } else if (xhr.status == 400) {
                console.log(xhr.responseText);
                alert('Action not allowed.');
            }
        }
    };
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = handleResponse;
    xhr.open('POST', endpoint, true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.send(JSON.stringify(data));
};

var loadGameState = function() {
    var gameStateLoaded = function(gameState) {
        state = gameState;
        reset();
    }
    getFromServer("/game-state/" + window.location.hash.substring(1), gameStateLoaded);
}

var loadGameConfig = function() {
    var gameConfigLoaded = function(gameConfig) {
        GAME_CONFIG = gameConfig;
        loadGameState();
    }
    getFromServer("/game-config", gameConfigLoaded);
}

var reset = function() {
    idDisplay = function(idName, displayType) {
        var x = document.getElementById(idName);
        x.style.display = (displayType);
    };
    for (var i = 0; i <= 2; i++) {
        for (var j = 0; j <= 2; j++) {
            if(state["plot" + i + j].seedType != 0) {
                for (var seed in GAME_CONFIG.seeds) {
                    idDisplay("sow" + seed + i + j, "none");
                }
                var growingImage = document.getElementById("growing" + i + j);
                growingImage.style.display = "block";
                growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[state["plot" + i + j].seedType].imageLarge + ")";
                idDisplay("soil" + i + j, "none");
                idDisplay("progressBar" + i + j, "block");
            } else {
                for (var seed in GAME_CONFIG.seeds) {
                    if (state[seed] > 0) {
                        idDisplay("sow" + seed + i + j, "block");
                    }
                }
                idDisplay("growing" + i + j, "none");
                idDisplay("soil" + i + j, "block");
                idDisplay("progressBar" + i + j, "none");
            }
        }
    }
    document.getElementById("cash").innerHTML = "CASH: $" + state.cash;
    for (var seed in GAME_CONFIG.seeds) {
        if (GAME_CONFIG.seeds.hasOwnProperty(seed)) {
            var seedConfig = GAME_CONFIG.seeds[seed];
        }
        document.getElementById("owned" + seed).innerHTML = state[seed];
        document.getElementById("buy" + seed).innerHTML = "$" + seedConfig.buyCost;
        document.getElementById("sell" + seed).innerHTML = "$" + seedConfig.sellCost;
    };
};

document.onreadystatechange = function() {
    if (document.readyState === 'complete') {
        loadGameConfig();
    }
};

var buy = function(seed) {
    if (state.cash < GAME_CONFIG.seeds[seed].buyCost) {
        window.alert("Not enough cash.");
        return;
    };
    var callback = function(newState) {
        state = newState;
        document.getElementById("owned" + seed).innerHTML = state[seed];
        document.getElementById("cash").innerHTML = "CASH: $" + state.cash;
        for (var i = 0; i <= 2; i++) {
            for (var j = 0; j <= 2; j++) {
                if(state["plot" + i + j].seedType == 0) {
                    document.getElementById("sow" + seed + i + j).style.display = "block"
                }
            };
        };
    };
    var data = {
        slug: state.slug,
        seed: seed
    };
    sendToServer('/action/buy', data, callback);
};

var sell = function(seed) {
    if (state[seed] <= 0) {
        window.alert("No " + GAME_CONFIG.seeds[seed].name + " seeds to sell.");
        return;
    };
    var callback = function(newState) {
        state = newState;
        document.getElementById("owned" + seed).innerHTML = state[seed];
        document.getElementById("cash").innerHTML = "CASH: $" + state.cash;
        for (var i = 0; i <= 2; i++) {
            for (var j = 0; j <= 2; j++) {
                if(state[seed] == 0) {
                    document.getElementById("sow" + seed + i + j).style.display = "none"
                }
            };
        };
    };
    var data = {
        slug: state.slug,
        seed: seed
    };
    sendToServer('/action/sell', data, callback);
};

var sow = function(x, y, seed) {
    if (state[seed] <= 0) {
        window.alert("No " + GAME_CONFIG.seeds[seed].name + " seeds to plant.");
        return;
    };
    var callback = function(newState) {
        state = newState;
        document.getElementById("owned" + seed).innerHTML = state[seed];
        var plotBox = document.getElementById("plot" + x + y);
        var sowButtons = plotBox.getElementsByClassName("sowPlantButton");
        for(var i = 0; i < sowButtons.length; i++) {
            sowButtons[i].style.display = "none";
        }
        if (state[seed] == 0) {
            for (var i = 0; i <= 2; i++) {
                for (var j = 0; j <= 2; j++) {
                    document.getElementById("sow" + seed + i + j).style.display = "none";
                }
            }
        }
        var growingImage = document.getElementById("growing" + x + y);
        growingImage.style.display = "block";
        growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seed].imageLarge + ")";
        var soil = document.getElementById("soil" + x + y);
        soil.style.display = "none";

        tick();
        var progressBar = document.getElementById("progressBar" + x + y);
        progressBar.style.display = "block";

    };
    var data = {
        slug: state.slug,
        seed: seed,
        x: x,
        y: y
    }
    sendToServer('/action/sow', data, callback);
};

var harvest = function(x, y) {
    var callback = function(newState) {
        var seed = state["plot" + x + y].seedType;
        state = newState;
        document.getElementById("owned" + seed).innerHTML = state[seed];
        for (var s in GAME_CONFIG.seeds) {
            if (state[s] > 0) {
                document.getElementById("sow" + s + x + y).style.display = "block";
            }
        };
        for (var i = 0; i <= 2; i++) {
            for (var j = 0; j <= 2; j++) {
                if(state["plot" + i + j].seedType == 0 && state[seed] > 0) {
                    document.getElementById("sow" + seed + i + j).style.display = "block"
                }
            };
        };
        var growingImage = document.getElementById("growing" + x + y);
        growingImage.style.display = "none";
        growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seed].imageLarge + ")";
        var soil = document.getElementById("soil" + x + y);
        soil.style.display = "block";
        var button = document.getElementById("button" + x + y);
        button.style.display = "none";
    };
    var data = {
        slug: state.slug,
        x: x,
        y: y
    }
    sendToServer('/action/harvest', data, callback);
};

var tick = function() {
    if (state == null) {
        return;
    }
    for (var i = 0; i <= 2; i++) {
        for (var j = 0; j <= 2; j++) {
            if(state["plot" + i + j].seedType != 0) {
                var startTime = state["plot" + i + j].sowTime;
                var currentTime = new Date().getTime();
                var timePassed = Math.floor((currentTime - startTime) / 1000);
                var typeSeed = state["plot" + i + j].seedType;
                var harvestTime = GAME_CONFIG.seeds[typeSeed].harvestTimeSeconds;
                var countdown = harvestTime - timePassed;
                var percentTimeLeft = countdown / harvestTime;
                document.getElementById("filler" + i + j).style.width = percentTimeLeft * 100 + "%";
                var clockDisplay = '0' + Math.floor(countdown / 60) + ":" + countdown % 60;
                if (countdown % 60 < 10) {
                    clockDisplay = '0' + Math.floor(countdown / 60) + ":0" + countdown % 60;
                }
                document.getElementById("time" + i + j).innerHTML = clockDisplay;
                if (countdown <= 0) {
                    document.getElementById("progressBar" + i + j).style.display = "none";
                    document.getElementById("button" + i + j).style.display = "block";
                }
            };
        };
    };
};

setInterval(tick, 100);