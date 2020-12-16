
// Code for getting data inputted into the form is from https://stackoverflow.com/questions/25881204/how-to-use-jquery-post-method-to-submit-form-values

$('#contact-form').find('.btn').on('click', function (e) {
    e.preventDefault()
    $.post("/newsletter", $("#contact-form").serialize()).done(function () {
        $('#contact-form').parent().prepend('<p class="text-center my-5">Thank you for your message. A member of the team will be in touch shortly</p>')
        $('#contact-form').remove()
    });
});