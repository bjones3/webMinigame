var startGame = function() {
    slug = document.getElementById('gameNameInput').value
    gamePassword = document.getElementById('gamePasswordInput').value
    localStorage.setItem('pwd_' + slug, gamePassword)
    localStorage.setItem('slug', slug)
    if (slug == '') {
        alert('Enter a game name');
        return;
    }
    callback = function(pass) {
        window.location.href = '/game/#' + slug;
    };
    var data = {
        password: gamePassword,
    };
    sendToServer('game-state/' + slug, data, callback);
};

var toggleIDDisplay = function(idName) {
    if (document.getElementById(idName).style.display == "none") {
        document.getElementById(idName).style.display = "block";
    }
    if (document.getElementById(idName).style.display == "block") {
        document.getElementById(idName).style.display = "none";
    }
};


var newOrLoadGame = function() {
    document.getElementById("newGameButton").style.display = "none"
    document.getElementById("loadGameButton").style.display = "none"
    document.getElementById("enterName").style.display = "block"
    document.getElementById("enterPassword").style.display = "block"
    document.getElementById("gameNameInput").style.display = "block"
    document.getElementById("gamePasswordInput").style.display = "block"
    document.getElementById("startButton").style.display = "block"
    document.getElementById("mainMenuButton").style.display = "block"
};
var mainMenu = function() {
    document.getElementById("newGameButton").style.display = "block"
    document.getElementById("loadGameButton").style.display = "block"
    document.getElementById("enterName").style.display = "none"
    document.getElementById("enterPassword").style.display = "none"
    document.getElementById("gameNameInput").style.display = "none"
    document.getElementById("gamePasswordInput").style.display = "none"
    document.getElementById("startButton").style.display = "none"
    document.getElementById("mainMenuButton").style.display = "none"
};