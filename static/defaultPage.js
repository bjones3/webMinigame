var newOrLoad;

var frontPageAlert = function(payload) {
    var alertElement = document.getElementById('alertBox');
    alertElement.innerHTML = payload;
    window.setTimeout(function () {
        alertElement.innerHTML = '';
    }, 4000);
};

var server = new Server(frontPageAlert, console.log);

var startGame = function() {
    var slug = document.getElementById('gameNameInput').value;
    var gamePassword = document.getElementById('gamePasswordInput').value;
    if (slug == '') {
        alert('Enter a game name');
        return;
    }
    if (gamePassword == '') {
        alert('Enter a password');
        return;
    }
    localStorage.setItem('pwd_' + slug, gamePassword);
    localStorage.setItem('slug', slug);
    localStorage.setItem('newOrLoad', newOrLoad);
    var callback = function(pass) {
        window.location.href = '/game/#' + slug;
    }
    var data = {
        password: gamePassword,
        newOrLoad: newOrLoad
    };
    server.sendToServer('game-state/' + slug, data, callback);
}

var newOrLoadGame = function(newLoad) {
    document.getElementById("newGameButton").style.display = "none";
    document.getElementById("loadGameButton").style.display = "none";
    document.getElementById("leaderboardsButton").style.display = "none";
    document.getElementById("mainMenuButton").style.display = "block";
    document.getElementById("enterName").style.display = "block";
    document.getElementById("enterPassword").style.display = "block";
    document.getElementById("gameNameInput").style.display = "block";
    document.getElementById("gamePasswordInput").style.display = "block";
    document.getElementById("startButton").style.display = "block";
    newOrLoad = newLoad;
}

var mainMenu = function() {
    document.getElementById("newGameButton").style.display = "block";
    document.getElementById("loadGameButton").style.display = "block";
    document.getElementById("leaderboardsButton").style.display = "block";
    document.getElementById("mainMenuButton").style.display = "none";
    document.getElementById("enterName").style.display = "none";
    document.getElementById("enterPassword").style.display = "none";
    document.getElementById("gameNameInput").style.display = "none";
    document.getElementById("gamePasswordInput").style.display = "none";
    document.getElementById("startButton").style.display = "none";
    document.getElementById("leaderboardsTable").style.display = "none";
}

var leaderboards = function() {
    document.getElementById("newGameButton").style.display = "none";
    document.getElementById("loadGameButton").style.display = "none";
    document.getElementById("leaderboardsButton").style.display = "none";
    document.getElementById("mainMenuButton").style.display = "block";
    document.getElementById("leaderboardsTable").style.display = "block";
}

//startButton is clicked upon pressing 'enter' in gamePasswordInput
document.onreadystatechange = function() {
    if (document.readyState === 'complete') {
        document.getElementById("gamePasswordInput")
            .addEventListener("keyup", function(event) {
            event.preventDefault();
            if (event.keyCode == 13) {
                document.getElementById("startButton").click();
            }
        });
    }
}