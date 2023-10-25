$(function() {

    cartButton = $('.cart-button');
    showCartButton = $('.show-cart-button');

    if (!localStorage.getItem('cart')) {
        localStorage.setItem('cart', JSON.stringify({}));
    }

    cartButton.click(function() {

        const urlParams = new URLSearchParams(window.location.search);

        keychainId = urlParams.get('id');
        keychainTitle = $('#keychain-title-value').text();
        keychainPrice = $('#keychain-price-value').text();
        keychainImg = $('#keychain_image').attr('src');


        cartList = JSON.parse(localStorage.getItem('cart'));

        if (!(keychainId in cartList)) {
            cartList[keychainId] = {
                'count': 1,
                'title': keychainTitle,
                'price': keychainPrice,
                'img': keychainImg
            };
        } else {
            cartList[keychainId].count += 1;
        }

        localStorage.setItem('cart', JSON.stringify(cartList));
        cartItems = JSON.parse(localStorage.cart);

        $('#cart-list').remove();
        $('.cart-title').after('<ul id="cart-list"></ul>');

        let sum = 0;
        let cartCount = 0;
        Object.values(cartItems).forEach((value) => {
            sum += parseInt(value.price) * parseInt(value.count);
            cartCount += parseInt(value.count);
            $('#cart-list').append(`
                <li class='cart-item'>${value.title} Количество: ${value.count} 
                    <img src=${value.img} width='25px' height='25px'>
                </li>
            `);
        });
        $('#cart-list').append(`<li class='cart-item'>Всего товаров: ${cartCount}</li>`);
        $('#cart-list').append(`<li class='cart-item'>Сумма: ${sum} ₽</li>`);

    });

});