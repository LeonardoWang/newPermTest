class Calculator():
    def __init__(self):
        self.Category = {'BO':'阅读','BR':'浏览器','BU':'商务', 'CO':'通讯','ED':'教育', 'FI' : '金融' ,'HE' : '健康' ,'IM' : '输入法' ,'LI' : '生活服务' ,'LO' : '定位' ,'NE' : '新闻' ,'MU' : '音乐','PE' : '个性化' ,'PH' : '相册' ,'SE' : '安全' ,'SH' : '购物' ,'SO' : '社交' ,'TO' : '工具' ,'VI' : '录像' ,'OT' : '其他', 'EN' : '娱乐','GA':'游戏'}
        self.app_total = 1988586
        self.cate_count = {}
        self.perm_count = {}
        self.perm_cate_count = {}
        self.load_cate_count()
        self.load_perm_count()
        self.load_perm_cate_count()

    def load_cate_count(self):
        f = open('cate_count')
        for lines in f.readlines():
            now_line = lines.strip().split(' ')
            self.cate_count[now_line[0]] = int(now_line[1])

    def load_perm_count(self):
        f = open('perm_count')
        for lines in f.readlines():
            now_line = lines.strip().split(' ')
            self.perm_count[now_line[0]] = int(now_line[1])

    def load_perm_cate_count(self):
        f = open('perm_cate_count')
        for lines in f.readlines():
            now_line = lines.strip().split(' ')
            temp_list = self.perm_cate_count.get(now_line[0],{})

            temp_number = self.cate_count[now_line[1]]
            if temp_number == 0:
                temp_list[now_line[1]] = 0
            else:
                temp_list[now_line[1]] = round(int(now_line[2])/temp_number*100,2)/100
            self.perm_cate_count[now_line[0]] = temp_list

    def get_cate_count(self):
        return self.cate_count

    def get_perm_count(self):
        return self.perm_count

    def get_perm_cate_count(self):
        return self.perm_cate_count

a = Calculator()
print(a.get_perm_cate_count())