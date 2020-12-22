// Adds minus icon to the accordion item headers when the item's body is shown. Collapse show code is from https://getbootstrap.com/docs/4.5/components/collapse/#methods. CSS classes for the plus and minus icons are from https://fontawesome.com/icons/plus?style=solid and https://fontawesome.com/icons/minus?style=solid

$(".collapse").on("show.bs.collapse", function () {
    $(this)
        .prev(".card-header")
        .find(".fas")
        .removeClass("fa-plus")
        .addClass("fa-minus");
})

// Adds minus icon to the accordion item headers when the item's body is hidden. Collapse hide code is from https://getbootstrap.com/docs/4.5/components/collapse/#methods. CSS classes for the plus and minus icons are from https://fontawesome.com/icons/plus?style=solid and https://fontawesome.com/icons/minus?style=solid

$(".collapse").on("hide.bs.collapse", function () {
    $(this)
        .prev(".card-header")
        .find(".fas")
        .removeClass("fa-minus")
        .addClass("fa-plus");
});

// Shows the toasts. Code is from https://getbootstrap.com/docs/4.5/components/toasts/

$('.toast').toast('show');