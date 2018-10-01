function update() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      fillTable(this.responseText);
    }
  };
  xhttp.open("POST", "update", true);
  xhttp.send();
}

var scoreboard = document.getElementById('scoreboard');
var header = scoreboard.firstChild;
function fillTable(json) {
  console.log("Refreshing table")
  var data = JSON.parse(json);
  data.sort((a, b) => {
    return b[1]-a[1];
  });
  while(header.nextSibling) {
      scoreboard.removeChild(header.nextSibling);
  }
  for(element of data) {
    var row = document.createElement("tr");
    var name = document.createElement("td");
    var score = document.createElement("td");
    name.innerHTML = element[0];
    score.innerHTML = element[1];
    row.appendChild(name);
    row.appendChild(score);
    scoreboard.appendChild(row);
  }
}

function submit_password(password) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      update();
      console.log("Got back response:", this.responseText)
    }
  };
  xhttp.open("POST", "score", true);
  var data = new FormData();
  data.append('level_password', password);
  xhttp.send(data);
}

update();
window.setInterval(update, 10000);
