$("#sort button").on("click", function () {
    let currentUrl = new URL(window.location);
    let sort = $(this).val();
    currentUrl.searchParams.set("sort", sort);
    window.location.replace(currentUrl);
});

$("#filter").on("click", function () {
    let currentUrl = new URL(window.location);
    let selectedCategories = [];
    let selectedBrands = [];
    $("input[name='categories']:checked").each(function () {
        selectedCategories.push($(this).val());
    });
    let categories = selectedCategories.join(",");
    if (categories) {
        currentUrl.searchParams.set("categories", categories);
    } else {
        currentUrl.searchParams.delete("categories");
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
    currentUrl.searchParams.delete("categories");
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