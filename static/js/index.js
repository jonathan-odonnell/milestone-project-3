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

// Checks the email address entered in the newsletter sign up form is valid, posts it to the /newsletter url and dynamically updates the HTML with a response once a success status has been returned. Code for preventing the default behaviour of the submit button is from https://stackoverflow.com/questions/9824808/disable-form-auto-submit-on-button-click/9825224. Code for checking the form validity is from https://stackoverflow.com/questions/7386817/html5-form-checkvalidity-method-not-found and https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/reportValidity. Code for posting the form data and updating the HTML is from https://stackoverflow.com/questions/7426085/jquery-getting-form-values-for-ajax-post and https://api.jquery.com/jquery.post/

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