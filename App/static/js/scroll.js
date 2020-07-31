
$(document).ready(function() {
    $(window).scroll(function() {
        var scroll_pos = $(document).scrollTop();
        $("#scroll_pos").val(scroll_pos);
    });
});

$(document).ready(function() {
    $("#body, html").animate({ scrollTop: $("#scroll_pos").val() }, { duration: 0 });
});

$(document).ready(function() {
    $(".map_instance").off("scroll");
    $(".map_container").off("scroll");
});