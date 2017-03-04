/**
 * Created by weijunwu on 11/5/16.
 */
$(document).ready(function() {
    $('select').material_select();
});

$('.search-label').on('click', function(event) {
    $('.error-list').empty();

    if (validateSearchForm()) {
        $('.search-form').submit();
    }
});

function validateSearchForm() {
    var errors = [];

    if($('[name="location"]').val() == "") {
        errors.push("Location field cannot be empty.");
    }

    if (parseInt($('[name="min_bedroom_num"]').val()) != 0 && parseInt($('[name="max_bedroom_num"]').val()) != 65535
        && parseInt($('[name="min_bedroom_num"]').val()) > parseInt($('[name="max_bedroom_num"]').val())) {
        errors.push("Min bedroom number cannot be greater than max bedroom number.");
    }

    if (parseInt($('[name="min_price"]').val()) != -1 && parseInt($('[name="max_price"]').val()) != 102400
        && parseInt($('[name="min_price"]').val()) > parseInt($('[name="max_price"]').val())) {
        errors.push("Min price cannot be greater than max price.");
    }

    for (var i = 0; i < errors.length; i++) {
        $('.error-list').append('<li>' + errors[i] + '</li>');
    }

    if (errors.length == 0) {
        return true;
    } else return false;
}