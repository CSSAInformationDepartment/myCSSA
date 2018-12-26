
var current_fs, next_fs, previous_fs; //fieldsets
var left, opacity, scale; //fieldset properties which we will animate
var animating; //flag to prevent quick multi-click glitches

var current_step = 1;

//Custome Parsley.js Validators
window.Parsley.addValidator("telNumberCheck", {
    requirementType: "integer",
    validateString: function(value, requirement) {
      var validate_flag = false
      value = value.replace(/\s+/g,"");
      if (value.slice(0,2) == '04'){
        if (value.length == 10 && $.isNumeric(value)) {
          validate_flag = true
        }
      } else if (value.slice(0,4) == '+861') {
        if (value.length == 14 && $.isNumeric(value)) {
          validate_flag = true
        }
      } 
      return validate_flag
    },
    messages: {
      'en': "Please provide a valid mobile phone number",
      'zh-cn': "请提供有效的中国（+861开头）或澳洲（04开头）的移动电话号码"
    }
  });

  window.Parsley.addValidator('maxFileSize', {
    validateString: function(_value, maxSize, parsleyInstance) {
      if (!window.FormData) {
        alert('Your browser is no longer supported!');
        return true;
      }
      var files = parsleyInstance.$element[0].files;
      return files.length != 1  || files[0].size <= maxSize * 1024 * 1024;
    },
    requirementType: 'integer',
    messages: {
      'en': 'This file should not be larger than %s Mb',
      'zh-cn': '文件大小不应超过 %s Mb.'
    }
  });

  window.Parsley.addValidator("databaseCheck", {
    requirementType: "string",
    validateString: function(value, requirement) {
      var validate_flag = false;
      var ajax_url = '';

      if (requirement == 'telNumber'){
        ajax_url = "/hub/ajax/checkPhoneIntegrity/"
      }
      if (requirement == 'email'){
        ajax_url = "/hub/ajax/checkEmailIntegrity/"
      }
      if (requirement == 'studentId'){
        ajax_url = "/hub/ajax/checkStudentIdIntegrity/"
      }

      $.ajax({
        type: "POST",
        url: ajax_url,
        data: {'value': value},
        async:false,
        success: function (data) {
          if (data['result'] == 'Valid'){
            validate_flag = true;
          }
        },
        error: function (request, error) {
          console.log(" Can't do because: " + error);
      },
      })
      return validate_flag
    },
    messages: {
      'en': "We have found duplicated record for this input. Please consider proceeding account migration or asking our staff",
      'zh-cn': "系统检测到重复的注册记录，请尝试进行myCSSA账号迁移或联系我们的工作人员"
    }
  });

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

// Parsley.js Locale
Parsley.addMessages('zh-cn', {
  defaultMessage: "不正确的值",
  type: {
    email:        "请输入一个有效的电子邮箱地址",
    url:          "请输入一个有效的链接",
    number:       "请输入正确的数字",
    integer:      "请输入正确的整数",
    digits:       "请输入正确的号码",
    alphanum:     "请输入字母或数字"
  },
  notblank:       "请输入值",
  required:       "必填项",
  pattern:        "请填写英文或拼音姓名",
  min:            "输入值请大于或等于 %s",
  max:            "输入值请小于或等于 %s",
  range:          "输入值应该在 %s 到 %s 之间",
  minlength:      "请输入至少 %s 个字符",
  maxlength:      "请输入至多 %s 个字符",
  length:         "字符长度应该在 %s 到 %s 之间",
  mincheck:       "请至少选择 %s 个选项",
  maxcheck:       "请选择不超过 %s 个选项",
  check:          "请选择 %s 到 %s 个选项",
  equalto:        "您两次输入的密码不相符"
});

Parsley.setLocale('zh-cn');

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
			formData['email'] = $('form #id_email').val()
			formData['telNumber'] = $('form #id_telNumber').val()
			formData['password'] = $('form #id_password').val()
			formData['confirmPassword'] = $('form #id_confirmPassword').val()
      $.ajax({
          type: "POST",
          url: "/hub/regform/",
          data: formData,
          async: false,
          dataType: "json",
          success: function (data) {
            console.log(data.user)
            $('form #id_user').val(data.user);
            LoadNextStep(current_fs,next_fs);
          },
          error : function(xhr,errmsg,err) {
            $('#ajax-errmsg').html('<div class="alert alert-dismissible alert-warning fade show" role="alert">Oops! We have encountered an error: '+errmsg+
            " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
		  }
  }
  
  if (current_step == 2){
		var formData = {}	
		if ($("#msform").parsley().isValid({group:"step2", force:false})){
		    console.log("Form Validation Complete")
				LoadNextStep(current_fs,next_fs);
      }
    }

  if (current_step == 3){
      var formData = new FormData($('#msform').get(0));
      //formData.delete('email');
      //formData.delete('telNumber');
      //formData.delete('password');
      //formData.delete('confirmPassword');
      if ($("#msform").parsley().isValid({group:"step3", force:false})){
          console.log("Form Validation Complete")
          $.ajax({
            type: "POST",
            url: "/hub/userinfo/create/",
            data: formData,
            processData: false,
            contentType: false,
            async: false,
            cache: false,
            success: function (data) {
              console.log(data)
              LoadNextStep(current_fs,next_fs);
            },
            error : function(xhr,errmsg,err) {
              $('#ajax-errmsg').html('<div class="alert alert-dismissible alert-warning fade show" role="alert">Oops! We have encountered an error: '+errmsg+
              " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
              console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
              }
          });
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



