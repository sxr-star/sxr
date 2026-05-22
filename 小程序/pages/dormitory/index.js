Page({
  data: {
    loading: false,
    error: '',
    dormitoryInfo: null,
    roommates: []
  },

  onLoad() {
    this.fetchDormitoryInfo();
  },

  onShow() {
    // 每次显示页面时刷新宿舍信息
    this.fetchDormitoryInfo();
  },

  // 查询宿舍信息
  fetchDormitoryInfo() {
    this.setData({
      loading: true,
      error: '',
      dormitoryInfo: null,
      roommates: []
    });

    wx.request({
      url: 'http://127.0.0.1:8000/api/dormitory_info/',
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          this.setData({
            dormitoryInfo: res.data.data.dormitory,
            roommates: res.data.data.roommates
          });
        } else {
          this.setData({
            error: res.data.message
          });
        }
      },
      fail: () => {
        this.setData({
          error: '网络请求失败'
        });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  // 返回报到页
  goBack() {
    wx.navigateBack({
      delta: 1,
      fail: () => {
        // 如果没有上一页，跳转到报到页
        wx.redirectTo({
          url: '/pages/index/index'
        });
      }
    });
  }
});
