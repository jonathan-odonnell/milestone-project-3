// Sets the sort by dropdown button HTML as the value of the sort search parameters if the value is not null. Current URL code is from https://developer.mozilla.org/en-US/docs/Web/API/Window/location and https://developer.mozilla.org/en-US/docs/Web/API/URL, and search parameters code is from https://developer.mozilla.org/en-US/docs/Web/API/URL/searchParams

$(document).ready(function() {
    let currentUrl = new URL(window.location);
    let sortBy = currentUrl.searchParams.get("sort");
    if (sortBy !== null) {
        if (sortBy === "featured") {
            $('#sort-by').html("Featured");
        } else if (sortBy === "date-added") {
            $('#sort-by').html("Date Added");
        } else if (sortBy === "price-asc") {
            $('#sort-by').html("Price (Low - High)");
        } else if (sortBy === "price-desc") {
            $('#sort-by').html("Price (High - Low)");
        } else {
            $('#sort-by').html("Average Rating");
        }
    }
});

// Sets the sort search parameter as the value of the link in the sort by dropdown that has been clicked and reloads the page. Current URL code is from https://developer.mozilla.org/en-US/docs/Web/API/Window/location and https://developer.mozilla.org/en-US/docs/Web/API/URL, and search parameters code is from https://developer.mozilla.org/en-US/docs/Web/API/URL/searchParams

$(".sort-by").next().children().on("click", function () {
    let currentUrl = new URL(window.location);
    let sort = $(this).val();   
    currentUrl.searchParams.set("sort", sort);
    window.location.replace(currentUrl);
});

// When a filter button is clicked, sets the value of the brands, categories and price search parameters as the values of the checked filter checkboxes and radio buttons and reloads the page. https://developer.mozilla.org/en-US/docs/Web/API/Window/location and https://developer.mozilla.org/en-US/docs/Web/API/URL, and search parameters code is from https://developer.mozilla.org/en-US/docs/Web/API/URL/searchParams

$(".filter").on("click", function () {
    //Gets the current URL
    let currentUrl = new URL(window.location);

    // Deletes the categories, brands, price and page search perameters from currentUrl
    currentUrl.searchParams.delete("categories");
    currentUrl.searchParams.delete("brands");
    currentUrl.searchParams.delete("price");
    currentUrl.searchParams.delete("page");

    // Create empty lists for selected brands and selected categories 
    let selectedCategories = [];
    let selectedBrands = [];

    // Adds the value of each checked categories checkbox to the selectedCategories list
    $(this).closest("form").find("input[name='category']:checked").each(function () {
        selectedCategories.push($(this).val());
    });

    // Joins the categories in the selectedCategories list separated by commas and assign the string to categories
    let categories = selectedCategories.join(",");

    // If categories has a value, set it as the value of the categories search perameter in currentUrl
    if (categories) {
        currentUrl.searchParams.set("categories", categories);
    }

    // Adds the value of each checked brands checkbox to the selectedBrands list
    $(this).closest("form").find("input[name='brands']:checked").each(function () {
        selectedBrands.push($(this).val());
    });

    // Joins the brands in the selected list separated by commas and assign the string to brands
    let brands = selectedBrands.join(",");

    // If brands has a value, set it as the value of the brands search perameter in currentUrl
    if (brands) {
        currentUrl.searchParams.set("brands", brands);
    }

    // If a price radio button is checked, assign it's value to price.
    let price = $("input:radio:checked").val();

    // If price has a value, set it as the value of the price search perameter in currentUrl
    if (price) {
        currentUrl.searchParams.set("price", price);
    }

    // Replaces the url with currentUrl and reloads the page
    window.location.replace(currentUrl);
});

// When a reset button is clicked, deletes the categories, brands and price search parameters and reloads the page. Current URL code is from https://developer.mozilla.org/en-US/docs/Web/API/Window/location and https://developer.mozilla.org/en-US/docs/Web/API/URL, and search parameters code is from https://developer.mozilla.org/en-US/docs/Web/API/URL/searchParams

$(".clear-filters").on("click", function () {
    let currentUrl = new URL(window.location);
    currentUrl.searchParams.delete("categories");
    currentUrl.searchParams.delete("brands");
    currentUrl.searchParams.delete("price");
    window.location.replace(currentUrl);
});

// If the page title is reviews, sets the search item in the browser's local storage as the page title and the search_url as the current URL. Code for local storage is from https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage and code for the current URL is from https://developer.mozilla.org/en-US/docs/Web/API/Window/location

$(document).ready(function () {
    localStorage.clear()
    if ($('h1').html() == "Reviews") {
        localStorage.setItem("search", $('h1').html())
        localStorage.setItem("search_url", String(window.location))
    }
})