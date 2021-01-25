// Changes the bars icon to the times icon and collapses the collapsable search bar if it is expanded when the navbar toggler. Collapse show code is from https://getbootstrap.com/docs/4.5/components/collapse. CSS classes for the bars and times icons are from https://fontawesome.com/icons/bars?style=solid and https://fontawesome.com/icons/times?style=solid.

$(".navbar-collapse").on("show.bs.collapse", function () {
    $("#search").collapse("hide");
    $(".navbar-toggler i").addClass("fa-times").removeClass("fa-bars");
});

// Changes the times icon to the bars icon when the navbar is expanded. Collapse hide code is from https://getbootstrap.com/docs/4.5/components/collapse. CSS classes for the bars and times icons are from https://fontawesome.com/icons/bars?style=solid and https://fontawesome.com/icons/times?style=solid.

$(".navbar-collapse").on("hide.bs.collapse", function () {
    $(".navbar-toggler i").addClass("fa-bars").removeClass("fa-times");
});

// Collapses the navbar when the collapsable search bar is expanded. Code is from https://getbootstrap.com/docs/4.5/components/collapse/#collapsehide

$("#search").on("show.bs.collapse", function () {
    $(".navbar-collapse").collapse("hide");
});

// Adds minus icon to the accordion item headers when the item's body is shown. Collapse show code is from https://getbootstrap.com/docs/4.5/components/collapse. CSS classes for the plus and minus icons are from https://fontawesome.com/icons/plus?style=solid and https://fontawesome.com/icons/minus?style=solid

$(".collapse").on("show.bs.collapse", function () {
    $(this)
        .prev(".card-header")
        .find(".fas")
        .removeClass("fa-plus")
        .addClass("fa-minus");
});

// Adds minus icon to the accordion item headers when the item's body is hidden. Collapse hide code is from https://getbootstrap.com/docs/4.5/components/collapse. CSS classes for the plus and minus icons are from https://fontawesome.com/icons/plus?style=solid and https://fontawesome.com/icons/minus?style=solid

$(".collapse").on("hide.bs.collapse", function () {
    $(this)
        .prev(".card-header")
        .find(".fas")
        .removeClass("fa-minus")
        .addClass("fa-plus");
});

// Shows the toasts. Code is from https://getbootstrap.com/docs/4.5/components/toasts/

$('.toast').toast('show');