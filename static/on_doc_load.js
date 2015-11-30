$(document).ready(function(){


        $("#hw_date_add").datepicker({dateFormat: 'yy-mm-dd'});

        $('.add_more').click(function(e){
        	e.preventDefault();
        	$(this).before("<input type='file'/>");
    	});


        $('#search_load').hide();
        $('#confirm_upload_load').hide();
        $('#my_sales_load').hide();
        $('#my_purchases_load').hide()
        $('.spinner').hide();

        
});