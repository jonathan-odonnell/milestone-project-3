// Sets the custom validity message for the confirm-password ID as an empty string when the value of the ID is changed. Code is from https://codepen.io/diegoleme/pen/surIK

$('#confirm-password').on('change', function () {
    $(this)[0].setCustomValidity("")
})

// Sets the custom validity message for the confirm-password ID if the password ID doesn't match the value of the confirm-password ID. Code for preventing the default behaviour of the submit button is from https://stackoverflow.com/questions/9824808/disable-form-auto-submit-on-button-click/9825224. Code for checking the form validity is from https://codepen.io/diegoleme/pen/surIK, https://stackoverflow.com/questions/7386817/html5-form-checkvalidity-method-not-found and https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/reportValidity

$('#sign-up-form').submit(function (e) {
    if ($(this).find('#password').val() !== $(this).find('#confirm-password').val()) {
        e.preventDefault()
        $(this).find('#confirm-password')[0].setCustomValidity("Passwords don't match")
    } else if ($(this)[0].reportValidity() === false) {
        e.preventDefault()
    }
})