

var GAME_CONFIG = null;

// var GAME_CONFIG_JSON = JSON.stringify(GAME_CONFIG);

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
    //xhr.open('POST', '/save/' + game_name, true);
    xhr.open('POST', endpoint, true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.send(JSON.stringify(data));
};

var loadGameState = function() {
    var gameStateLoaded = function(gameState) {
        state = gameState;
        reset();
    }
    console.log(window.location.hash);
    getFromServer("/game-state/" + window.location.hash.substring(1), gameStateLoaded);
}

var saveGameState = function() {
    var gameStateSaved = function() {
    }
    sendToServer("/save/" + state.slug, state, gameStateSaved);
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
                idDisplay("alfalfa" + i + j, "none");
                idDisplay("broccoli" + i + j, "none");
                idDisplay("cabbage" + i + j, "none");
                var growingImage = document.getElementById("growing" + i + j);
                growingImage.style.display = "block";
                growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[state["plot" + i + j].seedType].imageLarge + ")";
                idDisplay("soil" + i + j, "none");
                idDisplay("progressBar" + i + j, "block");
            } else {
                idDisplay("alfalfa" + i + j, "block");
                idDisplay("broccoli" + i + j, "block");
                idDisplay("cabbage" + i + j, "block");
                idDisplay("growing" + i + j, "none");
                idDisplay("soil" + i + j, "block");
                idDisplay("progressBar" + i + j, "none");
            }
        }
    }
    document.getElementById("cash").innerHTML = "CASH: $" + state.cash;
    document.getElementById("owneda").innerHTML = state.a;
    document.getElementById("ownedb").innerHTML = state.b;
    document.getElementById("ownedc").innerHTML = state.c;
    document.getElementById("buyA").innerHTML = "$" + GAME_CONFIG.seeds.a.buyCost;
    document.getElementById("buyB").innerHTML = "$" + GAME_CONFIG.seeds.b.buyCost;
    document.getElementById("buyC").innerHTML = "$" + GAME_CONFIG.seeds.c.buyCost;
    document.getElementById("sellA").innerHTML = "$" + GAME_CONFIG.seeds.a.sellCost;
    document.getElementById("sellB").innerHTML = "$" + GAME_CONFIG.seeds.b.sellCost;
    document.getElementById("sellC").innerHTML = "$" + GAME_CONFIG.seeds.c.sellCost;
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
    state[seed] ++;
    document.getElementById("owned" + seed).innerHTML = state[seed];
    state.cash -= GAME_CONFIG.seeds[seed].buyCost;
    document.getElementById("cash").innerHTML = "CASH: $" + state.cash;
    saveGameState();
};

var sell = function(seed) {
    if (state[seed] <= 0) {
        window.alert("No " + GAME_CONFIG.seeds[seed].name + " seeds to sell.");
        return;
    };
    state[seed] --;
    document.getElementById("owned" + seed).innerHTML = state[seed];
    state.cash += GAME_CONFIG.seeds[seed].sellCost;
    document.getElementById("cash").innerHTML = "CASH: $" + state.cash;
    saveGameState();
};

var sow = function(x, y, seed) {
    if (state[seed] <= 0) {
        window.alert("No " + GAME_CONFIG.seeds[seed].name + " seeds to plant.");
        return;
    };
    state[seed] --;
    document.getElementById("owned" + seed).innerHTML = state[seed];
    var plotBox = document.getElementById("plot" + x + y);
    var sowButtons = plotBox.getElementsByClassName("sowPlantButton");
    for(var i = 0; i < sowButtons.length; i++) {
        sowButtons[i].style.display = "none";
    }
    var growingImage = document.getElementById("growing" + x + y);
    growingImage.style.display = "block";
    growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seed].imageLarge + ")";
    var soil = document.getElementById("soil" + x + y);
    soil.style.display = "none";
    state["plot" + x + y].seedType = seed;
    state["plot" + x + y].sowTime = new Date().getTime();
    tick();
    var progressBar = document.getElementById("progressBar" + x + y);
    progressBar.style.display = "block";
    saveGameState();
};

var harvest = function(x, y) {
    var seed = state["plot" + x + y].seedType;
    state[seed] += GAME_CONFIG.seeds[seed].harvestYield;
    document.getElementById("owned" + seed).innerHTML = state[seed];
    var plotBox = document.getElementById("plot" + x + y);
    var sowButtons = plotBox.getElementsByClassName("sowPlantButton");
    for(var i = 0; i < sowButtons.length; i++) {
        sowButtons[i].style.display = "block";
    };
    var growingImage = document.getElementById("growing" + x + y);
    growingImage.style.display = "none";
    growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seed].imageLarge + ")";
    var soil = document.getElementById("soil" + x + y);
    soil.style.display = "block";
    var button = document.getElementById("button" + x + y);
    button.style.display = "none";
    state["plot" + x + y].seedType = 0;
    saveGameState();
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