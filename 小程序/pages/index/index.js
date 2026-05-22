Page({
  data: {
    // 登录页面数据
    isLoggedIn: false,
    loginPhone: '',
    code: '',
    loginPhoneError: '',
    codeError: '',
    loginLoading: false,
    loginResult: null,
    countdown: 0,
    sending: false,
    
    // 报到页面数据
    loading: false,
    result: null,
    name: '',
    studentId: '',
    phone: '',
    nameError: '',
    studentIdError: '',
    photoErrorFront: '',
    photoErrorBack: '',
    tempImagePathFront: '',
    tempImagePathBack: '',
    verifiedPhone: '',
    
    // 审核状态数据（4.0新增）
    currentTab: 'register',
    reviewStatus: null,
    reviewStatusDisplay: '',
    rejectReason: '',
    dormitoryNumber: '',
    statusLoading: false,
    statusError: ''
  },

  onLoad() {
    // 页面加载时检查登录状态
    this.checkLoginStatus();
  },

  onShow() {
    // 页面显示时从本地存储恢复图片路径
    const { tempImagePathFront, tempImagePathBack } = this.data;
    console.log('DEBUG onShow - tempImagePathFront:', tempImagePathFront);
    console.log('DEBUG onShow - tempImagePathBack:', tempImagePathBack);
    
    // 从本地存储恢复图片路径
    let needUpdate = false;
    let newFront = tempImagePathFront;
    let newBack = tempImagePathBack;
    
    try {
      const storedFront = wx.getStorageSync('tempImagePathFront');
      if (storedFront && !tempImagePathFront) {
        console.log('DEBUG: restoring tempImagePathFront from storage:', storedFront);
        newFront = storedFront;
        needUpdate = true;
      }
      const storedBack = wx.getStorageSync('tempImagePathBack');
      if (storedBack && !tempImagePathBack) {
        console.log('DEBUG: restoring tempImagePathBack from storage:', storedBack);
        newBack = storedBack;
        needUpdate = true;
      }
    } catch (e) {
      console.log('DEBUG: getStorageSync failed', e);
    }
    
    if (needUpdate) {
      this.setData({
        tempImagePathFront: newFront,
        tempImagePathBack: newBack,
        photoErrorFront: '',
        photoErrorBack: ''
      });
    } else {
      // 如果图片路径存在但验证仍然失败，尝试重新设置
      if (tempImagePathFront) {
        this.setData({ photoErrorFront: '' });
      }
      if (tempImagePathBack) {
        this.setData({ photoErrorBack: '' });
      }
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    wx.request({
      url: 'http://127.0.0.1:8000/api/check_login/',
      method: 'GET',
      success: (res) => {
        if (res.data.is_logged_in) {
          this.setData({
            isLoggedIn: true,
            phone: res.data.phone,
            verifiedPhone: res.data.phone
          });
        }
      }
    });
  },

  // 登录页面输入处理
  onLoginPhoneInput(e) {
    this.setData({
      loginPhone: e.detail.value,
      loginPhoneError: ''
    });
  },

  onCodeInput(e) {
    this.setData({
      code: e.detail.value,
      codeError: ''
    });
  },

  // 发送验证码
  handleSendCode() {
    if (this.data.countdown > 0 || this.data.sending) return;

    const phone = this.data.loginPhone.trim();
    
    if (!phone || phone.length !== 11) {
      this.setData({ loginPhoneError: '请输入正确的手机号' });
      return;
    }

    this.setData({ sending: true });

    wx.request({
      url: 'http://127.0.0.1:8000/api/send_code/',
      method: 'POST',
      data: { phone: phone },
      success: (res) => {
        if (res.data.success) {
          this.startCountdown();
          wx.showToast({
            title: '验证码已发送',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.message,
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'error'
        });
      },
      complete: () => {
        this.setData({ sending: false });
      }
    });
  },

  // 倒计时
  startCountdown() {
    let countdown = 60;
    this.setData({ countdown });
    
    const timer = setInterval(() => {
      countdown--;
      if (countdown <= 0) {
        clearInterval(timer);
        this.setData({ countdown: 0 });
      } else {
        this.setData({ countdown });
      }
    }, 1000);
  },

  // 登录
  handleLogin() {
    if (this.data.loginLoading) return;

    this.clearLoginErrors();

    const phone = this.data.loginPhone.trim();
    const code = this.data.code.trim();

    let hasError = false;

    if (!phone || phone.length !== 11) {
      this.setData({ loginPhoneError: '请输入正确的手机号' });
      hasError = true;
    }

    if (!code) {
      this.setData({ codeError: '验证码不能为空' });
      hasError = true;
    }

    if (hasError) return;

    this.setData({ loginLoading: true, loginResult: null });

    wx.request({
      url: 'http://127.0.0.1:8000/api/verify_code/',
      method: 'POST',
      data: {
        phone: phone,
        code: code
      },
      success: (res) => {
        if (res.data.success) {
          // 清除之前的图片数据（避免显示上一次的照片）
          try {
            wx.removeStorageSync('tempImagePathFront');
            wx.removeStorageSync('tempImagePathBack');
          } catch (e) {
            console.log('DEBUG: removeStorageSync failed', e);
          }
          
          this.setData({
            isLoggedIn: true,
            phone: phone,
            verifiedPhone: phone,
            loginResult: { success: true, message: '登录成功' },
            tempImagePathFront: '',
            tempImagePathBack: ''
          });
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          });
        } else {
          this.setData({
            loginResult: { success: false, message: res.data.message }
          });
          wx.showToast({
            title: res.data.message,
            icon: 'none'
          });
        }
      },
      fail: () => {
        this.setData({
          loginResult: { success: false, message: '网络请求失败' }
        });
        wx.showToast({
          title: '网络请求失败',
          icon: 'error'
        });
      },
      complete: () => {
        this.setData({ loginLoading: false });
      }
    });
  },

  // 退出登录
  handleLogout() {
    wx.request({
      url: 'http://127.0.0.1:8000/api/logout/',
      method: 'GET',
      success: () => {
        this.setData({
          isLoggedIn: false,
          loginPhone: '',
          code: '',
          phone: '',
          verifiedPhone: '',
          name: '',
          studentId: '',
          tempImagePath: ''
        });
        wx.showToast({
          title: '已退出登录',
          icon: 'success'
        });
      }
    });
  },

  // 报到页面输入处理
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

  // 计算文件的MD5哈希值
  getFileMD5(filePath) {
    return new Promise((resolve, reject) => {
      wx.getFileSystemManager().readFile({
        filePath: filePath,
        success: (res) => {
          const arrayBuffer = res.data;
          const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
          const hash = CryptoJS.MD5(wordArray).toString();
          resolve(hash);
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  },

  // 检查两张图片是否为同一张
  async checkImagesNotSame() {
    const { tempImagePathFront, tempImagePathBack } = this.data;
    
    if (tempImagePathFront && tempImagePathBack) {
      try {
        const md5Front = await this.getFileMD5(tempImagePathFront);
        const md5Back = await this.getFileMD5(tempImagePathBack);
        
        if (md5Front === md5Back) {
          this.setData({ 
            photoErrorBack: '身份证正面和反面不能上传同一张图片',
            photoErrorFront: '身份证正面和反面不能上传同一张图片'
          });
          return false;
        }
      } catch (err) {
        console.error('MD5计算失败', err);
      }
    }
    return true;
  },

  // 选择正面图片
  chooseImageFront() {
    const that = this;
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths[0];
        console.log('========================================');
        console.log('DEBUG chooseImageFront success:', filePath);
        console.log('filePath type:', typeof filePath);
        console.log('filePath length:', filePath ? filePath.length : 0);
        console.log('========================================');
        
        // 保存到本地存储
        try {
          wx.setStorageSync('tempImagePathFront', filePath);
          console.log('DEBUG setStorageSync tempImagePathFront: SUCCESS');
          // 验证存储是否成功
          const stored = wx.getStorageSync('tempImagePathFront');
          console.log('DEBUG verify storage after set:', stored);
        } catch (e) {
          console.log('DEBUG: setStorageSync failed', e);
        }
        
        // 使用Promise确保setData完成
        new Promise((resolve) => {
          that.setData({
            tempImagePathFront: filePath,
            photoErrorFront: ''
          }, resolve);
        }).then(() => {
          console.log('DEBUG after setData - tempImagePathFront:', that.data.tempImagePathFront);
          // 检查是否为同一张图片
          that.checkImagesNotSame();
        });
      },
      fail: (err) => {
        console.log('DEBUG chooseImageFront fail:', err);
      }
    });
  },

  // 选择反面图片
  chooseImageBack() {
    const that = this;
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths[0];
        console.log('========================================');
        console.log('DEBUG chooseImageBack success:', filePath);
        console.log('filePath type:', typeof filePath);
        console.log('filePath length:', filePath ? filePath.length : 0);
        console.log('========================================');
        
        // 保存到本地存储
        try {
          wx.setStorageSync('tempImagePathBack', filePath);
          console.log('DEBUG setStorageSync tempImagePathBack: SUCCESS');
          // 验证存储是否成功
          const stored = wx.getStorageSync('tempImagePathBack');
          console.log('DEBUG verify storage after set:', stored);
        } catch (e) {
          console.log('DEBUG: setStorageSync failed', e);
        }
        
        // 使用Promise确保setData完成
        new Promise((resolve) => {
          that.setData({
            tempImagePathBack: filePath,
            photoErrorBack: ''
          }, resolve);
        }).then(() => {
          console.log('DEBUG after setData - tempImagePathBack:', that.data.tempImagePathBack);
          // 检查是否为同一张图片
          that.checkImagesNotSame();
        });
      },
      fail: (err) => {
        console.log('DEBUG chooseImageBack fail:', err);
      }
    });
  },

  // 清除登录错误
  clearLoginErrors() {
    this.setData({
      loginPhoneError: '',
      codeError: ''
    });
  },

  // 清除报到错误
  clearErrors() {
    this.setData({
      nameError: '',
      studentIdError: '',
      photoErrorFront: '',
      photoErrorBack: ''
    });
  },

  // 检查文件是否存在
  fileExists(filePath) {
    return new Promise((resolve) => {
      wx.getFileSystemManager().access({
        path: filePath,
        success: () => resolve(true),
        fail: () => resolve(false)
      });
    });
  },

  // 验证表单
  async validateForm() {
    let { name, studentId } = this.data;
    let isValid = true;

    console.log('========================================');
    console.log('DEBUG validateForm START');
    console.log('========================================');
    
    // 直接从存储中获取图片路径（不依赖data）
    let tempImagePathFront = '';
    let tempImagePathBack = '';
    try {
      tempImagePathFront = wx.getStorageSync('tempImagePathFront') || '';
      tempImagePathBack = wx.getStorageSync('tempImagePathBack') || '';
    } catch (e) {
      console.log('DEBUG: getStorageSync failed', e);
    }

    console.log('DEBUG validateForm:', {
      name: !!name,
      studentId: !!studentId,
      tempImagePathFront: tempImagePathFront,
      tempImagePathFront_type: typeof tempImagePathFront,
      tempImagePathFront_length: tempImagePathFront ? tempImagePathFront.length : 0,
      tempImagePathBack: tempImagePathBack,
      tempImagePathBack_type: typeof tempImagePathBack,
      tempImagePathBack_length: tempImagePathBack ? tempImagePathBack.length : 0
    });
    console.log('========================================');

    this.clearErrors();

    if (!name) {
      this.setData({ nameError: '姓名不能为空' });
      isValid = false;
    }

    if (!studentId) {
      this.setData({ studentIdError: '学号不能为空' });
      isValid = false;
    }

    // 检查正面照片
    if (!tempImagePathFront) {
      console.log('DEBUG: tempImagePathFront is empty');
      this.setData({ photoErrorFront: '请上传身份证正面照片' });
      isValid = false;
    } else {
      const frontExists = await this.fileExists(tempImagePathFront);
      if (!frontExists) {
        console.log('DEBUG: tempImagePathFront file not exists');
        this.setData({ photoErrorFront: '正面照片文件不存在，请重新上传' });
        isValid = false;
      }
    }

    // 检查反面照片
    if (!tempImagePathBack) {
      console.log('DEBUG: tempImagePathBack is empty');
      this.setData({ photoErrorBack: '请上传身份证反面照片' });
      isValid = false;
    } else {
      const backExists = await this.fileExists(tempImagePathBack);
      if (!backExists) {
        console.log('DEBUG: tempImagePathBack file not exists');
        this.setData({ photoErrorBack: '反面照片文件不存在，请重新上传' });
        isValid = false;
      }
    }

    return isValid;
  },

  // 文件转base64
  fileToBase64(filePath) {
    return new Promise((resolve, reject) => {
      wx.getFileSystemManager().readFile({
        filePath: filePath,
        encoding: 'base64',
        success: (res) => {
          resolve(res.data);
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  },

  // 提交报到
  async handleRegister() {
    if (this.data.loading) return;

    if (!(await this.validateForm())) return;

    // 前端检查是否为同一张图片
    if (this.data.photoErrorFront || this.data.photoErrorBack) {
      wx.showToast({
        title: '请上传不同的身份证照片',
        icon: 'none'
      });
      return;
    }

    this.setData({
      loading: true,
      result: null
    });

    wx.showLoading({
      title: '正在提交...',
      mask: true
    });

    const { name, studentId } = this.data;
    
    // 从存储中获取图片路径
    let tempImagePathFront = '';
    let tempImagePathBack = '';
    try {
      tempImagePathFront = wx.getStorageSync('tempImagePathFront') || '';
      tempImagePathBack = wx.getStorageSync('tempImagePathBack') || '';
    } catch (e) {
      console.log('DEBUG: getStorageSync failed', e);
    }

    const verifiedPhone = this.data.verifiedPhone;
    if (!verifiedPhone) {
      wx.hideLoading();
      this.setData({ loading: false });
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    // 将两张照片转为base64
    let frontBase64 = '';
    let backBase64 = '';
    try {
      frontBase64 = await this.fileToBase64(tempImagePathFront);
      backBase64 = await this.fileToBase64(tempImagePathBack);
    } catch (e) {
      wx.hideLoading();
      this.setData({ loading: false });
      wx.showToast({ title: '照片处理失败', icon: 'none' });
      return;
    }

    // 一次性上传两张照片（使用base64）
    wx.request({
      url: 'http://127.0.0.1:8000/api/register_with_info_v3/',
      method: 'POST',
      data: {
        name: name,
        student_id: studentId,
        verified_phone: verifiedPhone,
        id_card_photo_front_base64: frontBase64,
        id_card_photo_back_base64: backBase64
      },
      success: (res) => {
        wx.hideLoading();
        const data = res.data || { success: false, message: '服务器响应失败' };
        if (data.success) {
          // 报到成功，清除存储的图片路径
          try {
            wx.removeStorageSync('tempImagePathFront');
            wx.removeStorageSync('tempImagePathBack');
          } catch (e) {}
          this.setData({
            name: '',
            studentId: '',
            tempImagePathFront: '',
            tempImagePathBack: '',
            result: data
          });
          wx.showToast({ title: '报到成功', icon: 'success' });
        } else {
          this.setData({ result: data });
          wx.showToast({ title: data.message || '提交失败', icon: 'none', duration: 3000 });
        }
        this.setData({ loading: false });
      },
      fail: (err) => {
        console.error('上传失败', err);
        wx.hideLoading();
        this.setData({ loading: false });
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      }
    });
  },

  // 切换标签页（4.0新增）
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ currentTab: tab });
    if (tab === 'status') {
      this.fetchReviewStatus();
    }
  },

  // 查询审核状态（4.0新增）
  fetchReviewStatus() {
    this.setData({
      statusLoading: true,
      statusError: '',
      reviewStatus: null
    });

    wx.request({
      url: 'http://127.0.0.1:8000/api/review_status/',
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          const reviewStatus = res.data.data.review_status;
          this.setData({
            reviewStatus: reviewStatus,
            reviewStatusDisplay: res.data.data.review_status_display,
            rejectReason: res.data.data.reject_reason || '',
            dormitoryNumber: res.data.data.dormitory_number || ''
          });
          // 审核通过，跳转到宿舍管理页面
          if (reviewStatus === 'approved') {
            wx.navigateTo({
              url: '/pages/dormitory/index'
            });
          }
        } else {
          this.setData({
            statusError: res.data.message
          });
        }
      },
      fail: () => {
        this.setData({
          statusError: '网络请求失败'
        });
      },
      complete: () => {
        this.setData({ statusLoading: false });
      }
    });
  }
});