$(document).ready(function(){
    $('.dropdown-menu a').click(function(event){
        var acc = $(this).text();
        $(".dropdown-toggle").text(acc);
    });
});