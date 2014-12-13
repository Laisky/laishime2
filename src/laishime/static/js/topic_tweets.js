$(function(){
    get_last_update_topics();
    get_most_post_topics();
});


function get_last_update_topics(){
    var url = "get-last-update-topics";

    $.getJSON(url, function(data){
        if(data.status != 1) return;

        $("#last-update-topics").html(data.data);
    });
}


function get_most_post_topics(){
    var url = "get-most-post-topics";

    $.getJSON(url, function(data){
        if(data.status != 1) return;

        $("#most-post-topics").html(data.data);
    });
}
