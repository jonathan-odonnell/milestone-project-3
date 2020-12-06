// Code is from https://www.tutorialrepublic.com/codelab.php?topic=bootstrap&file=accordion-with-plus-minus-icon

$(document).ready(function () {
  // Adds minus icon when collapse element is shown
  $(".collapse")
    .on("show.bs.collapse", function () {
      $(this)
        .prev(".card-header")
        .find(".fas")
        .removeClass("fa-plus")
        .addClass("fa-minus");
      // Adds minus icon when collapse element is hidden
    })
    .on("hide.bs.collapse", function () {
      $(this)
        .prev(".card-header")
        .find(".fas")
        .removeClass("fa-minus")
        .addClass("fa-plus");
    });
});

$('.toast').toast('show');