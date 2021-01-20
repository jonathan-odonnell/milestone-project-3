/* Sets the sort by dropdown button HTML as the value of the sort search parameters if the value is not null. Current URL code is from https://developer.mozilla.org/en-US/docs/Web/API/Window/location and https://developer.mozilla.org/en-US/docs/Web/API/URL, and search parameters code is from https://developer.mozilla.org/en-US/docs/Web/API/URL/searchParams */

$(document).ready(function () {
    let currentUrl = new URL(window.location);
    let search = currentUrl.searchParams.get("sort")
    if (search !== null) {
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

/*  Sets the sort search parameter as the value of the link in the product sort
by dropdown that has been clicked and reloads the page Current URL code is from
https:// developer.mozilla.org/en-US/docs/Web/API/Window/location. Search query
sort parameters code is from https://developer.mozilla.org/en-US/docs/Web/API/
URL/searchParams URL and https://developer.mozilla.org/en-US/docs/Web/API/URL, and replace code is from https://developer.mozilla.org/en-US/
docs/Web/API/Location/replace */

$('#product-sort-by').next().children().on('click', function () {
    let currentUrl = new URL(window.location);
    let sort = $(this).val();
    currentUrl.searchParams.set("sort", sort);
    window.location.replace(currentUrl);
})

/* When the next button is clicked on the add product or edit product page,
checks the form is valid and hides the div containing the product-details ID
and shows the div containing the product-features ID. Code for checking the
form validity is from https://stackoverflow.com/questions/7386817/
html5-form-checkvalidity-method-not-found and https://developer.mozilla.org/
en-US/docs/Web/API/HTMLFormElement/reportValidity */

$('#product-details').find('.btn').on('click', function () {
    if ($('form')[2].reportValidity() == false) {
        return
    } else {
        $('#product-details').addClass('d-none')
        $('#product-features').removeClass('d-none')
    }
})

/* When the back button is clicked on the add product or edit product page,
hides the div containing the product-features ID and shows the div containing
the product-details ID. */

$('#product-features').find('.btn').first().on('click', function () {
    $('#product-details').removeClass('d-none')
    $('#product-features').addClass('d-none')
})