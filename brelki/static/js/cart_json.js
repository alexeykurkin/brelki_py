$(function() {
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
                const urlParams = new URLSearchParams(window.location.search);
                keychainId = urlParams.get('id');
                itemFound = false;
                $('.cart-item').each(function() {

                    if ($(this).children('h3').attr('id') == keychainId) {
                        itemFound = true;
                        keychainCount = parseInt($(this).children('h3').next().text());
                        $(this).children('h3').next().text(keychainCount + 1);
                    } 
                });

                if (!itemFound) {
                    $('#cart-list').append(`
                    <div class="cart-item">
                        <img src="${response.img}" width="25px" height="25px">
                        <h3 id="${response.id}">${response.title}</h3>
                        <h2>1</h2>
                    </div>
                    `)
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
                console.log('action: ', response);
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
                $('.cart-item').each(function() {
                    $(this).remove();
                });
            },
            error: function(response) {
                console.log('error: ', response)
            }
        });

    });

});