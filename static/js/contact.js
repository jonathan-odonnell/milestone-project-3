// Checks the form is valid and posts the data entered to the /newsletter url and updates the html when the contact form send message button is clicked.
$('#contact-form').find('.btn').on('click', function (e) {
    // Prevents the button's default behaviour
    e.preventDefault()
    // Checks if the form is valid and if it is not reports its validity. Code is from https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation and https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/reportValidity
    if ($('#contact-form')[0].checkValidity() === false) {
        $('#contact-form')[0].reportValidity()
    } else {
        // checks that the form is valid and posts the data inputted to the /newsletter url. Code is from https://stackoverflow.com/questions/25881204/how-to-use-jquery-post-method-to-submit-form-values and https://stackoverflow.com/questions/7426085/jquery-getting-form-values-for-ajax-post
        $.post("/newsletter", $("#contact-form").serialize()).done(function () {
            //If a success status is returned, the HTML below is added to the DOM as the contact form's previous sibling and the contact form is removed from the DOM.
            $('#contact-form').parent().prepend('<p class="text-center">Thank you for your message. A member of the team will be in touch shortly</p>')
            $('#contact-form').remove()
        });
    }
});