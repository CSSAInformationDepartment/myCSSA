
var current_fs, next_fs, previous_fs; //fieldsets
var left, opacity, scale; //fieldset properties which we will animate
var animating; //flag to prevent quick multi-click glitches

var current_step = 1;

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

function LoadNextStep(current_fs,next_fs){
	if(animating) return false;	
	animating = true;


	//activate next step on progressbar using the index of next_fs
	$("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

	//show the next fieldset
	next_fs.show();
	//hide the current fieldset with style
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			//as the opacity of current_fs reduces to 0 - stored in "now"
			//1. scale current_fs down to 80%
			scale = 1 - (1 - now) * 0.2;
			//2. bring next_fs from the right(50%)
			left = (now * 50)+"%";
			//3. increase opacity of next_fs to 1 as it moves in
			opacity = 1 - now;
			current_fs.css({
        'transform': 'scale('+scale+')',
        'position': 'absolute'
      });
			next_fs.css({'left': left, 'opacity': opacity});
		},
		duration: 800,
		complete: function(){
			current_fs.hide();
			animating = false;
		},
		//this comes from the custom easing plugin
		easing: 'easeInOutBack'
	});
	current_step += 1;
}

function LoadPrevStep(current_fs,previous_fs){
	if(animating) return false;
	animating = true;
	//de-activate current step on progressbar
	$("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

	//show the previous fieldset
	previous_fs.show();
	//hide the current fieldset with style
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			//as the opacity of current_fs reduces to 0 - stored in "now"
			//1. scale previous_fs from 80% to 100%
			scale = 0.8 + (1 - now) * 0.2;
			//2. take current_fs to the right(50%) - from 0%
			left = ((1-now) * 50)+"%";
			//3. increase opacity of previous_fs to 1 as it moves in
			opacity = 1 - now;
			current_fs.css({'left': left});
			previous_fs.css({'transform': 'scale('+scale+')', 'opacity': opacity});
		},
		duration: 800,
		complete: function(){
			current_fs.hide();
			animating = false;
		},
		//this comes from the custom easing plugin
		easing: 'easeInOutBack'
	});
}


$(".nextstep").click(function(){
	current_fs = $(this).closest('fieldset')
	next_fs = current_fs.next()
	event.preventDefault();
	
	if (current_step == 1){
		var formData = {}	
		if ($("#msform").parsley().isValid({group:"step1", force:false})){
			console.log("Form Validation Complete")
			LoadNextStep(current_fs,next_fs);
		  } else {
        $("#msform").parsley().whenValidate({group:"step1", force:false})
      }
  }
  
  if (current_step == 2){
		var formData = {}	
		if ($("#msform").parsley().isValid({group:"step2", force:false})){
		    console.log("Form Validation Complete")
				LoadNextStep(current_fs,next_fs);
      } else {
        $("#msform").parsley().whenValidate({group:"step2", force:false})
      }
    }

  if (current_step == 3){
      if ($("#msform").parsley().isValid({group:"step3", force:false})){
					console.log("Form Validation Complete")
					var formData = new FormData($('#msform').get(0));
          $.ajax({
            type: "POST",
            url: "/hub/userinfo/create/",
            data: formData,
            processData: false,
            contentType: false,
            async: false,
            cache: false,
            success: function (data) {
              if (data.success) {
								LoadNextStep(current_fs,next_fs);
							} else {
								alert(data.errors)
							}
              
            },
            error : function(xhr,errmsg,err) {
              $('#ajax-errmsg').html('<div class="alert alert-dismissible alert-warning fade show" role="alert">Oops! We have encountered an error: '+errmsg+
              " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
              console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
              }
          });
        } else {
          $("#msform").parsley().whenValidate({group:"step3", force:false})
        }
    }
	
});

$(".previous").click(function(){

	current_fs = $(this).closest('fieldset')
	previous_fs = current_fs.prev();
	event.preventDefault();
	LoadNextStep(current_fs,previous_fs);
	current_step -= 1;
});

$(".submit").click(function(){
	return false;
})



