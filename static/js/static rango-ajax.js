$(document).ready(function(){
    $('#search-input').keyup(function() {
        var query;
        // extracte the value of input component
        query = $(this).val();
        
        // ajax method
        // /rango/suggest/?suggestion=
        $.get('/rango/suggest/',
        {'suggestion': query},
        function(data) {
            $('#categories-listing').html(data);
            })
    });
    
    // $('#query').keyup(function(){
    //     var search_engine;
    //     var query;

    //     search_engine = $('#search_engine').val();
    //     query = $(this).val();

    //     $.get('window.location.pathname',
    //     {'search_engine':search_engine,'query':query},
    //     function(data){
    //         alert("aaaa");
    //     })
    // });

    $('.rango-page-add').click(function() {
        var categoryid = $(this).attr('data-categoryid');
        var title = $(this).attr('data-title');
        var url = $(this).attr('data-url');
        var clickedButton = $(this);
        $.get('/rango/search_add_page/',
        {'category_id': categoryid, 'title': title, 'url': url},
        function(data) {
        $('#page-listing').html(data);
            clickedButton.hide();
        })
    });
        

});