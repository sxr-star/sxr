Page({
  data: {
    loading: false,
    result: null
  },

  handleRegister() {
    if (this.data.loading) {
      return;
    }

    this.setData({
      loading: true,
      result: null
    });

    wx.request({
      url: 'http://127.0.0.1:8000/api/register/',
      method: 'POST',
      success: (res) => {
        this.setData({
          result: res.data
        });
      },
      fail: (err) => {
        this.setData({
          result: {
            success: false,
            message: '网络请求失败，请确保服务器正在运行'
          }
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
