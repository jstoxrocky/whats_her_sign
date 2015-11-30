function get_info() {

    // Get search string
    search_name = $("#search_name").val();
    $("#results_img").empty()

    // Switch the magnifying glass image to the loading spinner
    $('#search_load').show();
    $('#search_icon').hide();

    // POST request to /get_hw
    url = "/get_info";
    $.post(url,{search_name:search_name}).done(function(response) {
        
        $('#search_load').hide();
        $('#search_icon').show();

        ppl_list = response['ppl_list'];


        for (var person_num=0; person_num < ppl_list.length; person_num++) {

            name = ppl_list[person_num]['name']
            age = ppl_list[person_num]['age']
            sign = ppl_list[person_num]['sign']
            bio = ppl_list[person_num]['bio']
            birthday = ppl_list[person_num]['birthday']
            img_list = ppl_list[person_num]['img']
            last_active_at = ppl_list[person_num]['last_active_at']

            $("#results_img").append('<h1>'+name+' ('+age+')</h1>')
            $("#results_img").append('<h3>'+sign+'</h3>')
            $("#results_img").append('<p>Last active: '+last_active_at+'</p>')
            $("#results_img").append('<p>'+bio+'</p>')
            $("#results_img").append('<p>DOB: '+birthday+'</p>')

            for (var i =0; i < img_list.length; i++) {

                img = '<a target="_blank" href="'+img_list[i]+'"><img class="tinder_img" src="'+img_list[i]+'"/></a>'

                $("#results_img").append(img)
            }

        }
        



    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });
};



function login() {

    // Get search string
    fb_id = $("#fb_id_add").val();
    fb_auth_token = $("#fb_auth_add").val();

    // Switch the magnifying glass image to the loading spinner
    $('#search_load').show();
    $('#search_icon').hide();

    // POST request to /get_hw
    url = "/login";
    $.post(url,{fb_id:fb_id,fb_auth_token:fb_auth_token}).done(function(response) {
        
        $('#search_load').hide();
        $('#search_icon').show();
        window.location.href = "/";


    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });
};