function changeSize() {
    if ($('.menu').width() < 1000) {
        $('.menu').addClass('menu-min');
        $('#keychain_image').addClass('img-min');
        $('.filter-options-block').addClass('filter-min');
    } else {
        $('.menu').removeClass('menu-min');
        $('#keychain_image').removeClass('img-min');
        $('.filter-options-block').removeClass('filter-min');
    }
}

$(function() {
    changeSize();
    $(window).resize(function() {
        changeSize();
        });
});