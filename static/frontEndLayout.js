var GAME_CONFIG = null;
var RECIPE_CONFIG = null;
var state = null;

var hideFlash = function() {
  var element = document.getElementById('flash');
  flash.classList.remove('in');
  flash.classList.add('out');
}
var showFlash = function(message) {
  var element = document.getElementById('flash');
  element.innerHTML = message;
  flash.classList.remove('out');
  flash.classList.add('in');
  setTimeout(hideFlash, 1500);
}

var setElementDisplay = function(name, x, y, display) {
    var id = name + x + '_' + y;
    var element = document.getElementById(id);
    element.style.display = display;
    return element;
}
var hideElement = function(name, x, y) {
    return setElementDisplay(name, x, y, "none");
}
var showElement = function(name, x, y) {
    return setElementDisplay(name, x, y, "block");
}

var toolTip = function(msg, id) {
    var span = document.createElement("SPAN");
    span.classList.add("tooltiptext");
    var txt = document.createTextNode(msg);
    span.appendChild(txt);
    var container = document.getElementById(id);
    container.classList.add("tooltip");
    container.appendChild(span);
}



var gettingStarted = function() {
    var buyBtn = document.getElementById("buya");
    toolTip("Buy a " + GAME_CONFIG.seeds[GAME_CONFIG.firstSeed].name + " seed", "buya");
    buyBtn.style.animationName = 'borderChange';
    buyBtn.style.animationDuration = '2s';
    buyBtn.style.animationIterationCount = 'infinite';
    buyBtn.addEventListener('click', afterBuy);
}
var afterBuy = function() {
    var buyBtn = document.getElementById("buya");
    var sowBtn = document.getElementsByClassName("sowPlantButton");
    var tooltip = document.getElementsByClassName("tooltiptext");
    for(var i = 0; i < tooltip.length; i++) {
        tooltip[i].style.display = "none";
    }
    toolTip("Plant seed", "sowa0_0");
    buyBtn.style.animationIterationCount = '0';
    for (var i = 0; i < sowBtn.length; i++) {
        sowBtn[i].style.animationName = 'borderChange';
        sowBtn[i].style.animationDuration = '2s';
        sowBtn[i].style.animationIterationCount = 'infinite';
        sowBtn[i].addEventListener('click', afterSow);
    }
}
var afterSow = function() {
    var sowBtn = document.getElementsByClassName("sowPlantButton");
    var tooltip = document.getElementsByClassName("tooltiptext");
    for(var i = 0; i < tooltip.length; i++) {
        tooltip[i].style.display = "none";
    }
    for (var i = 0; i < sowBtn.length; i++) {
        sowBtn[i].style.animationIterationCount = '0';
    }
    localStorage.setItem("newOrLoad", "load");
}

var logElement = function(msg) {
    var div = document.createElement("DIV");
    var txt = document.createTextNode(msg);
    div.appendChild(txt);
    var container = document.getElementById("notificationPanel");
    container.appendChild(div);
    container.scrollTop = div.offsetTop;
}

var server = new Server(showFlash, logElement);

var loadGameState = function() {
    slug = localStorage.getItem('slug');
    var data = {
        password: localStorage.getItem('pwd_' + slug),
        newOrLoad: "load"
    };
    var gameStateLoaded = function(gameState) {
        state = gameState;
        fetchRecipes();
        reset();
    }
    server.sendToServer("/game-state/" + window.location.hash.substring(1), data, gameStateLoaded);
}

var loadGameConfig = function() {
    var gameConfigLoaded = function(gameConfig) {
        GAME_CONFIG = gameConfig;
        loadGameState();
    }
    server.getFromServer("/game-config", gameConfigLoaded);
}



var reset = function() {
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if (state['plot' + i + "_" + j].seedType != 0 && state['plot' + i + "_" + j].locked == 0) {
                for (var seed in GAME_CONFIG.seeds) {
                    hideElement("sow" + seed, i, j);
                }
                var growingImage = showElement("growing", i, j);
                growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[state['plot' + i + "_" + j].seedType].imageLarge + ")";
                hideElement("soil", i, j);
                showElement("progressBar", i, j);
                hideElement("lock", i, j);
            } else {
                for (var seed in GAME_CONFIG.seeds) {
                    if (state.seedCounts[seed] > 0 && state['plot' + i + "_" + j].locked == 0) {
                        showElement("sow" + seed, i, j);
                    }
                }
                hideElement("growing", i, j);
                if (state['plot' + i + "_" + j].locked == 0) {
                    showElement("soil", i, j);
                    hideElement("lock", i, j);
                }
                hideElement("progressBar", i, j);
            }
        }
    }
    document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
    document.getElementById("carrots").innerHTML = "CARROTS: " + state.resources.carrots;
    document.getElementById("grass").innerHTML = "GRASS: " + state.resources.grass;
    document.getElementById("fertilizer").innerHTML = "FERTILIZER: " + state.resources.fertilizer;
    buyMsg = "Click any plot to unlock - $" + GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'],state.unlockCount);
    document.getElementById("buyPlot").innerHTML = buyMsg;
}

document.onreadystatechange = function() {
    if (document.readyState === 'complete') {
        loadGameConfig();
    }
};

var buy = function(recipeID) {
    if (state.resources.cash < RECIPE_CONFIG[recipeID].cashCost) {
        showFlash("Not enough cash.");
        return;
    }
    if (state.resources.carrots < RECIPE_CONFIG[recipeID].carrotsCost) {
        showFlash("Not enough carrots.");
        return;
    }
    if (state.resources.grass < RECIPE_CONFIG[recipeID].grassCost) {
        showFlash("Not enough grass.");
        return;
    }
    if (state.resources.fertilizer < RECIPE_CONFIG[recipeID].fertilizerCost) {
        showFlash("Not enough fertilizer.");
        return;
    }
    if (state.seedCounts[recipeID] == GAME_CONFIG.max_seed_count) {
        showFlash("Can't buy any more " + GAME_CONFIG.seeds[recipeID].name + " seeds.");
        return;
    }
    var callback = function(newState) {
        state = newState;
        document.getElementById("owned" + recipeID).innerHTML = state.seedCounts[recipeID];
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        document.getElementById("carrots").innerHTML = "CARROTS: " + state.resources.carrots;
        document.getElementById("grass").innerHTML = "GRASS: " + state.resources.grass;
        document.getElementById("fertilizer").innerHTML = "FERTILIZER: " + state.resources.fertilizer;
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if(state['plot' + i + "_" + j].seedType == 0 && state['plot' + i + "_" + j].locked == 0) {
                    showElement("sow" + recipeID, i, j);
                }
            }
        }
    }
    var data = {
        slug: state.slug,
        recipe_id: recipeID,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/buy', data, callback);
}

var sell = function(seed) {
    if (state.seedCounts[seed] <= 0) {
        showFlash("No " + GAME_CONFIG.seeds[seed].name + " seeds to sell.");
        return;
    }
    var callback = function(newState) {
        state = newState;
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if(state.seedCounts[seed] == 0) {
                    hideElement("sow" + seed, i, j);
                }
            }
        }
    }
    var data = {
        slug: state.slug,
        seed: seed,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/sell', data, callback);
}

var sow = function(x, y, seed) {
    if (state.seedCounts[seed] <= 0) {
        showFlash("No " + GAME_CONFIG.seeds[seed].name + " seeds to plant.");
        return;
    }
    if (state["plot" + x + "_" + y].seedType != 0) {
        showFlash("A seed is already planted here.");
    }
    var callback = function(newState) {
        state = newState;
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        var plotBox = document.getElementById("plot" + x + "_" + y);
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

    }
    var data = {
        slug: state.slug,
        seed: seed,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    }
    server.sendToServer('/action/sow', data, callback);
}

var harvest = function(x, y) {
    var callback = function(newState) {
        var seed = state["plot" + x + "_" + y].seedType;
        state = newState;
        fetchRecipes();
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        document.getElementById("carrots").innerHTML = "CARROTS: " + state.resources.carrots;
        document.getElementById("grass").innerHTML = "GRASS: " + state.resources.grass;
        document.getElementById("fertilizer").innerHTML = "FERTILIZER: " + state.resources.fertilizer;

        for (var s in GAME_CONFIG.seeds) {
            if (state.seedCounts[s] > 0) {
                showElement("sow" + s, x, y);
            }
        }
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if(state['plot' + i + "_" + j].seedType == 0 && state.seedCounts[seed] > 0 && state['plot' + i + "_" + j].locked == 0) {
                    showElement("sow" + seed, i , j);
                }
            }
        }
        var growingImage = hideElement("growing", x, y);
        growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seed].imageLarge + ")";
        showElement("soil", x, y);
        hideElement("button", x, y);
    }
    var data = {
        slug: state.slug,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/harvest', data, callback);
}

var unlock = function(x, y) {
    if (state.resources.cash < GAME_CONFIG.plotPrice * Math.pow(GAME_CONFIG.plotMultiplier,state.unlockCount)) {
            showFlash("Not enough cash.");
            return;
    }
    var callback = function(newState) {
        state = newState;
        state["plot" + x + "_" + y].locked = 0;
        document.getElementById("cash").innerHTML = "CASH: $" + state.resources.cash;
        buyMsg = "Click any plot to unlock - $" + GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'],state.unlockCount);
        document.getElementById("buyPlot").innerHTML = buyMsg;
        hideElement("lock", x, y);
        showElement("soil", x, y);
        for (var s in GAME_CONFIG.seeds) {
            if (state.seedCounts[s] > 0) {
                showElement("sow" + s, x, y);
            }
        }
    }
    var data = {
        slug: state.slug,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/unlock', data, callback);
}

var buyPlot = function() {
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if (state['plot' + i + "_" + j].locked == 1) {
                unlock(i, j);
                return;
            }
        }
    }
}

var createSeedMenu = function() {
    for (var id in RECIPE_CONFIG) {
        if (RECIPE_CONFIG.hasOwnProperty(id) && document.getElementById("row" + id) == null) {
            var container = document.getElementById("seedCosts");
                var tr = document.createElement("TR");
                tr.id = "row" + id;
            container.appendChild(tr);

                var td1 = document.createElement("TD");
                    var img1 = document.createElement("IMG");
                    img1.src = GAME_CONFIG.seeds[id].imageSmall;
                td1.appendChild(img1);

                var td2 = document.createElement("TD");
                    var div2 = document.createElement("DIV");
                    div2.style.textAlign = 'left'
                    div2.innerHTML = GAME_CONFIG.seeds[id].name;
                td2.appendChild(div2);

                var td3 = document.createElement("TD");
                    var div3 = document.createElement("DIV");
                    div3.id = "sell" + id;
                    div3.classList.add('border');
                    div3.addEventListener('click',createListener(sell,id));
                td3.appendChild(div3);

                var td4 = document.createElement("TD");
                    var div4 = document.createElement("DIV");
                    div4.id = "owned" + id;
                td4.appendChild(div4);

                var td5 = document.createElement("TD");
                    var div5 = document.createElement("DIV");
                    div5.classList.add('border');
                    div5.id = 'buy' + id;
                    div5.addEventListener('click',createListener(buy,id));
                        var div5a = document.createElement("DIV");
                            div5a.id = "buy" + id + "_label";
                    div5.appendChild(div5a);
                td5.appendChild(div5);

                var td6 = document.createElement("TD");
                    var img6 = document.createElement("IMG");
                    img6.id = "resource" + id;
                    img6.style.height = '20px';
                td6.appendChild(img6);

                var td7 = document.createElement("TD");
                    var div7 = document.createElement("DIV");
                    div7.id = "resourceCost" + id;
                td7.appendChild(div7);

            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tr.appendChild(td4);
            tr.appendChild(td5);
            tr.appendChild(td6);
            tr.appendChild(td7);

            if (RECIPE_CONFIG[id].carrotsCost > 0) {
                document.getElementById("resource" + id).src = "/static/carrot_s.png";
                document.getElementById("resourceCost" + id).innerHTML = "x" + RECIPE_CONFIG[id].carrotsCost;
            }
            if (RECIPE_CONFIG[id].grassCost > 0) {
                document.getElementById("resource" + id).src = "/static/grass_s.png";
                document.getElementById("resourceCost" + id).innerHTML = "x" + RECIPE_CONFIG[id].grassCost;
            }
            if (RECIPE_CONFIG[id].fertilizerCost > 0) {
                document.getElementById("resource" + id).src = "/static/fertilizer_s.png";
                document.getElementById("resourceCost" + id).innerHTML = "x" + RECIPE_CONFIG[id].fertilizerCost;
            }
            document.getElementById("owned" + id).innerHTML = state.seedCounts[id];
            document.getElementById("buy" + id + "_label").innerHTML = "$" + RECIPE_CONFIG[id].cashCost;
            document.getElementById("sell" + id).innerHTML = "$" + GAME_CONFIG.seeds[id].sellCost;
        }
    }
}

var createListener = function(fn,arg) {
    return function(){fn(arg);};
}

var fetchRecipes = function() {
    var callback = function(game_state,knownRecipes) {
        RECIPE_CONFIG = knownRecipes;
        createSeedMenu();
        var newOrLoad = localStorage.getItem('newOrLoad');
        if (newOrLoad == "new") {
            gettingStarted();
        }
    }
    var data = {
        slug: state.slug,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/recipe', data, callback);
}

var tick = function() {
    if (state == null) {
        return;
    }
    var readyToHarvest = 0;
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if(state['plot' + i + "_" + j].seedType != 0) {
                var startTime = state['plot' + i + "_" + j].sowTime;
                var currentTime = new Date().getTime();
                var timePassed = Math.floor((currentTime - startTime) / 1000);
                var typeSeed = state['plot' + i + "_" + j].seedType;
                var harvestTime = GAME_CONFIG.seeds[typeSeed].harvestTimeSeconds;
                var countdown = harvestTime - timePassed;
                var percentTimeLeft = countdown / harvestTime;
                document.getElementById("filler" + i + "_" + j).style.width = percentTimeLeft * 100 + "%";
                var toHHMMSS = function(sec_num) {
                    var hours   = Math.floor(sec_num / 3600);
                    var minutes = Math.floor((sec_num % 3600) / 60);
                    var seconds = Math.floor(sec_num % 60);

                    if (hours   < 10) {hours   = "0" + hours;}
                    if (minutes < 10) {minutes = "0" + minutes;}
                    if (seconds < 10) {seconds = "0" + seconds;}

                    if (hours   <= 0) {return minutes + ':' + seconds;}
                    return hours + ':' + minutes + ':' + seconds;
                }
                var clockDisplay = toHHMMSS(countdown);
                document.getElementById("time" + i + "_" + j).innerHTML = clockDisplay;
                if (countdown <= 0) {
                    readyToHarvest += 1;
                    hideElement("progressBar", i, j);
                    showElement("button", i, j);
                }
            }
        }
    }
    document.getElementById("title").innerHTML = readyToHarvest + " plots ready - Garden Sim 2K17";
}

setInterval(tick, 100);
