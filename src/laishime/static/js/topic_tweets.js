$(function() {
    get_last_update_topics();
    get_most_post_topics();
});


function bind_topics() {
    $("ul.topics").children().click(function() {
        var topic = arguments[0].target.innerText;
        get_tweets_by_topic(topic);
    });
}


function get_tweets_by_topic(topic) {
    var url = "get-tweets-by-topic";
    var data = {
        "topic": topic
    };

    $.getJSON(url, data, function(data) {
        if (data.status != 1) return;

        $("#tweets").html(data.data);
    });
}


function get_last_update_topics() {
    var url = "get-last-update-topics";

    $.getJSON(url, function(data) {
        if (data.status != 1) return;

        $("#last-update-topics").html(data.data);
        bind_topics();
    });
}


function get_most_post_topics() {
    var url = "get-most-post-topics";

    $.getJSON(url, function(data) {
        if (data.status != 1) return;

        $("#most-post-topics").html(data.data);
        bind_topics();
    });
}