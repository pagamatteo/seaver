/**
 * Created by ovi on 09/07/17.
 */

requests_watcher = new RequestWatcher();

requests_watcher.add_listener('workspace', function () {
    // carico i file in Vue
    v_files.files = workspace.files;
    menu_files.files = workspace.files;
});

// creo l'osservatore per la terminazione del download dei file
requests_watcher.add_listener('files', function () {
    alert("files loading compleated");

    // aggiungo i file al chart manager
    workspace.files.forEach(function (f) {
        chart_manager.add_file(f);
    });

    // eseguo il refresh del grafico
    chart_manager.refresh();
});

requests_watcher.add_listener('ann', function () {
    // ottengo i dati del workspace
    get_workspace(workspace_url);
});

requests_watcher.add_listener('event', function () {
    workspace.punctuals.forEach(function (e) {
        chart_manager.add_event(e);
    });
    workspace.intervals.forEach(function (e) {
        chart_manager.add_event(e);
    });
});