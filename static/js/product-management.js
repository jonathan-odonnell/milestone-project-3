$('#product-details').find('.btn').on('click', function () {
    // Code is from https://stackoverflow.com/questions/7386817/html5-form-checkvalidity-method-not-found and https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/reportValidity
    if ($('form')[1].reportValidity() == false) {
        return
    } else {
        $('#product-details').addClass('d-none')
        $('#product-features').removeClass('d-none')
    }
})

$('#product-features').find('.btn').first().on('click', function () {
    $('#product-details').removeClass('d-none')
    $('#product-features').addClass('d-none')
})