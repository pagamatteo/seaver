function manage_delete_file_response(file_sidebar_menu){
    $('#delete_file_modal').modal('toggle');
    //workspace_box_to_delete.closest(".workspace_box_col").remove();
}

/*
Funzione che cancella un file.
*/
function delete_file() {
    var index = v_files.index_to_delete;
    var f = workspace.files[index];

    // chiudo la finestra di eliminazione del file
    $('#delete_file_modal').modal('toggle');
    $("#data_processing_modal").modal('toggle');

    $.ajax({
        url: f.url,
        method: 'DELETE'
    }).done(function (data) {
        //location.reload();
        // imposto nessun file selezionato nel menu di destra
        menu_files.file_selected_index = -1;

        // elimino il file dal grafico
        chart_manager.delete_file(f);
        chart_manager.refresh();
        // elimino il file dal workspace (e quindi dai menù)
        workspace.files.splice(index, 1);
        $("#data_processing_modal").modal('toggle');
    }).fail(function (data) {
        console.log(data);
    })
}
// function delete_file(event, url_structure) {
//     var file_sidebar_menu = $(event.target).parent();
//     var file_name = file_sidebar_menu.text();
//     console.log(file_name);
//     //var worksapce_name = workspace_box_to_delete.closest( ".box-header " ).find( "h3" ).html();
//     console.log(url_structure);
//     var url = url_structure.replace("file_name", file_name);
//     console.log("url: " + url);
//
//     $.ajax({
//         url: url,
//         success: function (response) {
//             if (response["errors"] == false)
//                 //location.reload();
//                 manage_delete_file_response(file_sidebar_menu);
//         }
//       });
// }



/*function ask_delete_file_confirm(event, url) {
    $('#delete_file_modal').modal('toggle');
    $('#confirm_delete_file').on("click", function(){ delete_file(event, url); });
}*/


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

// var chart_data = [
// 						{
// 							"column-1": 8,
// 							"column-2": 5,
// 							"index": "category 1"
// 						},
// 						{
// 							"column-1": 6,
// 							"column-2": 7,
// 							"index": "category 2"
// 						},
// 						{
// 							"column-1": 2,
// 							"column-2": 3,
// 							"index": "category 3"
// 						},
// 						{
// 							"column-1": 1,
// 							"column-2": 3,
// 							"index": "category 4"
// 						},
// 						{
// 							"column-1": 2,
// 							"column-2": 1,
// 							"index": "category 5"
// 						},
// 						{
// 							"column-1": 3,
// 							"column-2": 2,
// 							"index": "category 6"
// 						},
// 						{
// 							"column-1": 6,
// 							"column-2": 8,
// 							"index": "category 7"
// 						}
// 					];
var chart_data = [];

var chart = AmCharts.makeChart("chartdiv",
    {
        "type": "serial",
        "categoryField": "index",
        "mouseWheelScrollEnabled": true,
        "mouseWheelZoomEnabled": true,
        "startDuration": 1,
        "categoryAxis": {
            "startOnAxis": true,
            "axisColor": "#DADADA",
            "gridAlpha": 0.07,
            "title": "Index",
            "guides": []
        },
        "chartCursor": {
            "enabled": true,
            "selectWithoutZooming": true
        },
        "chartScrollbar": {
            "enabled": true
        },
        "trendLines": [],
        "graphs": [],
        "guides": [],
        "valueAxes": [
            {
                "id": "ValueAxis-1",
                "title": "Value"
            }
        ],
        "allLabels": [],
        "balloon": {},
        "legend": {
            "enabled": false,
            "position": "left",
            "useGraphSettings": true
        },
        "titles": [
            {
                "id": "Title-1",
                "size": 15,
                "text": "Data plot"
            }
        ],
        "dataProvider": chart_data
    }
);