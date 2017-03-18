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

var setPlotStatus = function(plot, status) {
    plot.classList.remove('sowable', 'growing', 'harvestable', 'locked');
    plot.classList.add(status);
};

var updateGameState = function(newGameState) {
    /*  Update the global game state object, and update any UI elements needed

    This method will take a new game state (or a part of a new game state) and
    update the global `state` object.  When parts differ between the two, it
    will update the proper UI components to reflect the new change.  This
    should allow calling functions to blindly update parts of the game state
    without having to have knowledge of all the UI components that rely on it.
    By looking at the old verson of the game state, the hope is to only update
    parts of the display that need it rather than redrawing the entire thing
    from scratch every time.

    */

    state = newGameState;

    for (var plotName in newGameState.plots) {
        if (newGameState.plots.hasOwnProperty(plotName)) {
            if (!state.plots || state.plots[plotName] != newGameState.plots[plotName]) {
                // A plot has been updated
                var statePlot = newGameState.plots[plotName];
                var plotElement = document.getElementById("plot" + plotname);
                if (statePlot.seedType == 0) {
                    setPlotStatus(plotElement, 'sowable');
                }
                //TODO else: growing, harvestable, etc
            }
        }
    }

    for (var resourceId in newGameState.resources) {
        if (newGameState.resources.hasOwnProperty(resourceId)) {
            if (!state.resources || state.resources[resourceId] != newGameState.resources[resourceId]) {
                // A resource value has been updated
                document.getElementById(resource).innerHTML = resource + ': ' + state.resources[resource];
            }
        }
    }
    document.getElementById("cash").innerHTML = "cash: $" + state.resources.cash;
    var numPlots = Object.keys(state.plots).length
    var startingPlots = GAME_CONFIG['starting_field_width'] * GAME_CONFIG['starting_field_height']
    buyMsg = "Click any plot to unlock - $" + GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'],numPlots - startingPlots);
    document.getElementById("buyPlot").innerHTML = buyMsg;

};

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
    var sowBtn = document.getElementsByClassName("sowBtn");
    var tooltip = document.getElementsByClassName("tooltiptext");
    for(var i = 0; i < tooltip.length; i++) {
        tooltip[i].style.display = "none";
    }
    createSowButton('a')
    toolTip("Plant seed", "sowBtna0_0");
    buyBtn.style.animationIterationCount = '0';
    for (var i = 0; i < sowBtn.length; i++) {
        sowBtn[i].style.animationName = 'borderChange';
        sowBtn[i].style.animationDuration = '2s';
        sowBtn[i].style.animationIterationCount = 'infinite';
        sowBtn[i].addEventListener('click', afterSow);
    }
}
var afterSow = function() {
    var sowBtn = document.getElementsByClassName("sowBtn");
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
        updateGameState(gameState);
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

var plotStatus = function(status, x, y) {
    document.getElementById('plot' + x + '_' + y).classList.remove('sowable', 'growing', 'harvestable', 'locked');
    document.getElementById('plot' + x + '_' + y).classList.add(status);
}


var reset = function() {
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if (state.plots.hasOwnProperty(i + "_" + j)) {
                if (state.plots[i + "_" + j].seedType != 0) {
                    plotStatus('growing', i, j)
                    var growingImage = showElement("growing", i, j);
                    growingImage.style.backgroundImage = "url(" + GAME_CONFIG.seeds[state.plots[i + "_" + j].seedType].imageLarge + ")";

                } else {
                    plotStatus('sowable', i, j)
                    for (var seed in GAME_CONFIG.seeds) {
                        if (state.seedCounts[seed] > 0) {
                            hideElement("sowBtn" + seed, i, j);
                        }
                    }
                }
            } else {
                plotStatus('locked', i, j)
            }
        }
    }
    for (var resource in state.resources) {
            if (state.resources.hasOwnProperty(resource)) {
                document.getElementById(resource).innerHTML = resource + ': ' + state.resources[resource];
            }
        }
        document.getElementById("cash").innerHTML = "cash: $" + state.resources.cash;
    var numPlots = Object.keys(state.plots).length
    var startingPlots = GAME_CONFIG['starting_field_width'] * GAME_CONFIG['starting_field_height']
    buyMsg = "Click any plot to unlock - $" + GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'],numPlots - startingPlots);
    document.getElementById("buyPlot").innerHTML = buyMsg;
}

document.onreadystatechange = function() {
    if (document.readyState === 'complete') {
        loadGameConfig();
    }
};

var buy = function(recipeID) {

    for (var resource in state.resources) {
        if (state.resources.hasOwnProperty(resource)) {
            if (state.resources[resource] < RECIPE_CONFIG[recipeID][resource + 'Cost']) {
                showFlash("Not enough " + resource + ".");
                return;
            }
        }
    }
    if (state.seedCounts[recipeID] == GAME_CONFIG.max_seed_count) {
        showFlash("Can't buy any more " + GAME_CONFIG.seeds[recipeID].name + " seeds.");
        return;
    }
    var callback = function(newState) {
        state = newState;
        createSowButton(recipeID);
        document.getElementById("owned" + recipeID).innerHTML = state.seedCounts[recipeID];
        for (var resource in state.resources) {
            if (state.resources.hasOwnProperty(resource)) {
                document.getElementById(resource).innerHTML = resource + ': ' + state.resources[resource];
            }
        }
        document.getElementById("cash").innerHTML = "cash: $" + state.resources.cash;
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if (state.plots.hasOwnProperty(i + "_" + j)) {
                    if(state.plots[i + "_" + j].seedType == 0) {
                        showElement("sowBtn" + recipeID, i, j);
                    }
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
        document.getElementById("cash").innerHTML = "cash: $" + state.resources.cash;
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if(state.seedCounts[seed] == 0) {
                    hideElement("sowBtn" + seed, i, j);
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
    if (state.plots[x + "_" + y].seedType != 0) {
        showFlash("A seed is already planted here.");
    }
    var callback = function(newState) {
        state = newState;
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];
        plotStatus('growing', x, y)
        if (state.seedCounts[seed] == 0) {
            for (var i = 0; i < GAME_CONFIG.field_width; i++) {
                for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                    hideElement("sowBtn" + seed, i, j);
                }
            }
        }
        tick();
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
        var seed = state.plots[x + "_" + y].seedType;
        state = newState;
        fetchRecipes();
        document.getElementById("owned" + seed).innerHTML = state.seedCounts[seed];

        for (var resource in state.resources) {
            if (state.resources.hasOwnProperty(resource)) {
                document.getElementById(resource).innerHTML = resource + ': ' + state.resources[resource];
            }
        }
        document.getElementById("cash").innerHTML = "cash: $" + state.resources.cash;

        for (var s in GAME_CONFIG.seeds) {
            if (state.seedCounts[s] > 0) {
                showElement("sowBtn" + s, x, y);
            }
        }
        for (var i = 0; i < GAME_CONFIG.field_width; i++) {
            for (var j = 0; j < GAME_CONFIG.field_height; j++) {
                if (state.plots.hasOwnProperty(i + "_" + j)) {
                    if(state.plots[i + "_" + j].seedType == 0 && state.seedCounts[seed] > 0) {
                        showElement("sowBtn" + seed, i , j);
                    }
                }
            }
        }
        plotStatus('sowable');
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
    var numPlots = Object.keys(state.plots).length
    var startingPlots = GAME_CONFIG['starting_field_width'] * GAME_CONFIG['starting_field_height']
    if (state.resources.cash < GAME_CONFIG.plotPrice * Math.pow(GAME_CONFIG.plotMultiplier,numPlots - startingPlots)) {
        showFlash("Not enough cash.");
        return;
    }
    var callback = function(newState) {
        state = newState;
        document.getElementById("cash").innerHTML = "cash: $" + state.resources.cash;
        buyMsg = "Click any plot to unlock - $" + GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'],numPlots - startingPlots);
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
            if (state.plots.hasOwnProperty(i + "_" + j) == False) {
                unlock(i, j);
                return;
            }
        }
    }
}

var createSowButton = function(id) {
    for (var i = 0; i < GAME_CONFIG.field_width; i++) {
        for (var j = 0; j < GAME_CONFIG.field_height; j++) {
            if (document.getElementById("sowBtn" + id + i + '_' + j) == null) {
                var container = document.getElementById('plot' + i + '_' + j)
                    var p = document.createElement("P");
                    p.id = "sowBtn" + id + i + '_' + j;
                    p.classList.add('sowable', 'sowBtn');
                    p.style.backgroundImage = "url(" + GAME_CONFIG.seeds[id].imageMedium + ")";
                    p.addEventListener('click',createListener2(sow, i, j, id));
                container.appendChild(p);
            }
        }
    }
}

var createSeedInfo = function(id) {
    for (var recipe_id in RECIPE_CONFIG) {
        document.getElementById('seedInfoButton' + recipe_id).style.backgroundColor = 'white';
        document.getElementById('seedInfoButton' + recipe_id).style.color = 'black';
    }
    document.getElementById('seedInfoButton' + id).style.backgroundColor = 'blue';
    document.getElementById('seedInfoButton' + id).style.color = 'white';

    var seedInfoMenu = document.getElementById('seedInfoContent');
    while (seedInfoMenu.firstChild) {
        seedInfoMenu.removeChild(seedInfoMenu.firstChild);
    }
    var div = document.createElement("DIV");
        var img = document.createElement("IMG");
            img.src = GAME_CONFIG.seeds[id].imageSmall;
            img.style.display = 'inline';
        var divName = document.createElement("DIV");
            divName.innerHTML = GAME_CONFIG.seeds[id].name;
            divName.style.display = 'inline';
    div.appendChild(img);
    div.appendChild(divName);
    var divCost = document.createElement("DIV");
        divCost.innerHTML = 'Cost:';

    seedInfoMenu.appendChild(div);
    seedInfoMenu.appendChild(divCost);

    for (var cost in RECIPE_CONFIG[id]) {
        if (RECIPE_CONFIG[id].hasOwnProperty(cost) && RECIPE_CONFIG[id][cost] > 0) {
            var div = document.createElement("DIV");
                var img = document.createElement("IMG");
                if (cost == 'cashCost') {img.src = "/static/cash.png";}
                if (cost == 'carrotsCost') {img.src = "/static/carrot_s.png";}
                if (cost == 'grassCost') {img.src = "/static/grass_s.png";}
                if (cost == 'fertilizerCost') {img.src = "/static/fertilizer_s.png";}
                img.style.height = '20px';
                img.style.display = 'inline';

                var divCost = document.createElement("DIV");
                divCost.innerHTML = "x" + RECIPE_CONFIG[id][cost];
                divCost.style.display = 'inline';
            div.appendChild(img);
            div.appendChild(divCost);

            seedInfoMenu.appendChild(div);
        }
    }

    var divYield = document.createElement("DIV");
        divYield.innerHTML = "Yield:";
    seedInfoMenu.appendChild(divYield);

    for (var yieldType in GAME_CONFIG.seeds[id].yield) {
        if (GAME_CONFIG.seeds[id].yield[yieldType] > 0) {
            var div = document.createElement("DIV");
                var img = document.createElement("IMG");
                if (yieldType == 'seed') {img.src = GAME_CONFIG.seeds[id].imageSmall}
                if (yieldType == 'cash') {img.src = "/static/cash.png";}
                if (yieldType == 'carrots') {img.src = "/static/carrot_s.png";}
                if (yieldType == 'grass') {img.src = "/static/grass_s.png";}
                if (yieldType == 'fertilizer') {img.src = "/static/fertilizer_s.png";}
                img.style.height = '20px';
                img.style.display = 'inline';

                var divYieldMult = document.createElement("DIV");
                divYieldMult.innerHTML = "x" + GAME_CONFIG.seeds[id].yield[yieldType];
                divYieldMult.style.display = 'inline';
            div.appendChild(img);
            div.appendChild(divYieldMult);

            seedInfoMenu.appendChild(div);
        }
    }

    var divHarvestTime = document.createElement("DIV");
        divHarvestTime.innerHTML = "Harvest Time: " + toHHMMSS(GAME_CONFIG.seeds[id].harvestTimeSeconds);
    seedInfoMenu.appendChild(divHarvestTime);

    var divBonus = document.createElement("DIV");
        divBonus.innerHTML = "Bonus seed chance: " + GAME_CONFIG.seeds[id].probability;
    seedInfoMenu.appendChild(divBonus);
}

var createSeedMenu = function() {
    for (var id in RECIPE_CONFIG) {
        if (RECIPE_CONFIG.hasOwnProperty(id) && document.getElementById("row" + id) == null) {
            var container = document.getElementById("seedCosts");
                var tr = document.createElement("TR");
                tr.id = "row" + id;
            container.appendChild(tr);

                var td0 = document.createElement("TD");
                    var div0 = document.createElement("DIV");
                    div0.id = 'seedInfoButton' + id;
                    div0.classList.add('seedInfoButton');
                    div0.innerHTML = "i";
                    div0.addEventListener('click',createListener(createSeedInfo,id));
                td0.appendChild(div0);

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
                    div3.innerHTML = "$" + GAME_CONFIG.seeds[id].sellCost;
                    div3.classList.add('border');
                    div3.addEventListener('click',createListener(sell,id));
                td3.appendChild(div3);

                var td4 = document.createElement("TD");
                    var div4 = document.createElement("DIV");
                    div4.id = "owned" + id;
                    div4.innerHTML = state.seedCounts[id];
                td4.appendChild(div4);

                var td5 = document.createElement("TD");
                    var div5 = document.createElement("DIV");
                    div5.classList.add('border');
                    div5.id = 'buy' + id;
                    div5.innerHTML = "$" + RECIPE_CONFIG[id].cashCost;
                    div5.addEventListener('click',createListener(buy,id));
                        var div5a = document.createElement("DIV");
                            div5a.id = "buy" + id + "_label";
                    div5.appendChild(div5a);
                td5.appendChild(div5);

            tr.appendChild(td0);
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tr.appendChild(td4);
            tr.appendChild(td5);
        }
    }
}

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

var createListener = function(fn,arg) {
    return function(){fn(arg);};
}
var createListener2 = function(fn,arg,arg2,arg3) {
    return function(){fn(arg,arg2,arg3);};
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
            if (state.plots.hasOwnProperty(i + "_" + j)) {
                if(state.plots[i + "_" + j].seedType != 0) {
                    var startTime = state.plots[i + "_" + j].sowTime;
                    var currentTime = new Date().getTime();
                    var timePassed = Math.floor((currentTime - startTime) / 1000);
                    var typeSeed = state.plots[i + "_" + j].seedType;
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
                        plotStatus('harvestable', i, j)
                    }
                }
            }
        }
    }
    document.getElementById("title").innerHTML = readyToHarvest + " plots ready - Garden Sim 2K17";
}

setInterval(tick, 100);
