Page({
  data: {
    loading: false,
    result: null,
    name: '',
    studentId: '',
    phone: '',
    nameError: '',
    studentIdError: '',
    phoneError: ''
  },

  onNameInput(e) {
    this.setData({
      name: e.detail.value,
      nameError: ''
    });
  },

  onStudentIdInput(e) {
    this.setData({
      studentId: e.detail.value,
      studentIdError: ''
    });
  },

  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value,
      phoneError: ''
    });
  },

  clearErrors() {
    this.setData({
      nameError: '',
      studentIdError: '',
      phoneError: ''
    });
  },

  validateForm() {
    const { name, studentId, phone } = this.data;
    let isValid = true;

    this.clearErrors();

    if (!name) {
      this.setData({ nameError: '姓名不能为空' });
      isValid = false;
    }

    if (!studentId) {
      this.setData({ studentIdError: '学号不能为空' });
      isValid = false;
    }

    if (!phone) {
      this.setData({ phoneError: '手机号不能为空' });
      isValid = false;
    } else if (phone.length !== 11) {
      this.setData({ phoneError: '手机号格式不正确' });
      isValid = false;
    }

    return isValid;
  },

  handleRegister() {
    if (this.data.loading) {
      return;
    }

    if (!this.validateForm()) {
      return;
    }

    this.setData({
      loading: true,
      result: null
    });

    const { name, studentId, phone } = this.data;

    wx.request({
      url: 'http://127.0.0.1:8000/api/register_with_info/',
      method: 'POST',
      data: {
        name: name,
        student_id: studentId,
        phone: phone
      },
      success: (res) => {
        this.setData({
          result: res.data
        });

        if (res.data.success) {
          this.setData({
            name: '',
            studentId: '',
            phone: ''
          });

          wx.showToast({
            title: '报到成功',
            icon: 'success',
            duration: 2000
          });
        } else {
          wx.showToast({
            title: res.data.message,
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        this.setData({
          result: {
            success: false,
            message: '网络请求失败，请确保服务器正在运行'
          }
        });

        wx.showToast({
          title: '网络请求失败',
          icon: 'error',
          duration: 2000
        });
      },
      complete: () => {
        this.setData({
          loading: false
        });
      }
    });
  }
});
