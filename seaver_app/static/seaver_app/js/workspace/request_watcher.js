/**
 * Created by ovi on 09/07/17.
 */

requests_watcher = new RequestWatcher();

var request_workspace_id = requests_watcher.add_listener('workspace', function () {
    // carico i file in Vue
    v_files.files = workspace.files;
    menu_files.files = workspace.files;
    menu_punctual_events.events = workspace.punctuals;
    menu_interval_events.events = workspace.intervals;

    // rimuovo il listener
    requests_watcher.remove_listener('workspace', request_workspace_id);
});

var file_listener = function () {
    //alert("files loading compleated");
    requests_watcher.progressBar.css("width", 100 + '%').attr("aria-valuenow", 100 + '%').text(100 + '%');
    if ($('#loading_file_modal').is(':visible')) {
        $("#loading_file_modal").modal('toggle');
    }
    //$('#finish_file_loading').prop('disabled', false);

    // aggiungo i file al chart manager
    workspace.files.forEach(function (f) {
        chart_manager.add_file(f);
    });

    // eseguo il refresh del grafico
    chart_manager.refresh();

    // rimuovo il listener
    requests_watcher.remove_listener('files', request_files_id);
};

// creo l'osservatore per la terminazione del download dei file
var request_files_id = requests_watcher.add_listener('files', file_listener);

var request_annotation_id = requests_watcher.add_listener('ann', function () {
    // ottengo i dati del workspace
    get_workspace(workspace_url);

    // rimuovo il listener
    requests_watcher.remove_listener('ann', request_annotation_id);
});

var request_event_id = requests_watcher.add_listener('event', function () {
    workspace.punctuals.forEach(function (e) {
        chart_manager.add_event(e);
    });
    workspace.intervals.forEach(function (e) {
        chart_manager.add_event(e);
    });

    // rimuovo il listener
    requests_watcher.remove_listener('event', request_event_id);
});