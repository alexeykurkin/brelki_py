$(function() {
    priceOptions = $('.price-options div').hide();
    popularityOptions = $('.popularity-options div').hide();
    categoryOptions = $('.category-options div').hide();

    arrowPrice = $('#price-arrow');
    arrowPopularity = $('#popularity-arrow');
    arrowCategory = $('#category-arrow');
    arrowRating = $('#rating-arrow');

    optionTitlePrice = $('#h3-price');
    optionTitlePopularity = $('#h3-popularity');
    optionTitleCategory= $('#h3-category');
    optionTitleRating = $('#h3-rating');

    function handleFilterOptionSlide(div, arrow) {

        priceOptions.slideUp(300);
        popularityOptions.slideUp(300);
        categoryOptions.slideUp(300);

        if (arrow.hasClass('rotated')) {
            arrow.removeClass('rotated');
        } else {
            arrow.addClass('rotated');
        }

        div.slideToggle();
    }

    $('#h3-price').on('click', handleFilterOptionSlide(priceOptions, arrowPrice));

    // $('#h3-price').click(function() {
    //     priceOptions.slideToggle();

    //     if (arrowPrice.hasClass('rotated')) {
    //         arrowPrice.removeClass('rotated');
    //     } else if (!arrowPrice.hasClass('rotated')) {
    //         arrowPrice.addClass('rotated');
    //     }

    //     if (popularityOptions.is(':visible')) {
    //         popularityOptions.slideUp(300);
    //     } 
    //     if (categoryOptions.is(':visible')) {
    //         categoryOptions.slideUp(300);
    //     }
    // });


});