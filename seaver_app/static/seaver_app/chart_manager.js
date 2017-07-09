/**
 * Created by ovi on 09/07/17.
 */

function ChartManager(chart) {
    this.fields = {};
    this.data = [];
    // come avviene la visualizzazione di un field
    this.graphs = {};
    // annotazioni
    this.guides = [];
    this.chart = null;
    // 0 significa tutti
    this.points_per_field = 0;
    this.__get_index_increment = function (field_name) {
        if (this.points_per_field === 0)
        // tutti i punti
            return 1;

        //  restituisce di quanto deve crescere l'indice della serie
        var index_increment = Math.floor(this.fields[field_name].data.length / this.points_per_field);
        if (index_increment < 1)
            index_increment = 1;

        return index_increment;
    };
    this.__create_graph = function (field_name) {
        if (field_name in this.graphs)
            return;

        this.graphs[field_name] = {
            "balloonText": "[[title]] of [[category]]:[[value]]",
            "bullet": "round",
            "id": field_name,
            "title": field_name,
            "valueField": field_name,
            "hidden": false
        };
    };
    this.__delete_graph = function (field_name) {
        if (field_name in this.graphs) {
            delete this.graphs[field_name];
        }
    };
    this.__create_field_data = function (field_name) {
        var field = this.fields[field_name];

        var index_increment = this.__get_index_increment(field_name);

        for (i = 0; i < field.data.length; i += index_increment) {
            var point_index = i * field.stretching + field.offset;
            var point_data = {'index': point_index};
            //  in che posizione di data inserire il nuovo punto
            var data_index = _.sortedIndexBy(this.data, point_data, 'index');
            if ((data_index < this.data.length) && (this.data[data_index].index === point_index)) {
                // se l'elemento esiste già
                this.data[data_index][field_name] = field.data[i];
            }
            else {
                point_data[field_name] = field.data[i];
                this.data.splice(data_index, 0, point_data);
            }
        }
    };
    __delete_field_data = function (field_name) {
        var field = this.fields[field_name];

        var index_increment = this.__get_index_increment(field_name);

        for (var i = 0; i < field.data.length; i += index_increment) {
            var point_index = i * field.stretching + field.offset;
            var point_data = {'index': point_index};
            // in che posizione di data inserire il nuovo punto
            var data_index = _.sortedIndexBy(this.data, point_data, 'index');

            delete this.data[data_index][field_name];

            // se l'elemento contiene solo index lo elimino dall'array
            if (Object.keys(this.data[data_index]).length === 1) {
                this.data.splice(data_index, 1);
                i -= 1;
            }

        }
    };
    this.__update_field_data = function (field_name) {
        this.__delete_field_data(field_name);
        this.__create_field_data(field_name);
    };
    this.__add_annotation_index = function (index) {
        // funzione che blocca l'indice per le annotazioni
        var data_index = _.sortedIndexBy(this.data, {'index': index}, 'index');
        // controllo che l'indice non esista già in data
        if ((data_index < this.data.length) && (this.data[data_index].index === index)) {
            // controllo che annotation esista
            if ('annotations' in this.data[data_index]) {
                // aggiungo +1 alle annotazioni bloccanti
                this.data[data_index]['annotations'] += 1;
            } else {
                // solo un'annotazione sta bloccando il punto
                this.data[data_index]['annotations'] = 1;
            }
        } else {
            // ora un'annotazione sta bloccando il punto
            this.data.splice(data_index, 0, {
                'index': index,
                'annotations': 1
            })
        }
    };
    this.set_chart = function (chart) {
        this.chart = chart;
        this.guides = chart.categoryAxis.guides;
    };
    this.set_points_per_field = function (points_per_field) {
        for (field_name in this.fields) {
            if (this.fields.hasOwnProperty(field_name)) {
                this.__delete_field_data(field_name);
            }
        }

        this.points_per_field = points_per_field;

        for (field_name in this.fields) {
            if (this.fields.hasOwnProperty(field_name)) {
                this.__delete_field_data(field_name);
            }
        }
    };
    this.show_graph = function (field_name) {
        this.chart.showGraph(this.graphs[field_name]);
    };
    this.hide_graph = function (field_name) {
        this.chart.hideGraph(this.graphs[field_name]);
    };
    this.add_field = function (field_name, data, offset, stretching) {
        if (field_name in this.fields) {
            this.__delete_field_data(field_name);
        }

        this.fields[field_name] = {};
        this.fields[field_name].data = data;
        this.fields[field_name].offset = offset;
        this.fields[field_name].stretching = stretching;

        this.__create_field_data(field_name);

        this.__create_graph(field_name)
    };
    this.add_field_if_not_exists = function (field_name, data, offset, stretching) {
        if (field_name in this.fields)
            return;

        this.add_field(field_name, data, offset, stretching);
    };
    this.delete_field = function (field_name) {
        if (!(field_name in this.fields))
            return;

        this.__delete_field_data(field_name);
        delete this.fields[field_name];

        this.__delete_graph(field_name);
    };
    this.set_offset = function (field_name, offset) {
        if (this.fields[field_name].offset !== offset) {
            this.__delete_field_data(field_name);
            this.fields[field_name].offset = offset;
            this.__create_field_data(field_name);
        }
    };
    this.set_stretching = function (field_name, stretching) {
        if (this.fields[field_name].stretching !== stretching) {
            this.__delete_field_data(field_name);
            this.fields[field_name].stretching = stretching;
            this.__create_field_data(field_name);
        }
    };
    this.refresh = function () {
        var graphs = [];
        for (key in this.graphs) {
            if (this.graphs.hasOwnProperty(key)) {
                graphs.push(this.graphs[key]);
            }
        }
        this.chart.graphs = graphs;
        this.chart.dataProvider = this.data;
        this.chart.validateData();
    };
    this.rename_field = function (previous_name, current_name) {
        if (previous_name !== current_name) {
            var previous_field = this.fields[previous_name];
            this.delete_field(previous_field);
            this.add_field(current_name, previous_field.data, previous_field.offset,
                previous_field.stretching);
        }
    };
    //  file method
    this.get_field_name = function (f, field) {
        return f.name + "_" + field.name;
    };
    this.add_file = function (f) {
        for (var i = 0; i < f.fields.length; i += 1) {
            var field = f.fields[i];
            var chart_field_name = this.get_field_name(f, field);
            this.add_field_if_not_exists(chart_field_name, field.data, f.offset, f.stretching);

            this.graphs[chart_field_name].hidden = !((f.active) && (field.active));
        }
    };
    this.delete_file = function (f) {
        for (var i = 0; i < f.fields.length; i += 1) {
            var field = f.fields[i];
            var chart_field_name = this.get_field_name(f, field);
            this.delete_field(chart_field_name);
        }
    };
    this.show_hide_file = function (f) {
        for (var i = 0; i < f.fields.length; i += 1) {
            var field = f.fields[i];
            var chart_field_name = this.get_field_name(f, field);
            if (f.active && field.active)
                this.show_graph(chart_field_name);
            else
                this.hide_graph(chart_field_name)
        }
    };
    this.add_event = function (e) {
        var guide = new AmCharts.Guide();
        guide.lineColor = "#CC0000";
        guide.lineAlpha = 1;
        guide.fillAlpha = 0.2;
        guide.fillColor = "#CC0000";
        guide.dashLength = 2;
        guide.inside = true;
        guide.labelRotation = 90;

        guide.id = e.url;
        guide.category = e.start;

        // aggiungo che un'annotazione sta bloccando l'indice corrispondente
        this.__add_annotation_index(e.start);

        if ('stop' in e) {
            guide.toCategory = e.stop;
            // aggiungo che un'annotazione sta bloccando l'indice corrispondente
            this.__add_annotation_index(e.stop);
        }

        guide.label = e.annotation.name;

        this.chart.categoryAxis.addGuide(guide);
    };
    this.remove_event = function (e) {
        var index = _.findIndex(this.guides, function (o) {
            return o.id === e.url;
        });

        // ho trovato il guide corrispondente e lo rimuovo
        if (index !== -1) {
            this.chart.categoryAxis.removeGuide(this.guides[index]);
        }
    };

    this.set_chart(chart);
}