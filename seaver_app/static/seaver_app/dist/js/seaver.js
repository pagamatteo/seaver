/*
Funzione che gestisce la risposta restituita dal server in seguito alla validazione del form relativo alla
creazione di un nuovo workspace.
*/
function manage_create_workspace_response(response) {
    if (response['errors'] == false) {                // form compilato correttamente

        // dato che il form è compilato correttamente visualizzo il nuovo workspace creato
        var results = response['results'];

        // nascondo la finestra contenente il for
        $('#myModal').modal('toggle');

        // copio dal sorgente HTML un div workspace_box_col e un div workspace_box
        workspace_box_col = $(".workspace_box_col:first").clone();
        workspace_box = $(".workspace_box:first").clone(true);

        // rimuovo dal div workspace_box_col tutti i div workspace_box in esso contenuti
        workspace_box_col.find(".workspace_box").remove();

        // popolo con i dati ricevuti dal server il div workspace_box recuperato
        workspace_box.find(".box-title").text(results['workspace_name']);
        workspace_box.find("p").remove();

        // appendo al div workspace_box_col quello workspace_box appena modificato
        workspace_box_col.append( workspace_box );

        // prependo il div workspace_box_col appena aggiornato al div workspace_box_row
        $(".workspace_box_row").prepend( workspace_box_col );

        console.log(workspace_box_col);

    }
    else {                                                  // form compilato in maniera errata
        // visualizzo i messaggi di errore
        var errors = response['results'];
        console.log(errors);
        var error_string = "";
        for (error_field in errors) {
            var clean_error_field = error_field.match(/(.*)_(.*)/)[2];
            clean_error_field = clean_error_field.charAt(0).toUpperCase() + clean_error_field.slice(1);
            error_messages = errors[error_field];
            error_string += '<div class="alert alert-danger">' + '<strong>';
            for (var i = 0; i < error_messages.length; i++) {
                error_message = error_messages[i];
                error_string += '<p>' + clean_error_field + ': ' + error_message + '</p>';
            }
            error_string += '</strong></div>';
        }
        var errors_div = $("#create_workspace_form_errors");
        errors_div.html(error_string);
    }
}

/*
Funzione che recupera i campi del form relativo alla creazione di un nuovo workspace e contatta il server
per creare il nuovo workspace.
*/
function create_workspace() {
    var form = $("#create_workspace_form");
    console.log("Create workspace...");

    $.ajax({
        url: form.attr("data-validate-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (response) {
          manage_create_workspace_response(response);
        }
      });
}


function manage_delete_workspace_response(workspace_box_to_delete){
    $('#delete_workspace_modal').modal('toggle');
    workspace_box_to_delete.closest(".workspace_box_col").remove();
}

/*
Funzione che cancella un workspace.
*/
function delete_workspace(event, url_structure) {
    var workspace_box_to_delete = $(event.target);
    var worksapce_name = workspace_box_to_delete.closest( ".box-header " ).find( "h3" ).html();
    var url = url_structure.replace("workspace_name", worksapce_name);
    console.log("Name: " + worksapce_name);

    $.ajax({
        url: url,
        success: function (response) {
            if (response["errors"] == false)
                //location.reload();
                manage_delete_workspace_response(workspace_box_to_delete);
        }
      });
}


function ask_delete_workspace_confirm(event, url) {
    $('#delete_workspace_modal').modal('toggle');
    $('#confirm_delete_workspace').on("click", function(){ delete_workspace(event, url); });
}




function manage_delete_file_response(file_sidebar_menu){
    $('#delete_file_modal').modal('toggle');
    //workspace_box_to_delete.closest(".workspace_box_col").remove();
}

/*
Funzione che cancella un file.
*/
function delete_file(event, url_structure) {
    var file_sidebar_menu = $(event.target).parent();
    var file_name = file_sidebar_menu.text();
    //var worksapce_name = workspace_box_to_delete.closest( ".box-header " ).find( "h3" ).html();
    var url = url_structure.replace("file_name", file_name);
    console.log("url: " + url);

    $.ajax({
        url: url,
        success: function (response) {
            if (response["errors"] == false)
                //location.reload();
                manage_delete_file_response(file_sidebar_menu);
        }
      });
}


function ask_delete_file_confirm(event, url) {
    $('#delete_file_modal').modal('toggle');
    $('#confirm_delete_file').on("click", function(){ delete_file(event, url); });
}

// var chartData = [ {
//     "country": "USA",
//     "visits": 4252
//   }, {
//     "country": "China",
//     "visits": 1882
//   }, {
//     "country": "Japan",
//     "visits": 1809
//   }, {
//     "country": "Germany",
//     "visits": 1322
//   }, {
//     "country": "UK",
//     "visits": 1122
//   }, {
//     "country": "France",
//     "visits": 1114
//   }, {
//     "country": "India",
//     "visits": 984
//   }, {
//     "country": "Spain",
//     "visits": 711
//   }, {
//     "country": "Netherlands",
//     "visits": 665
//   }, {
//     "country": "Russia",
//     "visits": 580
//   }, {
//     "country": "South Korea",
//     "visits": 443
//   }, {
//     "country": "Canada",
//     "visits": 441
//   }, {
//     "country": "Brazil",
//     "visits": 395
//   }, {
//     "country": "Italy",
//     "visits": 386
//   }, {
//     "country": "Australia",
//     "visits": 384
//   }, {
//     "country": "Taiwan",
//     "visits": 338
//   }, {
//     "country": "Poland",
//     "visits": 328
// } ];
// AmCharts.makeChart( "chartdiv", {
//   "type": "serial",
//   "dataProvider": chartData,
//   "categoryField": "country",
//   "graphs": [ {
//     "valueField": "visits",
//     "type": "column"
//   } ]
// } );

var chart_data = [
						{
							"column-1": 8,
							"column-2": 5,
							"index": "category 1"
						},
						{
							"column-1": 6,
							"column-2": 7,
							"index": "category 2"
						},
						{
							"column-1": 2,
							"column-2": 3,
							"index": "category 3"
						},
						{
							"column-1": 1,
							"column-2": 3,
							"index": "category 4"
						},
						{
							"column-1": 2,
							"column-2": 1,
							"index": "category 5"
						},
						{
							"column-1": 3,
							"column-2": 2,
							"index": "category 6"
						},
						{
							"column-1": 6,
							"column-2": 8,
							"index": "category 7"
						}
					];

var chart = AmCharts.makeChart("chartdiv",
				{
					"type": "serial",
					"categoryField": "index",
					"startDuration": 1,
					"categoryAxis": {
						"gridPosition": "start"
					},
					"chartCursor": {
						"enabled": true
					},
					"chartScrollbar": {
						"enabled": true
					},
					"trendLines": [],
					"graphs": [
						{
							"balloonText": "[[title]] of [[category]]:[[value]]",
							"bullet": "round",
							"id": "AmGraph-1",
							"title": "graph 1",
							"valueField": "column-1"
						},
						{
							"balloonText": "[[title]] of [[category]]:[[value]]",
							"bullet": "square",
							"id": "AmGraph-2",
							"title": "graph 2",
							"valueField": "column-2"
						}
					],
					"guides": [],
					"valueAxes": [
						{
							"id": "ValueAxis-1",
							"title": "Axis title"
						}
					],
					"allLabels": [],
					"balloon": {},
					"legend": {
						"enabled": true,
						"useGraphSettings": true
					},
					"titles": [
						{
							"id": "Title-1",
							"size": 15,
							"text": "Chart Title"
						}
					],
					"dataProvider": chart_data
				}
			);