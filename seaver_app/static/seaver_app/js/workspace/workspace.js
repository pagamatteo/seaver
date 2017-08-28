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