var GAME_CONFIG = null;
var RECIPE_CONFIG = null;
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

// boo globals :(
var sowX = null;
var sowY = null;

var showSowMenu = function(i, j) {
    seedCount = 0;
    for (var seedId in state.seedCounts) {
        if (state.seedCounts.hasOwnProperty(seedId)) {
            seedCount += state.seedCounts[seedId];
        }
    }
    if (seedCount == 0) {
        showFlash("No seeds to plant!");
        return;
    }
    sowX = i;
    sowY = j;
    document.getElementById("sowMenuBg").style.display = "block";
    tutorialTransition(3);
};

var hideSowMenu = function() {
    document.getElementById("sowMenuBg").style.display = "none";
};

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

    if (!state || state.plots != newGameState.plots) {
        // Plots differ!  Figure out how:

        var newPlotCount = Object.keys(newGameState.plots).length;
        if (!state || Object.keys(state.plots).length != newPlotCount) {
            // Number of unlocked plots changed.  Update price
            var startingPlots = GAME_CONFIG['starting_field_width'] * GAME_CONFIG['starting_field_height'];
            var newPrice = GAME_CONFIG['plotPrice'] * Math.pow(GAME_CONFIG['plotMultiplier'], newPlotCount - startingPlots);
            buyMsg = "Click any plot to unlock for $" + newPrice;
            var element = document.getElementById("buyPlot");
            element.innerHTML = buyMsg;
            if (newGameState.resources['res0'] >= newPrice) {
                element.style.color = 'black';
            } else {
                element.style.color = '#ccc';
            }
        }


        for (var plotName in newGameState.plots) {
            if (newGameState.plots.hasOwnProperty(plotName)) {
                if (!state || state.plots[plotName] != newGameState.plots[plotName]) {
                    // A plot has been updated
                    var statePlot = newGameState.plots[plotName];
                    var plotElement = document.getElementById("plot" + plotName);
                    if (statePlot.seedType == 0) {
                        setPlotStatus(plotElement, 'sowable');
                    } else if (!plotElement.classList.contains('harvestable')) {
                        setPlotStatus(plotElement, 'growing');
                        var seed = GAME_CONFIG.seeds[statePlot.seedType];
                        var growingImgs = plotElement.getElementsByClassName('growingImg');
                        for (var i = 0; i < growingImgs.length; i++) {
                            growingImgs[i].style.backgroundImage = "url(" + seed.imageLarge + ")";
                        }
                    }
                    //TODO else: growing, harvestable, etc
                }
            }
        }

    }

    for (var resourceId in newGameState.resources) {
        if (newGameState.resources.hasOwnProperty(resourceId)) {
            if (!state || state.resources[resourceId] != newGameState.resources[resourceId]) {
                // A resource value has been updated
                var valueElement = document.getElementById("resvalue_" + resourceId);

                if (! valueElement) {
                    // User's never seen this resource before-- add a row
                    if (GAME_CONFIG.resources[resourceId]) {
                        var resourceTable = document.getElementById("resourceTable");
                            var row = document.createElement('tr');
                                var nameTd = document.createElement('td');
                                    var nameSpan = document.createElement('span');
                                    nameSpan.id = "resname_" + resourceId;
                                    nameSpan.innerHTML = GAME_CONFIG.resources[resourceId].name;
                                nameTd.appendChild(nameSpan);
                                    var nameColon = document.createTextNode(':');
                                nameTd.appendChild(nameColon);
                            row.appendChild(nameTd);
                                var valueTd = document.createElement('td');
                                    var valueElement = document.createElement('span');
                                    valueElement.id = "resvalue_" + resourceId;
                                valueTd.appendChild(valueElement);
                            row.appendChild(valueElement);
                        resourceTable.appendChild(row);
                    } else {
                        console.log("Unknown resource: " + resourceId);
                    }
                }

                if (valueElement) {
                    valueElement.innerHTML = newGameState.resources[resourceId];
                }
            }
        }
    }

    if (!state || state.seedCounts != newGameState.seedCounts) {
        for (var seedId in newGameState.seedCounts) {
            if (newGameState.seedCounts.hasOwnProperty(seedId)) {
                var oldCount = null;
                if (state && state.seedCounts[seedId]) {
                    oldCount = state.seedCounts[seedId];
                }
                var newCount = newGameState.seedCounts[seedId];
                if (oldCount != newCount) {
                    var seedCountElement = document.getElementById("owned_" + seedId);
                    if (seedCountElement) {
                        // check for existence because we may not know any recipes for this seed yet
                        seedCountElement.innerHTML = newGameState.seedCounts[seedId];
                    }

                    if (!oldCount && newCount) {
                        // did we go from 0->1 ?
                        var sowButton = document.getElementById('sowBtn_' + seedId);
                        if (!sowButton) {
                            // first time we've seen this seed type

                            var container = document.getElementById('sowButtonHolder');
                            var sowButton = document.createElement("button");
                            sowButton.id = 'sowBtn_' + seedId;
                            sowButton.classList.add('sowBtn');
                            sowButton.classList.add('tstage3');
                            sowButton.style.backgroundImage = "url(" + GAME_CONFIG.seeds[seedId].imageMedium + ")";
                            toolTip("Plant seed", sowButton);
                            sowButton.onclick = (function(seedId) {return function() { sow(seedId); }})(seedId);
                            container.appendChild(sowButton);
                        }
                        sowButton.style.display = 'block';
                    } else if (oldCount && !newCount) {
                    // did we go from 1->0 ?
                        var sowButton = document.getElementById('sowBtn_' + seedId);
                        sowButton.style.display = 'none';
                    }
                }
            }
        }
    }

    state = newGameState;
};

var toolTip = function(msg, element) {
    var span = document.createElement("span");
    span.classList.add("tooltiptext");
    var txt = document.createTextNode(msg);
    span.appendChild(txt);
    element.classList.add("tooltip");
    element.appendChild(span);
};

var tutorialTransition = function(toStage) {
    var from = toStage - 1;
    var container = document.getElementById("body");
    if (!from || container.classList.contains('tutorial_stage' + from)) {
        container.classList.remove('tutorial_stage' + from);
        container.classList.add('tutorial_stage' + toStage);
    }
};

var endTutorial = function() {
    var body = document.getElementById("body");
    body.classList.remove('tutorial_stage1', 'tutorial_stage2', 'tutorial_stage3');
    localStorage.setItem("newOrLoad", "load");
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

var fetchRecipes = function() {
    var callback = function(game_state, knownRecipes) {
        RECIPE_CONFIG = knownRecipes;
        createSeedMenu();
        var newOrLoad = localStorage.getItem('newOrLoad');
        if (newOrLoad == "new") {
            tutorialTransition(1);
        }
    };
    var data = {
        slug: state.slug,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/recipe', data, callback);
};

var loadGameState = function() {
    slug = localStorage.getItem('slug');
    var data = {
        password: localStorage.getItem('pwd_' + slug),
        newOrLoad: "load"
    };
    var gameStateLoaded = function(gameState) {
        updateGameState(gameState);
        fetchRecipes();
        setInterval(tick, 200);
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

document.onreadystatechange = function() {
    if (document.readyState === 'complete') {
        loadGameConfig();
    }
};

var buy = function(recipeID) {

    for (var resource in state.resources) {
        if (state.resources.hasOwnProperty(resource)) {
            if (state.resources[resource] < RECIPE_CONFIG[recipeID].cost[resource]) {
                showFlash("Not enough " + GAME_CONFIG.resources[resource].name + ".");
                return;
            }
        }
    }
    if (state.seedCounts[recipeID] >= GAME_CONFIG.max_seed_count) {
        showFlash("Can't buy any more " + GAME_CONFIG.seeds[recipeID].name + " seeds.");
        return;
    }
    var data = {
        slug: state.slug,
        recipe_id: recipeID,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    var buyCallback = function(response) {
        updateGameState(response);
        tutorialTransition(2);
    };
    server.sendToServer('/action/buy', data, buyCallback);
};

var sell = function(seed) {
    if (state.seedCounts[seed] <= 0) {
        showFlash("No " + GAME_CONFIG.seeds[seed].name + " seeds to sell.");
        return;
    }
    var data = {
        slug: state.slug,
        seed: seed,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/sell', data, updateGameState);
};

var sow = function(seed) {
    // boo globals :(
    var x = sowX;
    var y = sowY;
    if (state.seedCounts[seed] <= 0) {
        showFlash("No " + GAME_CONFIG.seeds[seed].name + " seeds to plant.");
        return;
    }
    if (state.plots[x + "_" + y].seedType != 0) {
        showFlash("A seed is already planted here.");
    }
    var data = {
        slug: state.slug,
        seed: seed,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    var sowCallback = function(response) {
        updateGameState(response);
        endTutorial();
    };
    server.sendToServer('/action/sow', data, sowCallback);
};

var harvest = function(x, y) {
    var callback = function(newState) {
        updateGameState(newState);
        fetchRecipes();
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
    var numPlots = Object.keys(state.plots).length
    var startingPlots = GAME_CONFIG['starting_field_width'] * GAME_CONFIG['starting_field_height']
    if (state.resources.res0 < GAME_CONFIG.plotPrice * Math.pow(GAME_CONFIG.plotMultiplier,numPlots - startingPlots)) {
        showFlash("Not enough cash.");
        return;
    }
    var data = {
        slug: state.slug,
        x: x,
        y: y,
        password: localStorage.getItem('pwd_' + state.slug)
    };
    server.sendToServer('/action/unlock', data, updateGameState);
};

var toggleSeedInfo = function(recipeId) {
    var hiding = document.getElementById('seedInfoRow_' + recipeId).style.display == 'table-row';

    for (var recipe_id in RECIPE_CONFIG) {
        document.getElementById('seedInfoButton' + recipeId).style.backgroundColor = 'white';
        document.getElementById('seedInfoButton' + recipeId).style.color = 'black';
        document.getElementById('seedInfoRow_' + recipeId).style.display = 'none';
    }
    if (hiding) return;

    document.getElementById('seedInfoButton' + recipeId).style.backgroundColor = 'blue';
    document.getElementById('seedInfoButton' + recipeId).style.color = 'white';
    document.getElementById('seedInfoRow_' + recipeId).style.display = 'table-row';
};

var createSeedInfo = function(container, recipeId) {
    var recipe = RECIPE_CONFIG[recipeId];
    var seedId = RECIPE_CONFIG[recipeId].seedId;
    var seed = GAME_CONFIG.seeds[seedId];


    var divCost = document.createElement("div");
        divCost.appendChild(document.createTextNode('Cost:'));

    container.appendChild(divCost);

    for (var resource in recipe.cost) {
        if (recipe.cost.hasOwnProperty(resource) && recipe.cost[resource] > 0) {
            var div = document.createElement("span");
                var img = document.createElement("IMG");
                img.src = GAME_CONFIG.resources[resource].imageUrl;
                img.classList.add('resourceIcon');

                var divCostNum = document.createElement("span");
                divCostNum.innerHTML = "x" + recipe.cost[resource];
                divCostNum.style.display = 'inline';
            div.appendChild(img);
            div.appendChild(divCostNum);

            divCost.appendChild(div);
        }
    }

    var divYield = document.createElement("div");
        divYield.appendChild(document.createTextNode('Yield:'));
    container.appendChild(divYield);

    if (seed.seed > 0) {
        var div = document.createElement("span");
        var img = document.createElement("IMG");
        img.src = seed.imageSmall;
        img.classList.add('seedIcon');

        var divYieldMult = document.createElement("span");
        divYieldMult.innerHTML = "x" + seed.seed;
        divYieldMult.style.display = 'inline';
        div.appendChild(img);
        div.appendChild(divYieldMult);

        divYield.appendChild(div);
    }
    for (var yieldType in seed.yield) {
        if (seed.yield[yieldType] > 0) {
            var div = document.createElement("span");
                var img = document.createElement("IMG");
                img.src = GAME_CONFIG.resources[yieldType].imageUrl;
                img.classList.add('resourceIcon');

                var divYieldMult = document.createElement("DIV");
                divYieldMult.innerHTML = "x" + seed.yield[yieldType];
                divYieldMult.style.display = 'inline';
            div.appendChild(img);
            div.appendChild(divYieldMult);

            divYield.appendChild(div);
        }
    }

    var divHarvestTime = document.createElement("DIV");
        divHarvestTime.innerHTML = "Harvest Time: " + toHHMMSS(seed.harvestTimeSeconds);
    container.appendChild(divHarvestTime);

    var divBonus = document.createElement("DIV");
        divBonus.innerHTML = "Bonus seed chance: " + Math.round(100 * seed.probability) + "%";
    container.appendChild(divBonus);
};

var createSeedMenu = function() {
    for (var recipeId in RECIPE_CONFIG) {
        if (RECIPE_CONFIG.hasOwnProperty(recipeId) && document.getElementById("row" + recipeId) == null) {
            var seedId = RECIPE_CONFIG[recipeId].seedId;
            var container = document.getElementById("seedCosts");

            var tr = document.createElement("TR");
                tr.id = "row" + recipeId;
            container.appendChild(tr);

                var td0 = document.createElement("TD");
                    var div0 = document.createElement("DIV");
                    div0.id = 'seedInfoButton' + recipeId;
                    div0.classList.add('seedInfoButton');
                    div0.innerHTML = "i";
                    div0.addEventListener('click',createListener(toggleSeedInfo,recipeId));
                td0.appendChild(div0);

                var td1 = document.createElement("TD");
                    var img1 = document.createElement("IMG");
                    img1.src = GAME_CONFIG.seeds[seedId].imageSmall;
                td1.appendChild(img1);

                var td2 = document.createElement("TD");
                    var div2 = document.createElement("DIV");
                    div2.style.textAlign = 'left';
                    div2.innerHTML = GAME_CONFIG.seeds[seedId].name;
                td2.appendChild(div2);

                var td3 = document.createElement("TD");
                    var div3 = document.createElement("DIV");
                    div3.id = "sell" + recipeId;
                    div3.innerHTML = "$" + GAME_CONFIG.seeds[seedId].sellCost;
                    div3.classList.add('border');
                    div3.addEventListener('click',createListener(sell,seedId));
                td3.appendChild(div3);

                var td4 = document.createElement("TD");
                    var div4 = document.getElementById("owned_" + seedId);
                    if (!div4) {
                        div4 = document.createElement("DIV");
                        div4.id = "owned_" + seedId;
                    }
                    div4.innerHTML = state.seedCounts[seedId];
                td4.appendChild(div4);

                var td5 = document.createElement("TD");
                    var div5 = document.createElement("DIV");
                    div5.classList.add('border');
                    div5.id = 'buy' + recipeId;
                    div5.innerHTML = "$" + RECIPE_CONFIG[recipeId].cost['res0'];
                    if (GAME_CONFIG.firstRecipe == recipeId) {
                        div5.classList.add('tstage1');
                        toolTip("Buy a " + GAME_CONFIG.seeds[seedId].name + " seed", div5);
                    }
                    div5.addEventListener('click',createListener(buy,recipeId));
                        var div5a = document.createElement("DIV");
                            div5a.id = "buy" + recipeId + "_label";
                    div5.appendChild(div5a);
                td5.appendChild(div5);

            tr.appendChild(td0);
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tr.appendChild(td4);
            tr.appendChild(td5);

            var seedInfo = document.createElement("TR");
            seedInfo.id = 'seedInfoRow_' + recipeId;
            seedInfo.style.display = 'none';
            container.appendChild(seedInfo);

            var seedInfoTd = document.createElement("TD");
            seedInfoTd.colSpan = 6;
            createSeedInfo(seedInfoTd, recipeId);
            seedInfo.appendChild(seedInfoTd);
        }
    }
};

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

var createListener = function(fn, arg) {
    return function() { fn(arg); };
};

var tick = function() {
    if (state == null) {
        return;
    }
    var readyToHarvest = 0;
    for (var plotId in state.plots) {
        if (state.plots.hasOwnProperty(plotId)) {
            if(state.plots[plotId].seedType != 0) {
                var startTime = state.plots[plotId].sowTime;
                var currentTime = new Date().getTime();
                var timePassed = Math.floor((currentTime - startTime) / 1000);
                var typeSeed = state.plots[plotId].seedType;
                var harvestTime = GAME_CONFIG.seeds[typeSeed].harvestTimeSeconds;
                var countdown = harvestTime - timePassed;
                var percentTimeLeft = countdown / harvestTime;
                document.getElementById("filler" + plotId).style.width = percentTimeLeft * 100 + "%";
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
                document.getElementById("time" + plotId).innerHTML = clockDisplay;
                if (countdown <= 0) {
                    readyToHarvest += 1;
                    setPlotStatus(document.getElementById('plot' + plotId), 'harvestable');
                }
            }
        }
    };
    document.getElementById("title").innerHTML = readyToHarvest + " plots ready - Garden Sim 2K17";
};
