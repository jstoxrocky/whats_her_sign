function display_ppl(ppl_list, loc_id, is_new) {

        for (var person_num=0; person_num < ppl_list.length; person_num++) {

            name = ppl_list[person_num]['name']
            _id = ppl_list[person_num]['_id']
            age = ppl_list[person_num]['age']
            sign = ppl_list[person_num]['sign']
            bio = ppl_list[person_num]['bio']
            birthday = ppl_list[person_num]['birthday']
            img_list = ppl_list[person_num]['img']
            large_img_list = ppl_list[person_num]['large_img_list']
            last_active_at = ppl_list[person_num]['last_active_at']

            outside_div = $("#" + loc_id).append('<div id="'+person_num+'" class="well"></div>')

            $("#"+person_num).append('<h1 style="display:inline;">'+name+' ('+age+')</h1><span style="float:right;" id="put_here"></span>')
            $("#"+person_num).append('<h3>'+sign+'</h3>')
            $("#"+person_num).append('<p>Last active: '+last_active_at+'</p>')
            $("#"+person_num).append('<p>'+bio+'</p>')
            $("#"+person_num).append('<p>DOB: '+birthday+'</p>')
            $("#"+person_num).append('<p id="curr_id" style="font-size:1em;">'+_id+'</p>')


            for (var i =0; i < img_list.length; i++) {

                img = '<a target="_blank" href="'+large_img_list[i]+'"><img class="tinder_img" src="'+img_list[i]+'"/></a>'
                $("#"+person_num).append(img)
            }

            if (is_new) {

                pass = '<img class="nav_bar_img pass action_btn" src="../static/images/x_black.png">'
                like = '<img class="nav_bar_img like action_btn" src="../static/images/heart_black.png">'
                superlike = '<img class="nav_bar_img superlike action_btn" src="../static/images/star_black.png">'
                // button_div = '<button class="btn_div" value="'+_id+'">' + pass + superlike + like + '</button>'
                $("#put_here").append(pass + superlike + like)

                $(function() {
                    $('.like').click(function(e) {
                        url = "/like";
                        $.post(url,{_id:_id}).done(function(response) {
                            
                           likes_remaining = response['likes_remaining']
                           match = response['match']
                           if (match) {
                                alert("Yeah! You matched with " + name)
                           }
                           explore_info()


                        // If POST request fails
                        }).fail(function(error) {
                            console.log(error);
                        });
                    });
                });
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
            is_new = response['new'];
            console.log(is_new)
            display_ppl(ppl_list, loc_id, is_new)
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
        display_ppl(me_list, loc_id, false)

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



function superlike(btn) {

    _id = btn.val()

    // Switch the magnifying glass image to the loading spinner
    // $('#search_load').show();

    // POST request to /get_hw
    url = "/superlike";
    $.post(url,{_id:_id}).done(function(response) {
        
       console.log(response)

    // If POST request fails
    }).fail(function(error) {
        console.log(error);
    });
};



function like(btn) {

    _id = btn.val()

    // Switch the magnifying glass image to the loading spinner
    // $('#search_load').show();

    // POST request to /get_hw
    url = "/like";
    $.post(url,{_id:_id}).done(function(response) {
        
       console.log(response)

    // If POST request fails
    }).fail(function(error) {
        console.log(error);
    });
};



function explore_info() {

    loc_id = 'explore_info'
    $("#"+loc_id).empty()

    $('#flame_load').show();
    $('#flame').hide();

    // POST request to /get_hw
    url = "/get_explore_info";
    $.post(url).done(function(response) {

        $('#flame_load').hide();
        $('#flame').show();

        ppl_list = response['ppl_list'];
        display_ppl(ppl_list, loc_id, true)

    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });


};


