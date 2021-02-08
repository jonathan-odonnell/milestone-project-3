// Sets the custom validity message for the confirm-password ID the error message if the password doesn't match the confirm password value or as an empty string on keyup. Code is from https://codepen.io/diegoleme/pen/surIK.

$('#confirm-password').on('keyup', function () {
    console.log($('#sign-up-form')[0].checkValidity())
    if ($('#sign-up-form').find('#password').val() !== $(this).val()) {
        $(this)[0].setCustomValidity("Passwords don't match");
    } else {
        $(this)[0].setCustomValidity("");
    }
});
