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

// Checks the email address entered in the newsletter sign up form is valid, posts it to the /newsletter url and dynamically updates the HTML with a response once a success status has been returned. Code is from https://stackoverflow.com/questions/25881204/how-to-use-jquery-post-method-to-submit-form-values, https://stackoverflow.com/questions/7426085/jquery-getting-form-values-for-ajax-post and https://stackoverflow.com/questions/9824808/disable-form-auto-submit-on-button-click/9825224

$('#newsletter-sign-up .btn').on('click', function (e) {
    e.preventDefault()
    if ($('#newsletter-sign-up')[0].reportValidity() == true) {
        $.post("/newsletter", $("#newsletter-sign-up").serialize()).done(function () {
            $('.newsletter-heading').html('<p>Thanks for signing up to our newsletter</p>')
            $('.newsletter-heading').siblings('.col-12').remove()
            $('.newsletter-heading').removeClass('subheadings').addClass('my-5')
        });
    }
});