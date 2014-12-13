$(function(){
});


function get_last_update_topics(){
    var url = "get-last-update-topics";

    $.getJSON(url, function(data){
        if(data.status != 1) return;

        var articles = "";
        for(var i in data.data){
            var topic = data.data.i.topic;
            var timestamp = data.data.i.timestamp;
        }
    });
}
