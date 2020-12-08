// Configures slick carousel. Code is from https://kenwheeler.github.io/slick/
$(document).ready(function () {
    $('#featured-products').slick({
        slidesToShow: 3,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 2000,
        dots: true,
        responsive: [
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2,
                }
            }]
    });
});