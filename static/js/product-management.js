$(document).ready(function() {
    let currentUrl = new URL(window.location);
    let search = currentUrl.searchParams.get("sort")
    if (search !== undefined) {
        if (search === "a-to-z") {
            $('#product-filter').html("Name A - Z")
        } else if (search === "z-to-a") {
            $('#product-filter').html("Name Z - A")
        } else if (search === "cat_asc") {
            $('#product-filter').html("Category A - Z")
        } else if (search === "cat_desc") {
            $('#product-filter').html("Category Z - A")
        }
    }
})

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

$('#product-filter').next().children().on('click', function() {
    let currentUrl = new URL(window.location);
    let sort = $(this).val();
    html = $(this).html()
    currentUrl.searchParams.set("sort", sort);
    window.location.replace(currentUrl);
})