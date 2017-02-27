var GAME_CONFIG = null;

var state = null;

var hideFlash = function() {
  var element = document.getElementById('flash');
  flash.classList.remove('in');
  flash.classList.add('out');

};

var showFlash = function(message) {
  var element = document.getElementById('flash');
  element.innerHTML = message;
  flash.classList.remove('out');
  flash.classList.add('in');
  setTimeout(hideFlash, 1500);
};

var logElement = function(msg) {
    var div = document.createElement("DIV");
    var txt = document.createTextNode(msg);
    div.appendChild(txt);
    var container = document.getElementById("notificationPanel");
    container.appendChild(div);
    container.scrollTop = div.offsetTop;
};

var server = new Server(showFlash, logElement);

var loadGameState = function() {
    slug = localStorage.getItem('slug');
    var data = {
        password: localStorage.getItem('pwd_' + slug),
        newOrLoad: "load"
    };
    var gameStateLoaded = function(gameState) {
        state = gameState;
        reset();
    };
    server.sendToServer("/game-state/" + window.location.hash.substring(1), data, gameStateLoaded);
};

var loadGameConfig = function() {
    var gameConfigLoaded = function(gameConfig) {
        GAME_CONFIG = gameConfig;
        loadGameState();
    };
    server.getFromServer("/game-config", gameConfigLoaded);
};

var setElementDisplay = function(name, i, j, display) {
    var id = name + i + ',' + j;
    var element = document.getElementById(id);
    element.style.display = display;
    return element;
};

var hideElement = function(name, i, j) {
    return setElementDisplay(name, i, j, "none");
};

var showElement = function(name, i, j) {
    return setElementDisplay(name, i, j, "block");
};

var reset = function() {
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if (state["plot" + i + "," + j].seedType != 0 && state["plot" + i + "," + j].locked == 0) {
                for (var seed in GAME_CONFIG.seeds) {
                    hideElement("sow" + seed, i, j);
                }
                var growingImage = showElement("growing", i, j);
                growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[state["plot" + i + "," + j].seedType].imageLarge + ")";
                hideElement("soil", i, j);
                showElement("progressBar", i, j);
                hideElement("lock", i, j);
            } else {
                for (var seed in GAME_CONFIG.seeds) {
                    if (state.seedCounts[seed] > 0 && state["plot" + i + "," + j].locked == 0) {
                        showElement("sow" + seed, i, j);
                    }
                }
                hideElement("growing", i, j);
                if (state["plot" + i + "," + j].locked == 0) {
                    showElement("soil", i, j);
                    hideElement("lock", i, j);
                }
                hideElement("progressBar", i, j);
            }
        }
    }
    document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
    document.getElementById("buyPlot").innerHTML = "Buy Plot - $" + GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'],state.unlockCount);
    for (var seed in GAME_CONFIG.seeds) {
        if (GAME_CONFIG.seeds.hasOwnProperty(seed)) {
            var seedConfig = GAME_CONFIG.seeds[seed];
        }
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
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
    if (state.resources.cash < GAME_CONFIG.seeds[seed].buyCost) {
        showFlash("Not enough cash.");
        return;
    };
    var callback = function(newState) {
        state = newState;
        logElement("Bought 1 " + GAME_CONFIG.seeds[seed].name + " seed.")
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if(state["plot" + i + "," + j].seedType == 0 && state["plot" + i + "," + j].locked == 0) {
                    showElement("sow" + seed, i, j);
                }
            };
        };
    };
    var data = {
        slug: state.slug,
        seed: seed,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/buy', data, callback);
};

var sell = function(seed) {
    if (state.seedCounts[seed] <= 0) {
        showFlash("No " + GAME_CONFIG.seeds[seed].name + " seeds to sell.");
        return;
    };
    var callback = function(newState) {
        state = newState;
        logElement("Sold 1 " + GAME_CONFIG.seeds[seed].name + " seed.")
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if(state.seedCounts[seed] == 0) {
                    hideElement("sow" + seed, i, j);
                }
            };
        };
    };
    var data = {
        slug: state.slug,
        seed: seed,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/sell', data, callback);
};

var sow = function(x, y, seed) {
    if (state.seedCounts[seed] <= 0) {
        showFlash("No " + GAME_CONFIG.seeds[seed].name + " seeds to plant.");
        return;
    };
    var callback = function(newState) {
        state = newState;
        logElement("Planted 1 " + GAME_CONFIG.seeds[seed].name + " seed.")
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        var plotBox = document.getElementById("plot" + x + "," + y);
        var sowButtons = plotBox.getElementsByClassName("sowPlantButton");
        for(var i = 0; i < sowButtons.length; i++) {
            sowButtons[i].style.display = "none";
        }
        if (state.seedCounts[seed] == 0) {
            for (var i = 0; i < GAME_CONFIG.field_width; i++) {
                for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                    hideElement("sow" + seed, i, j);
                }
            }
        }
        var growingImage = showElement("growing", x, y);
        growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seed].imageLarge + ")";
        hideElement("soil", x, y);

        tick();
        showElement("progressBar", x, y);

    };
    var data = {
        slug: state.slug,
        seed: seed,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    }
    server.sendToServer('/action/sow', data, callback);
};

var harvest = function(x, y) {
    var callback = function(newState) {
        var seed = state["plot" + x + "," + y].seedType;
        state = newState;
        logElement("Harvested 1 " + GAME_CONFIG.seeds[seed].name + " seed.")
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        for (var s in GAME_CONFIG.seeds) {
            if (state.seedCounts[s] > 0) {
                showElement("sow" + s, x, y);
            }
        };
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if(state["plot" + i + "," + j].seedType == 0 && state.seedCounts[seed] > 0 && state["plot" + i + "," + j].locked == 0) {
                    showElement("sow" + seed, i , j);
                }
            };
        };
        var growingImage = hideElement("growing", x, y);
        growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seed].imageLarge + ")";
        showElement("soil", x, y);
        hideElement("button", x, y);
    };
    var data = {
        slug: state.slug,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/harvest', data, callback);
};

var unlock = function(x, y) {
    if (state.resources.cash < GAME_CONFIG.plotPrice * Math.pow(GAME_CONFIG.plotMultiplier,state.unlockCount)) {
            showFlash("Not enough cash.");
            return;
    }
    var callback = function(newState) {
        state = newState;
        logElement("Unlocked a new plot!")
        state["plot" + x + "," + y].locked = 0;
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        document.getElementById("buyPlot").innerHTML = "Buy Plot - $" + GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'],state.unlockCount);
        hideElement("lock", x, y);
        showElement("soil", x, y);
        for (var s in GAME_CONFIG.seeds) {
            if (state.seedCounts[s] > 0) {
                showElement("sow" + s, x, y);
            }
        }
    };
    var data = {
        slug: state.slug,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/unlock', data, callback);
};

var buyPlot = function() {
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if (state["plot" + i + "," + j].locked == 1) {
                unlock(i, j);
                return;
            }
        }
    }
};

var tick = function() {
    if (state == null) {
        return;
    }
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if(state["plot" + i + "," + j].seedType != 0) {
                var startTime = state["plot" + i + "," + j].sowTime;
                var currentTime = new Date().getTime();
                var timePassed = Math.floor((currentTime - startTime) / 1000);
                var typeSeed = state["plot" + i + "," + j].seedType;
                var harvestTime = GAME_CONFIG.seeds[typeSeed].harvestTimeSeconds;
                var countdown = harvestTime - timePassed;
                var percentTimeLeft = countdown / harvestTime;
                document.getElementById("filler" + i + "," + j).style.width = percentTimeLeft * 100 + "%";
                var toHHMMSS = function(sec_num) {
                    var hours   = Math.floor(sec_num / 3600);
                    var minutes = Math.floor((sec_num % 3600) / 60);
                    var seconds = Math.floor(sec_num % 60);

                    if (hours   < 10) {hours   = "0" + hours;}
                    if (minutes < 10) {minutes = "0" + minutes;}
                    if (seconds < 10) {seconds = "0" + seconds;}

                    if (hours   <= 0) {return minutes + ':' + seconds;}
                    return hours + ':' + minutes + ':' + seconds;
                };
                var clockDisplay = toHHMMSS(countdown);
                document.getElementById("time" + i + "," + j).innerHTML = clockDisplay;
                if (countdown <= 0) {
                    hideElement("progressBar", i, j);
                    showElement("button", i, j);
                }
            };
        };
    };
};

setInterval(tick, 100);
