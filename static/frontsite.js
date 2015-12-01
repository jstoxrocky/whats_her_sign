function get_info() {

    // Get search string
    search_name = $("#search_name").val();
    // console.log(search_name)
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


        // console.log(ppl_list)

        for (var person_num=0; person_num < ppl_list.length; person_num++) {

            name = ppl_list[person_num]['name']
            age = ppl_list[person_num]['age']
            sign = ppl_list[person_num]['sign']
            bio = ppl_list[person_num]['bio']
            birthday = ppl_list[person_num]['birthday']
            img_list = ppl_list[person_num]['img']
            large_img_list = ppl_list[person_num]['large_img_list']
            last_active_at = ppl_list[person_num]['last_active_at']

           $("#results_img").append('<div id="'+person_num+'" class="well"></div>')

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
        



    // If POST request fails
    }).fail(function(error) {
        $("#get_hw_response").text(error);
        console.log("FAILURE");
    });
};
