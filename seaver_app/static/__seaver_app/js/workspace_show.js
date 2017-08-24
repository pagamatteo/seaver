var v_workspaces;
var v_workspaces_box;

function manage_delete_workspace_response(index) {
    $('#delete_workspace_modal').modal('toggle');
    v_workspaces_box.delete_workspace(index);
    v_workspaces.delete_workspace(index);
}

/*
Funzione che cancella un workspace.
*/
function delete_workspace(workspace_name, index, url_structure) {
    var url = url_structure.replace("workspace_name", workspace_name);

    $.ajax({
        url: url,
        success: function (response) {
            if (response["errors"] == false)
                manage_delete_workspace_response(index);
        }
    });
}

/*
Funzione che gestisce la risposta restituita dal server in seguito alla validazione del form relativo alla
creazione di un nuovo workspace.
*/
function manage_create_workspace_response(response) {
    if (response['errors'] == false) {                // form compilato correttamente

        var workspace_data = response['results'];

        v_workspaces_box.add_workspace(workspace_data);
        v_workspaces.add_workspace(workspace_data);

        // nascondo la finestra contenente il for
        $('#myModal').modal('toggle');

    }
    else {                                                  // form compilato in maniera errata
        // visualizzo i messaggi di errore
        var errors = response['results'];
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
            manage_create_workspace_response(response);
        }
    });
}


$("[data-widget='collapse']").click(function () {
    //Find the box parent........
    var box = $(this).parents(".box").first();
    //Find the body and the footer
    var bf = box.find(".box-body, .box-footer");
    if (!$(this).children().hasClass("fa-plus")) {
        $(this).children(".fa-minus").removeClass("fa-minus").addClass("fa-plus");
        bf.slideUp();
    } else {
        //Convert plus into minus
        $(this).children(".fa-plus").removeClass("fa-plus").addClass("fa-minus");
        bf.slideDown();
    }
});