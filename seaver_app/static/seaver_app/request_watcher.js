/**
 * Created by ovi on 09/07/17.
 */

// osservatore di richieste
function RequestWatcher() {
    // gruppi di richieste
    this.groups = {};
    // listeners di eventy
    this.listeners = {
        // si attivano per ogni gruppo che termina il download
        'any': []
    };
    this.add = function (group_name) {
        // aggiungo il tipo di gruppo se non esiste
        if (!(group_name in this.groups)) {
            this.groups[group_name] = {
                requests: 0,
                responses: 0
            };
        }
        this.groups[group_name].requests += 1;
    };
    this.remove = function (group_name) {
        var group = this.groups[group_name];
        group.responses += 1;

        // ho finito di scaricare i dati
        if (group.responses >= group.requests) {
            // attivo tutti i listener su any
            this.listeners['any'].forEach(function (l) {
                l();
            });
            if (group_name in this.listeners) {
                // attivo tutti i listeners
                var listeners = this.listeners[group_name];
                listeners.forEach(function (l) {
                    l();
                })
            }
        }
    };
    this.add_listener = function (group_name, listener) {
        if (!(group_name in this.listeners)) {
            this.listeners[group_name] = []
        }

        this.listeners[group_name].push(listener);
    };
    this.remove_listener = function (group_name, listener) {
        _.pull(this.listeners[group_name], listener);
    }
}
