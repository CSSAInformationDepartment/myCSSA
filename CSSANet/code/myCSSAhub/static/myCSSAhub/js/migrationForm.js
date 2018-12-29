
  //Form validation init
$("#msform").parsley({
  errorClass: "is-invalid",
  successClass: "is-valid",
  errorsWrapper: '<span class="form-text text-danger"></span>',
  errorTemplate: "<span></span>",
  trigger: "blur"
});

//Date-Time Picker
$(function() {
  $("#datetimepicker1").datetimepicker({
    format: "L"
  });
});
