$(document).ready(function() {

    $('.modal').modal({
        dismissible: false
    });

    $('#upload-button').click(function() {
        $('#modal1').modal('open');
    });

    $('#go-back, #go-start').click(function() {
        $(".dd-container").animate({
            opacity: '1'
        }, {
            duration: 200,
            queue: false
        });

        $(".uf-container").animate({
            opacity: '0'
        }, {
            duration: 200,
            queue: false
        });

        $(".dt-container").animate({
            opacity: '0'
        }, {
            duration: 200,
            queue: false
        });
    });

});
