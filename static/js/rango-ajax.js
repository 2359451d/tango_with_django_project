$(document).ready(function(){
    $('#like_btn').click(function(){
        var catecategoryIdVar;
        // id is extracted from the button
        catecategoryIdVar = $(this).attr('data-categoryid');

        // handles AJAX GET requests, get() method is asynchronous
        //  /rango/like_category/?category_id=<category_id_var>
        // data para is from Response(view)
        $.get('/rango/like_category/',
        {'category_id': catecategoryIdVar},
        function(data) {
        $('#like_count').html(data);
        $('#like_btn').hide();
        })
    });
});