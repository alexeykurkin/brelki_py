$(function() {

    const cartBlock = $('.cart-block'); // блок корзины
    const cartList = $('#cart-list'); // div со списком брелков (cart-item) в блоке корзины
    const cartClearButton = $('#cart-clear'); // кнопка очистки корзины
    const keychainCountElt = $('#cartKeychainCount'); // кол-во брелков в корзине
    const cartSumElt = $('#cartSumElement'); // сумма стоимостей всех брелков
    const cartSumBlock = $('.cart-sum-title');
    const noCartItemsTitle = $('#noCartItemsTitle'); // надпись, что корзина пуста
    const toggleCartButton = $('#toggle_cart_button'); // кнопка показа/скрытия корзины
    const cartSubmitMinus = $('#cart-submit-minus'); // Кнопка "-" у счётчика брелков
    const cartSubmitPlus = $('#cart-submit-plus'); // Кнопка "+" у счётчика брелков
    const cartSubmitAdd = $('#cart-submit-add'); // Кнопка добавления брелка в корзину

    function handleCartAction(cartAction, form) {
        form.submit(function(event) {
            event.preventDefault();
            $.ajax(
                {
                    type: 'post',
                    url: this.action,
                    data: {
                        action: cartAction,
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                    },
                    dataType: 'json',
                    success: function(response) {

                        const cartKeychains = $('.cart-item');
                        let cartSum;
                        let cartLen
                        let cartItemCount;
                        let keychainId;
                        let keychainImg;
                        let keychainTitle;

                        if (cartAction != 'delete') {
                            cartItemCount = response.cart_item_count;
                            keychainId = response.id;
                            keychainImg = response.img;
                            keychainTitle = response.title;
                            cartSum = response.cart_sum;
                            cartLen = response.user_cart_len;
                        } else {
                            cartLen = 0;
                            cartSum = 0;
                            cartItemCount = 0;
                        }

                        function handleAddPlusMinusDisplay(mode) {
                            console.log(mode);
                            if (mode == 'hide_add') {
                                cartSubmitAdd.hide();
                                cartSubmitPlus.show();
                                cartSubmitMinus.show();
                                keychainCountElt.show();
                            } else if (mode == 'show_add') {
                                cartSubmitAdd.show();
                                cartSubmitPlus.hide();
                                cartSubmitMinus.hide();
                                keychainCountElt.hide();
                            }
                        }

                        function handleEmptyCart(cartLen) {
                            if (cartLen == 0) {
                                cartClearButton.hide();
                                cartSumBlock.hide();
                                noCartItemsTitle.show();
                                handleAddPlusMinusDisplay(mode='show_add');
                                cartKeychains.each(function() {
                                    $(this).remove();
                                });
                            } else {
                                cartClearButton.show();
                                cartSumBlock.show();
                                noCartItemsTitle.hide();
                                handleAddPlusMinusDisplay(mode='hide_add');
                            }
                        }

                        function updateSumAndCount(cartItemCount, cartSum, cartLen) {
                            keychainCountElt.text(cartItemCount);
                            cartSumElt.text(cartSum);
                            toggleCartButton.html(`Корзина (${cartLen})`);
                        }

                        function appendKeychainToCart(keychainData) {
                            cartList.append(`
                                <a href="/keychain/${keychainData.keychainId}">
                                    <div class="cart-item">
                                        <img src="/${keychainData.keychainImg}" width="25px" height="25px">
                                        <h3 id="${keychainData.keychainId}">${response.title}</h3>
                                        <h2>1</h2>
                                    </div>
                                </a>
                            `);
                        }

                        if (cartBlock.is(':hidden')) {
                            cartBlock.slideToggle();
                        }

                        handleEmptyCart(cartLen);
                        
                        let cartKeychainFound = false;
                        cartKeychains.each(function() {
                            let cartKeychainTitle = $(this).children('h3');
                            let cartKeychainId = $(this).children('h3').attr('id');
                            if (cartKeychainId == keychainId) {
                                cartKeychainFound = true;
                                if (cartItemCount == 0) {
                                    $(this).remove();
                                    handleAddPlusMinusDisplay(mode='show_add');
                                } else {
                                    cartKeychainTitle.next('h2').text(cartItemCount);
                                }
                            }
                        });
                        
                        // Изменение суммы покупок и количества брелка в корзине
                        updateSumAndCount(cartItemCount, cartSum, cartLen);

                        if (!cartKeychainFound) {
                            let keychainData = {'keychainId': keychainId, 'keychainTitle': keychainTitle, 'keychainImg': keychainImg};
                            if (cartAction != 'delete') {
                                appendKeychainToCart(keychainData);
                            }
                        }
                    }
                }
            );
        });
    }

    toggleCartButton.on('click', () => cartBlock.slideToggle());
    handleCartAction('plus', $('#add-cart-form'));
    handleCartAction('minus', $('#substract-cart-form'));
    handleCartAction('delete', $('#delete-cart-form'));

});