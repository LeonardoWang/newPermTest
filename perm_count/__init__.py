class Calculator():
    def __init__(self):
        self.Category = {'BO':'阅读','BR':'浏览器','BU':'商务', 'CO':'通讯','ED':'教育', 'FI' : '金融' ,'HE' : '健康' ,'IM' : '输入法' ,'LI' : '生活服务' ,'LO' : '定位' ,'NE' : '新闻' ,'MU' : '音乐','PE' : '个性化' ,'PH' : '相册' ,'SE' : '安全' ,'SH' : '购物' ,'SO' : '社交' ,'TO' : '工具' ,'VI' : '录像' ,'OT' : '其他', 'EN' : '娱乐','GA':'游戏'}
        self.Perm_list = { 'android.permission.READ_CONTACTS':1,
                            'android.permission.WRITE_CONTACTS':2,
                            'android.permission.GET_ACCOUNTS':3,
                            'android.permission.READ_CALENDAR':4,
                            'android.permission.WRITE_CALENDAR':5,
                            'android.permission.SEND_SMS':6,
                            'android.permission.RECEIVE_SMS':7,
                            'android.permission.READ_SMS':8,
                            'android.permission.RECEIVE_WAP_PUSH':9,
                            'android.permission.RECEIVE_MMS':10,
                            'android.permission.ACCESS_FINE_LOCATION':11,
                            'android.permission.ACCESS_COARSE_LOCATION':12,
                            'android.permission.READ_PHONE_STATE':13,
                            'android.permission.CALL_PHONE':14,
                            'android.permission.READ_CALL_LOG':15,
                            'android.permission.WRITE_CALL_LOG':16,
                            'com.android.voicemail.permission.ADD_VOICEMAIL':17,
                            'android.permission.USE_SIP':18,
                            'android.permission.PROCESS_OUTGOING_CALLS':19,
                            'android.permission.RECORD_AUDIO':20,
                            'android.permission.CAMERA':21,
                            'android.permission.BODY_SENSORS':22,
                            'android.permission.READ_EXTERNAL_STORAGE':23,
                            'android.permission.WRITE_EXTERNAL_STORAGE':24,
                            'android.permission.READ_PHONE_NUMBERS':25,
                            'android.permission.ANSWER_PHONE_CALLS':26}
        self.app_total = 1988586
        self.cate_count = {}
        self.perm_count = {}
        self.perm_percent = {}
        self.perm_cate_count = {}
        self.load_cate_count()
        self.load_perm_count()
        self.load_perm_cate_count()

    def load_cate_count(self):
        f = open('perm_count/cate_count')
        for lines in f.readlines():
            now_line = lines.strip().split(' ')
            self.cate_count[now_line[0]] = int(now_line[1])

    def load_perm_count(self):
        f = open('perm_count/perm_count')
        for lines in f.readlines():
            now_line = lines.strip().split(' ')
            self.perm_count[now_line[0]] = int(now_line[1])
            self.perm_percent[now_line[0]] = round(int(now_line[1])/self.app_total,4)

    def load_perm_cate_count(self):
        f = open('perm_count/perm_cate_count')
        for lines in f.readlines():
            now_line = lines.strip().split(' ')
            temp_list = self.perm_cate_count.get(now_line[0],{})

            temp_number = self.cate_count[now_line[1]]
            if temp_number == 0:
                temp_list[now_line[1]] = 0
            else:
                temp_list[now_line[1]] = round(int(now_line[2])/temp_number,4)
            self.perm_cate_count[now_line[0]] = temp_list
    def get_perm_id(self, perm):
        return self.Perm_list.get(perm, -1)

    def get_cate_count(self):
        return self.cate_count

    def get_perm_count(self):
        return self.perm_count

    def get_perm_cate_count(self):
        return self.perm_cate_count

    def get_perm_percent(self):
        return self.perm_percent

    def print_perm_cate_list(self, cate):
        for perm in self.Perm_list:
            if cate is not None:
                print(perm, self.perm_cate_count[perm].get(cate, 0))
            else:
                print(perm, self.perm_percent[perm])

