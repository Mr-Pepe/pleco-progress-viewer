var errorElm = document.getElementById('error');
var dbFileElm = document.getElementById('dbfile');
const chartCtx = document.getElementById('progressChart');

// Start the worker in which sql.js will run
var worker = new Worker("node_modules/sql.js/dist/worker.sql-wasm.js");
worker.onerror = error;

// Open a database
worker.postMessage({ action: 'open' });

function error(e) {
	console.log(e);
	errorElm.style.height = '2em';
	errorElm.textContent = e.message;
}

function noerror() {
	errorElm.style.height = '0';
}

const chart = new Chart(chartCtx, {type:'line'});

// Run a command in the database
function execute(commands) {
	worker.onmessage = function (event) {
		var results = event.data.results;
		if (!results) {
			error({message: event.data.error});
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
	worker.postMessage({ action: 'exec', sql: commands });
}

// Load a db from a file
dbFileElm.onchange = function () {
	var f = dbFileElm.files[0];
	var r = new FileReader();
	r.onload = function () {
		worker.onmessage = function () {
			execute("SELECT firstreviewedtime FROM pleco_flash_scores_3 ORDER BY firstreviewedtime ASC;")
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
