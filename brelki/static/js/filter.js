$(function() {
    priceOptions = $('.price-options div').hide();
    popularityOptions = $('.popularity-options div').hide();
    categoryOptions = $('.category-options div').hide();

    arrowPrice = $('#price-arrow');
    arrowPopularity = $('#popularity-arrow');
    arrowCategory = $('#category-arrow');

    optionTitlePrice = $('#h3-price');
    optionTitlePopularity = $('#h3-popularity');
    optionTitleCategory= $('#h3-category');

    $('#h3-price').click(function() {
        priceOptions.slideToggle();

        if (arrowPrice.hasClass('rotated')) {
            arrowPrice.removeClass('rotated');
        } else if (!arrowPrice.hasClass('rotated')) {
            arrowPrice.addClass('rotated');
        }

        if (popularityOptions.is(':visible')) {
            popularityOptions.slideUp(300);
        } 
        if (categoryOptions.is(':visible')) {
            categoryOptions.slideUp(300);
        }
    });
    $('#h3-popularity').click(function() {
        popularityOptions.slideToggle();

        if (arrowPopularity.hasClass('rotated')) {
            arrowPopularity.removeClass('rotated');
        } else if (!arrowPopularity.hasClass('rotated')) {
            arrowPopularity.addClass('rotated');
        }

        if (priceOptions.is(':visible')) {
            priceOptions.slideUp(300);
        } 
        if (categoryOptions.is(':visible')) {
            categoryOptions.slideUp(300);
        }
    });
    $('#h3-category').click(function() {

        if (arrowCategory.hasClass('rotated')) {
            arrowCategory.removeClass('rotated');
        } else if (!arrowCategory.hasClass('rotated')) {
            arrowCategory.addClass('rotated');
        }

        categoryOptions.slideToggle();
        if (priceOptions.is(':visible')) {
            priceOptions.slideUp(300);
        } 
        if (popularityOptions.is(':visible')) {
            popularityOptions.slideUp(300);
        } 
    });
});
