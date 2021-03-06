/**
 * Created by ovi on 09/07/17.
 */

function get_punctual_event(url) {
    requests_watcher.add('event');
    $.get(url).done(function (data) {
        // ottengo l'annotazione corrispondente
        data.annotation = annotations_by_url[data.annotation];

        var index = _.sortedIndexBy(workspace.punctuals, data, 'start');
        workspace.punctuals.splice(index, 0, data);
    }).always(function () {
        requests_watcher.remove('event');
    })
}

function get_interval_event(url) {
    requests_watcher.add('event');
    $.get(url).done(function (data) {
        // ottengo l'annotazione corrispondente
        data.annotation = annotations_by_url[data.annotation];

        var index = _.sortedIndexBy(workspace.intervals, data, 'start');
        workspace.intervals.splice(index, 0, data);
    }).always(function () {
        requests_watcher.remove('event');
    })
}

// ottine i dati del campo
function get_field_data(field) {
    requests_watcher.add('files');
    $.get(field.field_data).done(function (data) {
        field['data'] = data.field_data;
    }).fail(function (errors) {
        console.log(errors);
    }).always(function () {
        requests_watcher.remove('files');
    });
}


// aggiunge il campo al file
function add_field_to_file(field, f) {
    // aggiungo al data un campo che serve per il menù laterale
    field.name_on_change = false;

    // put in alphabetic order
    var field_index = _.sortedIndexBy(f.fields, field, function (e) {
        var name = e.name;
        // i nomi delle analisi vanno dopo
        if (!(e.computed))
            name = 0 + name;
        return name.toLowerCase();
    });
    get_field_data(field);
    f.fields.splice(field_index, 0, field);
}

// ottiene il campo
function get_field(field_url, f) {
    requests_watcher.add('files');
    $.get(field_url).done(function (data) {
        add_field_to_file(data, f);
    }).fail(function (errors) {
        console.log(errors);
    }).always(function () {
        requests_watcher.remove('files');
    })
}

function get_file(file_url) {
    requests_watcher.add('files');
    $.get(file_url).done(function (data) {

        //console.log(requests_watcher);

        data.fields = [];
        // put in alphabetic order
        var file_index = _.sortedIndexBy(workspace.files, data, function (e) {
            return e.name.toLowerCase();
        });
        workspace.files.splice(file_index, 0, data);
        // carica il nome del file nella barra laterale
        data.field_names.forEach(function (field_url) {
            get_field(field_url, data)
        });
    }).fail(function (errors) {
        console.log(errors)
    }).always(function () {
        requests_watcher.remove('files');
    });
}

function get_workspace(workspace_url) {
    requests_watcher.add('workspace');
    $.get(workspace_url).done(function (data) {
        workspace = data;

        // aggiungo i campi degli eventi
        workspace['punctuals'] = [];
        workspace['intervals'] = [];

        // scarico gli annotation events
        data['punctual_annotations'].forEach(function (url) {
            get_punctual_event(url);
        });
        data['interval_annotations'].forEach(function (url) {
            get_interval_event(url);
        });

        var fs = data.files;
        if (fs.length > 0) {
            if (!$('#loading_file_modal').is(':visible')) {
                $("#loading_file_modal").modal('toggle');
            }
        }
        workspace.files = [];
        fs.forEach(function (f_url) {
            get_file(f_url);
        });
    }).fail(function (error) {
        console.log(error);
    }).always(function () {
        requests_watcher.remove('workspace');
    });
}


function get_puctual_annotations(url) {
    requests_watcher.add('ann');
    $.get(url).done(function (data) {
        // se la lista non è finita
        if (data['next'] !== null)
            get_puctual_annotations(data['next']);

        var punctuals = annotation_events.punctual;
        for (var i = 0; i < data['count']; i += 1) {
            var result = data['results'][i];

            // salvo l'annotazione per la ricerca by url
            annotations_by_url[result.url] = result;

            var index = _.sortedIndexBy(punctuals, result, function (e) {
                return e.name.toLowerCase();
            });
            punctuals.splice(index, 0, result)
        }
    }).always(function () {
        requests_watcher.remove('ann');
    })
}


function get_interval_annotations(url) {
    requests_watcher.add('ann');
    $.get(url).done(function (data) {
        // se la lista non è finita
        if (data['next'] !== null)
            get_interval_annotations(data['next']);

        var intervals = annotation_events.interval;
        for (var i = 0; i < data['count']; i += 1) {
            var result = data['results'][i];

            // salvo l'annotazione per la ricerca by url
            annotations_by_url[result.url] = result;

            var index = _.sortedIndexBy(intervals, result, function (e) {
                return e.name.toLowerCase();
            });
            intervals.splice(index, 0, result)
        }
    }).always(function () {
        requests_watcher.remove('ann');
    })
}

function get_annotations(punctual_url, interval_url) {
    get_puctual_annotations(punctual_url);
    get_interval_annotations(interval_url);
}

var workspace;
var workspace_url;
var annotation_events = {'punctual': [], 'interval': []};
var annotations_by_url = {};

