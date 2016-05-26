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

function bind_getrank_clicks() {
    $("#getrank").bind("click", function() {
        //alert("I'm here, are you?");
        var ajax = $.getJSON("/_get_rank", {url: $("#url").val()});
        ajax.done(function(data) {
            result = [];

            $.each(data.ss, function(index, value) {
                result.push("\n\nPS: " + this.number);
                result.push("=====")

                $.each(this.overall_rank, function(index, value) {
                    if(this.gap) {
                        gap = this.gap
                    } else {
                        gap = "0.0"
                    }
                    crew_str = []

                    crew_str.push(
                        this.position,
                        " ",
                        this.driver,
                        " - ",
                        this.co_driver,
                        " [",
                        this.car,
                        " (",
                        this.class,
                        ")] (+",
                        gap,
                        ")");

                    result.push(crew_str.join(""))
                });
            });

            // console.log(result)

            var elem = $("#result");
            elem.text(result.join("\n"));
            autosize.update(elem);
        });
    }); // end click function
}
