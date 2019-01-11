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


//Custome Parsley.js Validators

var ajax_urls_dict = {
    'telNumber': '/hub/ajax/checkPhoneIntegrity/',
    'email': '/hub/ajax/checkEmailIntegrity/',
    'studentId':'/hub/ajax/checkStudentIdIntegrity/'
}

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
      'zh-cn': "请提供有效的中国（+86开头）或澳洲（04开头）的移动电话号码"
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

      $.ajax({
        type: "POST",
        url: ajax_urls_dict[requirement],
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
