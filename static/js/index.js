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
            },
            {
                breakpoint: 776,
                settings: {
                    arrows: false,
                    slidesToShow: 2,

                }
            }]
    });
});

$('#newsletter-submit').on('click', function (e) {
    e.preventDefault()
    let email = $("input[name='email']").val()
    $.post("/newsletter", { "email": email }).done(function () {
        $('#newsletter-heading').html('<p class="lead">Thanks for signing up to our newsletter</h2>')
        $('#newsletter-heading').siblings('.col-12').remove()
        $('#newsletter-heading').removeClass('subheadings').addClass('my-5')
    });
});