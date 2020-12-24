// When the send message button is clicked, checks the form is valid and posts the data entered to the /newsletter url and updates the HTML with a response when a success status is received. Code for checking the form validity is from https://stackoverflow.com/questions/7386817/html5-form-checkvalidity-method-not-found and https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/reportValidity. Code for posting the form data and updating the HTML is from https://stackoverflow.com/questions/7426085/jquery-getting-form-values-for-ajax-post and https://stackoverflow.com/questions/9824808/disable-form-auto-submit-on-button-click/9825224

$('#contact-form').find('.btn').on('click', function (e) {
    e.preventDefault()
    if ($('#contact-form')[0].reportValidity() === true) {
        $.post("/newsletter", $("#contact-form").serialize()).done(function () {
            $('#contact-form').parent().prepend('<p class="text-center">Thank you for your message. A member of the team will be in touch shortly</p>')
            $('#contact-form').remove()
        });
    }
});