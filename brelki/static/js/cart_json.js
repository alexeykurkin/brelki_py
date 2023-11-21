$(function() {

    cartBlock = $('.cart-block');
    cartClearButton = $('#cart-clear');

    $('#toggle_cart_button').click(function() {
        if (cartBlock.is(':hidden')) {
            cartBlock.slideToggle();
        } else if (cartBlock.is(':visible')) {
            cartBlock.slideToggle();
        }
    });

    $('#add-cart-form').submit(function(event) {
        event.preventDefault();
        $.ajax({
            type: 'post',
            url: this.action,
            data: {
                action: 'plus',
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            dataType: 'json',
            success: function(response) {
                $('.cart-sum-title').show();
                $('.cart-sum').text(parseInt(response.cart_sum))

                $('.cart-item-count').text(parseInt(response.cart_item_count));

                $('#toggle_cart_button').html(`Корзина (${response.user_cart_len})`);
                $('.no-cart-items-title').hide();

                if (cartBlock.is(':hidden')) {
                    cartBlock.slideToggle();
                }
                cartClearButton.show();

                const urlParams = new URLSearchParams(window.location.search);
                keychainId = urlParams.get('id');
                itemFound = false;
                $('.cart-item').each(function() {
                    if ($(this).children('h3').attr('id') == keychainId) {
                        itemFound = true;
                        $(this).children('h3').next().text(response.cart_item_count);
                        if (cartBlock.is(':hidden')) {
                            cartBlock.slideToggle();
                        }
                    } 
                });

                if (!itemFound) {
                    $('#cart-list').append(`
                    <a href="/keychain?id=${keychainId}">
                        <div class="cart-item">
                            <img src="${response.img}" width="25px" height="25px">
                            <h3 id="${response.id}">${response.title}</h3>
                            <h2>1</h2>
                        </div>
                    </a>
                    `);
                    $('#cart-submit-minus').show();
                    $('#cart-submit-add').hide();
                    $('#cart-submit-plus').show();
                    $('.cart-item-count-block').show();
                }

            },
            error: function(response) {
                console.log('error: ', response)
            }
        });

    });

    $('#substract-cart-form').submit(function(event) {

        event.preventDefault();
        $.ajax({
            type: 'post',
            url: this.action,
            data: {
                action: 'minus',
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            dataType: 'json',
            success: function(response) {
                $('.cart-sum').text(parseInt(response.cart_sum));
                $('.cart-item-count').text(parseInt(response.cart_item_count));

                if (response.user_cart_len == 0) {
                    cartClearButton.hide();
                    $('#cart-submit-minus').hide();
                    $('#cart-submit-add').show();
                    $('#cart-submit-plus').hide();
                    $('.cart-item-count-block').hide();
                    $('.no-cart-items-title').show();
                    $('.cart-sum-title').hide();
                }

                $('#toggle_cart_button').html(`Корзина (${response.user_cart_len})`);

                if (cartBlock.is(':hidden')) {
                    if (cartBlock.is(':hidden')) {
                        cartBlock.slideToggle();
                    }
                }
                // cartClearButton.show();

                const urlParams = new URLSearchParams(window.location.search);
                keychainId = urlParams.get('id');

                $('.cart-item').each(function() {
                    if ($(this).children('h3').attr('id') == keychainId) {
                        keychainCount = parseInt($(this).children('h3').next().text());
                        if ($(this).children('h3').next().text() == '1') {
                            $(this).remove();
                        } else {
                            $(this).children('h3').next().text(keychainCount - 1);
                        }
                    }
                });
            },
            error: function(response) {
                console.log('error: ', response)
            }
        });

    });

    $('#delete-cart-form').submit(function(event) {
        event.preventDefault();
        $.ajax({
            type: 'post',
            url: this.action,
            data: {
                action: 'delete',
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            dataType: 'json',
            success: function(response) {
                $('#toggle_cart_button').html('Корзина (0)');
                $('.no-cart-items-title').show();
                $('.cart-sum-title').hide();
                $('.cart-item').each(function() {
                    $(this).remove();
                    $('#cart-submit-minus').hide();
                    cartBlock.hide();
                    cartClearButton.hide();
                });
                $('#cart-submit-minus').hide();
                $('#cart-submit-add').show();
                $('#cart-submit-plus').hide();
                $('.cart-item-count-block').hide();
            },
            error: function(response) {
                console.log('error: ', response)
            }
        });

    });

});