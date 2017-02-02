var GAME_CONFIG = {
    startingCash: 10,
    seeds: {
        a: {
            name: "Alfalfa Sprouts",
            imageSmall: "static/alfalfa.jpg",
            imageMedium: "static/alfalfa.jpg",
            imageLarge: "static/alfalfa.jpg",
            buyCost: 3,
            sellCost: 1,
            harvestYield: 4,
            harvestTimeSeconds: 40
        },
        b: {
            name: "Broccoli",
            imageSmall: "static/broccoli.jpg",
            imageMedium: "static/broccoli.jpg",
            imageLarge: "static/broccoli.jpg",
            buyCost: 6,
            sellCost: 1,
            harvestYield: 9,
            harvestTimeSeconds: 120
        },
        c: {
            name: "Cabbage",
            imageSmall: "static/cabbage.jpg",
            imageMedium: "static/cabbage.jpg",
            imageLarge: "static/cabbage.jpg",
            buyCost: 12,
            sellCost: 2,
            harvestYield: 10,
            harvestTimeSeconds: 300
        }
    }
};

var state = {
    cash: GAME_CONFIG.startingCash,
    a: 0,
    b: 0,
    c: 0
};
for (var i = 0; i <= 2; i++) {
    for (var j = 0; j <= 2; j++) {
        state[("plot" + i + j)] = {seedType: 0, sowTime: 0};
    }
};

var reset = function() {
    state.cash = GAME_CONFIG.startingCash;
    state.a = 0;
    state.b = 0;
    state.c = 0;

    for (var i = 0; i <= 2; i++) {
        for (var j = 0; j <= 2; j++) {
            state[("plot" + i + j)].seedType = 0;
            state[("plot" + i + j)].sowTime = 0;
        };
    };

    classDisplay = function(className, displayType) {
        var x = document.getElementsByClassName(className);
        for (var i = 0; i < x.length; i++) {
            x[i].style.display = (displayType);
        };
    };
    classDisplay("sowPlantButton", "block");
    classDisplay("invisBlockContainer", "none");
    classDisplay("soil", "block");
    classDisplay("progressBar", "none");
    classDisplay("button", "none");

    document.getElementById("cash").innerHTML = "CASH: $" + state.cash;
    document.getElementById("owneda").innerHTML = 0;
    document.getElementById("ownedb").innerHTML = 0;
    document.getElementById("ownedc").innerHTML = 0;
    document.getElementById("buyA").innerHTML = "$" + GAME_CONFIG.seeds.a.buyCost;
    document.getElementById("buyB").innerHTML = "$" + GAME_CONFIG.seeds.b.buyCost;
    document.getElementById("buyC").innerHTML = "$" + GAME_CONFIG.seeds.c.buyCost;
    document.getElementById("sellA").innerHTML = "$" + GAME_CONFIG.seeds.a.sellCost;
    document.getElementById("sellB").innerHTML = "$" + GAME_CONFIG.seeds.b.sellCost;
    document.getElementById("sellC").innerHTML = "$" + GAME_CONFIG.seeds.c.sellCost;
};

document.onreadystatechange = function() {
  if (document.readyState === 'complete') {
    reset();
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
    seed = 0;
};

var tick = function() {
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
                if (countdown == 0) {
                    document.getElementById("progressBar" + i + j).style.display = "none";
                    document.getElementById("button" + i + j).style.display = "block";
                }

            };
        };
    };
};

setInterval(tick, 100);