var errorOutput = document.getElementById('error');
var loadDbButton = document.getElementById('dbfile');

const chartContext = document.getElementById('progressChart');
const chart = new Chart(chartContext, { type: 'line' });

var worker = new Worker("node_modules/sql.js/dist/worker.sql-wasm.js");
worker.onerror = error;

worker.postMessage({ action: 'open' });

function error(e) {
	console.log(e);
	errorOutput.style.height = '2em';
	errorOutput.textContent = e.message;
}

function noerror() {
	errorOutput.style.height = '0';
}

function showProgress(sqlCommand, scoreFile) {
	worker.onmessage = function (event) {
		var results = event.data.results;
		if (!results) {
			error({ message: event.data.error });
			return;
		}
		noerror()

		var utc_timestamps = results[0].values.flat().map(x => x * 1000)

		chart.data = {
			labels: utc_timestamps,
			datasets: [{
				label: 'Cards',
				data: [...Array(utc_timestamps.length).keys()],
				fill: false,
				borderColor: 'rgb(75, 192, 192)',
				tension: 0.1
			}]
		}
		chart.options = {
			plugins: {
				title: {
					display: true,
					text: scoreFile
				}
			},
			scales: {
				x: {
					type: 'time',
					time: {
						unit: 'month'
					}
				},
				y: {
					beginAtZero: true
				}
			}
		}
		chart.update()
	}
	worker.postMessage({ action: 'exec', sql: sqlCommand });
}

function populateScoreFileButtons() {
	worker.onmessage = function (event) {
		var results = event.data.results;
		if (!results) {
			error({ message: event.data.error });
			return;
		}
		noerror()

		var scoreFileButtons = document.getElementById("scoreFileButtons");
		scoreFileButtons.innerHTML = '';

		for (let iScoreFile = 0; iScoreFile < results[0].values.length; iScoreFile++) {
			var scoreFileButton = document.createElement("button");
			var scoreFileId = results[0].values[iScoreFile][0]
			var scoreFileName = results[0].values[iScoreFile][1]
			scoreFileButton.textContent = scoreFileName;
			scoreFileButton.value = scoreFileId;
			scoreFileButton.style.fontSize = '16px';
			scoreFileButton.style.marginInline = '8px'

			scoreFileButton.onclick = function () {
				console.log("Showing progress for score file '" + this.textContent + "'")
				var sqlCommand = "SELECT firstreviewedtime FROM pleco_flash_scores_" + this.value + " ORDER BY firstreviewedtime ASC;"
				showProgress(sqlCommand, this.textContent)
			};
			scoreFileButtons.appendChild(scoreFileButton);
		}

	}
	worker.postMessage({ action: 'exec', sql: "SELECT id, name FROM pleco_flash_scorefiles;" });
}

loadDbButton.onchange = function () {
	var f = loadDbButton.files[0];
	var r = new FileReader();
	r.onload = function () {
		worker.onmessage = function () {
			populateScoreFileButtons();
		};
		try {
			worker.postMessage({ action: 'open', buffer: r.result }, [r.result]);
		}
		catch (exception) {
			worker.postMessage({ action: 'open', buffer: r.result });
		}
	}
	r.readAsArrayBuffer(f);
}
