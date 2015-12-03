function display_ppl(ppl_list, loc_id) {

        for (var person_num=0; person_num < ppl_list.length; person_num++) {

            name = ppl_list[person_num]['name']
            age = ppl_list[person_num]['age']
            sign = ppl_list[person_num]['sign']
            bio = ppl_list[person_num]['bio']
            birthday = ppl_list[person_num]['birthday']
            img_list = ppl_list[person_num]['img']
            large_img_list = ppl_list[person_num]['large_img_list']
            last_active_at = ppl_list[person_num]['last_active_at']




            $("#" + loc_id).append('<div id="'+person_num+'" class="well"></div>')
            $("#"+person_num).append('<h1>'+name+' ('+age+')</h1>')
            $("#"+person_num).append('<h3>'+sign+'</h3>')
            $("#"+person_num).append('<p>Last active: '+last_active_at+'</p>')
            $("#"+person_num).append('<p>'+bio+'</p>')
            $("#"+person_num).append('<p>DOB: '+birthday+'</p>')


            for (var i =0; i < img_list.length; i++) {

                img = '<a target="_blank" href="'+large_img_list[i]+'"><img class="tinder_img" src="'+img_list[i]+'"/></a>'

                $("#"+person_num).append(img)
            }

        }

}


function get_info() {

    // Get search string
    search_name = $("#search_name").val();
    // console.log(search_name)
    loc_id = 'results_img'
    $("#"+loc_id).empty()

    // Switch the magnifying glass image to the loading spinner
    $('#search_load').show();
    $('#search_icon').hide();

    // POST request to /get_hw
    url = "/get_info";
    $.post(url,{search_name:search_name}).done(function(response) {
        
        $('#search_load').hide();
        $('#search_icon').show();

        signed_in = response['signed_in'];

        if (signed_in){
            ppl_list = response['ppl_list'];
            display_ppl(ppl_list, loc_id)
        }
        else {
            alert('You must sign in.')
        }

    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });
};


function self_info() {

    loc_id = 'self_info'
    $("#"+loc_id).empty()

    // POST request to /get_hw
    url = "/get_self_info";
    $.post(url).done(function(response) {

        me_list = response['me_list'];
        display_ppl(me_list, loc_id)

    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });


};


function self_matches_over_time() {

    $('#matches_load').show();

    url = "/get_matches_over_time";
    $.get(url).done(function(response) {

        $('#matches_load').hide();

        x = response['x'];
        y = response['y'];

        ch = new chart("#ch_match_volume");
        ch.line(x, y, 'Matches');
        ch.set_title('Match Volume')
        ch.set_subtitle('Number of Tinder matches by day')
        ch.set_ylabel('')


    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });

};




function self_msg_over_time() {

    $('#msg_load').show();

    url = "/get_msg_over_time";
    $.get(url).done(function(response) {

        $('#msg_load').hide();

        x = response['x'];
        sent = response['sent'];
        recieved = response['recieved'];

        ch = new chart("#ch_msg_volume");
        ch.line(x, sent, 'Sent');
        ch.line(x, recieved, 'Recieved');
        ch.set_title('Message Volume')
        ch.set_subtitle('Number of messages sent/recieved by day')
        ch.set_ylabel('')


    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });

};
