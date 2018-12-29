
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

$(".nextstep").click(function(){
  if ($("#msform").parsley().isValid({group:"block1", force:false})){
    console.log("Form Validation Complete")
    var formData = new FormData($('#msform').get(0));
    console.log(formData)
    $.ajax({
      type: "POST",
      url: "/hub/migration/",
      data: formData,
      processData: false,
      contentType: false,
      async: false,
      cache: false,
      dataType: "json",
      success: function (data) {
        console.log(data)
        href="/hub/regform/"+ data.migrationId +"/";
        $("#completeMigration").attr("href",href)
      },
      error : function(xhr,errmsg,err) {
        $('#ajax-errmsg').html('<div class="alert alert-dismissible alert-warning fade show" role="alert">Oops! We have encountered an error: '+errmsg+
          " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
          console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
      });
    } else {
      $("#msform").parsley().whenValidate({group:"block1", force:false})
    }
});
