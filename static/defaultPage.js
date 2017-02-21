var newOrLoad;

var startGame = function() {
    var slug = document.getElementById('gameNameInput').value
    var gamePassword = document.getElementById('gamePasswordInput').value
    if (slug == '') {
        alert('Enter a game name');
        return;
    }
    if (gamePassword == '') {
        alert('Enter a password');
        return;
    }
    localStorage.setItem('pwd_' + slug, gamePassword)
    localStorage.setItem('slug', slug)
    var callback = function(pass) {
        window.location.href = '/game/#' + slug;
    };
    var data = {
        password: gamePassword,
        newOrLoad: newOrLoad
    };
    sendToServer('game-state/' + slug, data, callback);
};

var newGame = function() {
    document.getElementById("newGameButton").style.display = "none"
    document.getElementById("loadGameButton").style.display = "none"
    document.getElementById("leaderboardsButton").style.display = "none"
    document.getElementById("enterName").style.display = "block"
    document.getElementById("enterPassword").style.display = "block"
    document.getElementById("gameNameInput").style.display = "block"
    document.getElementById("gamePasswordInput").style.display = "block"
    document.getElementById("startButton").style.display = "block"
    document.getElementById("mainMenuButton").style.display = "block"
    newOrLoad = "new"
};

var loadGame = function() {
    document.getElementById("newGameButton").style.display = "none"
    document.getElementById("loadGameButton").style.display = "none"
    document.getElementById("leaderboardsButton").style.display = "none"
    document.getElementById("enterName").style.display = "block"
    document.getElementById("enterPassword").style.display = "block"
    document.getElementById("gameNameInput").style.display = "block"
    document.getElementById("gamePasswordInput").style.display = "block"
    document.getElementById("startButton").style.display = "block"
    document.getElementById("mainMenuButton").style.display = "block"
    newOrLoad = "load"
};

var mainMenu = function() {
    document.getElementById("newGameButton").style.display = "block"
    document.getElementById("loadGameButton").style.display = "block"
    document.getElementById("leaderboardsButton").style.display = "block"
    document.getElementById("enterName").style.display = "none"
    document.getElementById("enterPassword").style.display = "none"
    document.getElementById("gameNameInput").style.display = "none"
    document.getElementById("gamePasswordInput").style.display = "none"
    document.getElementById("startButton").style.display = "none"
    document.getElementById("mainMenuButton").style.display = "none"
    document.getElementById("leaderboardsTable").style.display = "none"
};

var leaderboards = function() {
    document.getElementById("newGameButton").style.display = "none"
    document.getElementById("loadGameButton").style.display = "none"
    document.getElementById("leaderboardsButton").style.display = "none"
    document.getElementById("mainMenuButton").style.display = "block"
    document.getElementById("leaderboardsTable").style.display = "block"
};

