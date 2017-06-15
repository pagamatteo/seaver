/*
Funzione che gestisce la risposta restituita dal server in seguito alla validazione del form relativo alla
creazione di un nuovo workspace.
*/
function manage_response(response) {
    if (JSON.stringify(response) === '{}') {                // form compilato correttamente
        console.log("Corretto");
        $('#myModal').modal('toggle');
        location.reload();
    }
    else {                                                  // form compilato in maniera errata
        // visualizzo i messaggi di errore
        var errors = response;
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

    $.ajax({
        url: form.attr("data-validate-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (response) {
          manage_response(response);
        }
      });
}
