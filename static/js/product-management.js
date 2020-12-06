$('#product-details').find('.btn').on('click', function () {
    $('#product-details').addClass('d-none')
    $('#product-features').removeClass('d-none')
})

$('#product-features').find('.btn').first().on('click', function () {
    $('#product-details').removeClass('d-none')
    $('#product-features').addClass('d-none')
})