$(document).ready(function() {

    $("#about-btn").click( function(event) {
        alert("You clicked the button using JQuery!");
        msgstr = $("#msg").html()
        msgstr = msgstr + "ooo"
        $("#msg").html(msgstr)
    });

    $('ul.navbar-nav > li > a[href="' + document.location.pathname + '"]').parent().addClass('active');
});

