function fill_event_list() {
    console.log("Start filling event list");

    var ajax = $.getJSON("/_get_event_list");
    ajax.done(function(data) {

        $("#event-list").empty();
        $.each(data.list, function(index) {
            //console.log("index: " + index);
            //console.log("link: " + this.link);
            //console.log("event: " + this.event);
            $("#event-list").append("<li class='col-sm-6'><a class='event-link' data-url='"+this.link+"' href='#'>"+this.event+"</a></li>");
        });

        bind_anchor_clicks()

    });

    console.log("End filling event list");
}

function bind_anchor_clicks() {
    $(".event-link").bind("click", function() {
        $("#url").val($(this).data("url"));
    }); // end click Function
}
