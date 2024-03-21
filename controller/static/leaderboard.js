let socket = new WebSocket("ws://localhost:8000/live-updates/leaderboard");

socket.onopen = function(e) {
    console.log("[open] Connection established");
};

socket.onmessage = function(event) {
    let json = JSON.parse(event.data.toString())
    showLeaderboard(json)
};

socket.onclose = function(event) {
    if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
        console.log('[close] Connection closed not cleanly');
    }
};

function showLeaderboard(leaderboard) {
    console.log("[showLeaderboard] Message from server ", leaderboard);
    buildTable(leaderboard["user_list"])
    let lastModifiedTag = document.getElementById("lastModifiedDate")
    let lastModifiedDate = new Date(leaderboard["current_time_ms"])
    lastModifiedTag.textContent = "Last modified: " + lastModifiedDate.toLocaleString();
}

function buildTable(data){
    let table = document.getElementById('leaderboardTable');
    table.innerHTML = ""
    for(let i =0; i<data.length; i++){
        let row = `<tr><td>${data[i]["rank"]}</td><td>${data[i]["score"]}</td><td>${data[i]["nickname"]}</td></tr>`
        table.innerHTML += row;
    }
}

socket.onerror = function(error) {
    console.log("[error] ERROR occurred")
};
