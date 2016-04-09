function fill_event_list() {
    console.log("Start filling event list");

    var ajax = $.getJSON("/_get_event_list");
    ajax.done(function(data) {

        $("#event-list").empty();
        $.each(data.list, function(index) {
            //console.log("index: " + index);
            //console.log("link: " + this.link);
            //console.log("event: " + this.event);
            $("#event-list").append("<li class='col-sm-6'><a href='"+this.link+"'>"+this.event+"</a></li>");
        });

    });

    console.log("End filling event list");
}
