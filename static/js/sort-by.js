$(document).ready(function() {
    let currentUrl = new URL(window.location);
    let sortBy = currentUrl.searchParams.get("sort")
    if (sortBy !== null) {
        if (sortBy === "featured") {
            $('#sort-by').html("Featured")
        } else if (sortBy === "date-added") {
            $('#sort-by').html("Date Added")
        } else if (sortBy === "price-asc") {
            $('#sort-by').html("Price (Low - High)")
        } else if (sortBy === "price-desc") {
            $('#sort-by').html("Price (High - Low)")
        } else {
            $('#sort-by').html("Average Rating")
        }
    }
})

$("#sort-by").next().children().on("click", function () {
    let currentUrl = new URL(window.location);
    let sort = $(this).val();
    
    currentUrl.searchParams.set("sort", sort);
    window.location.replace(currentUrl);
});

$('#collapseFilters').on('show.bs.collapse', function() {
    $('#filters').html('<i class="fas fa-times pr-1"></i>Close')
})

$('#collapseFilters').on('hide.bs.collapse', function() {
    $('#filters').html('<i class="fas fa-filter pr-1"></i>Filters')
})

$("#filter").on("click", function () {
    let currentUrl = new URL(window.location);
    let selectedCategories = [];
    let selectedBrands = [];
    $("input[name='category']:checked").each(function () {
        selectedCategories.push($(this).val());
    });
    let categories = selectedCategories.join(",");
    if (categories) {
        currentUrl.searchParams.set("category", categories);
    } else {
        currentUrl.searchParams.delete("category");
    }
    $("input[name='brands']:checked").each(function () {
        selectedBrands.push($(this).val());
    });
    let brands = selectedBrands.join(",");
    if (brands) {
        currentUrl.searchParams.set("brands", brands);
    } else {
        currentUrl.searchParams.delete("brands");
    }
    let price = $("input:radio:checked").val();
    if (price) {
        currentUrl.searchParams.set("price", price);
    }
    currentUrl.searchParams.delete("page");
    window.location.replace(currentUrl);
});

$("#clear-filters").on("click", function () {
    let currentUrl = new URL(window.location);
    currentUrl.searchParams.delete("category");
    currentUrl.searchParams.delete("brands");
    currentUrl.searchParams.delete("price");
    window.location.replace(currentUrl);
});

$(document).ready(function () {
    localStorage.clear()
    if ($('h1').html() == "Reviews") {
        localStorage.setItem("search", $('h1').html())
        localStorage.setItem("search_url", String(window.location))
    }
})