from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import *
import multiprocessing as mp
from rebalance import Rebalance


class Createpage(object): # 狀態總覽
    def __init__(self, master=None,key='',screct=''):
        self.root = master
        self.root.geometry('%dx%d' % (800, 600))
        self.rb = Rebalance(key,screct)
        self.USDTpro = StringVar()
        self.TWDpro = StringVar()
        self.investment = StringVar()
        self.grade = StringVar()
        self.sellSelf = StringVar()
        self.selloption = ["不做任何動作", "賣出持倉"]
        self.sellSelf.set(self.selloption[0])
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root) #建立Frame
        self.page.pack()
        Label(self.page).grid(row=0, stick=W)
        Label(self.page, text = '當前資產狀態').grid(row=0, column=0,columnspan=2, stick=EW, pady=10)
        self.balance = Label(self.page, text = '...')
        self.balance.grid(row=1,columnspan=2, stick=EW, pady=5)
        
        Label(self.page, text = 'USDT 比例 (%)').grid(row=4, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.USDTpro).grid(row=4, column=1, stick=W, pady=5)
        Label(self.page, text = 'TWD 比例 (%)').grid(row=5, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.TWDpro).grid(row=5, column=1, stick=W, pady=5)
        Label(self.page, text = '相差多少後再平衡 (%)').grid(row=6, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.grade).grid(row=6, column=1, stick=W, pady=5)
        
        Label(self.page, text = '開單金額：').grid(row=7, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.investment).grid(row=10, column=1, stick=W, pady=5)

        Button(self.page, text='創建屯幣寶', command=self.create_rb).grid(row=11, column=1, stick=E)

        self.msg = ''
        self.st = ScrolledText(self.page,height=10)
        self.st.grid(row=13, columnspan=2, stick=W, pady=5)

        OptionMenu(self.page, self.sellSelf, *self.selloption).grid(row=14, column=1, sticky=EW)
        Button(self.page, text='關閉屯幣寶', command=self.del_rb).grid(row=14, column=1, stick=E)
        initBalance = self.rb.get_assets_info()
        self.balance['text'] = 'TWD: {} \n USDT: {}'.format(str(initBalance['TWD']),str(initBalance['USDT']))

        if self.rb.balance['USDT'] != 0:
            res = askyesno(title = '詢問',message='您有尚未關閉的屯幣寶，是否繼續使用？')
            if res :
                self.checking()
            else:
                cancelPre = askyesno(title = '詢問',message='是否賣出上次屯幣寶購買的餘額？')
                if cancelPre:
                    self.rb.del_rb()


    def create_rb(self):
        investment = float(self.investment.get())
        if investment<1000:
            showinfo(title='警告', message='開單金額需大於 1000 TWD')
            return
        self.msg += '創建中..請稍後..\n\n'
        self.printInfo()
        res = self.rb.createBal(investment ,float(self.USDTpro.get())/100 ,float(self.TWDpro.get())/100 ,float(self.grade.get())/100)
        if not res:
            showinfo(title='警告', message='兩種幣種總和應等於100%！！')
            return

        self.msg+= '創建完成!\n'
        self.printInfo()
        self.checking()

    def checking(self):
        initBalance = self.rb.get_assets_info()
        self.balance['text'] = 'TWD: {} \n USDT: {}'.format(str(initBalance['TWD']),str(initBalance['USDT']))
        self.msg = '\n屯幣寶進行中..\n\n'
        self.rb.checking()
        self.msg += '初始投資額 {} \n'.format(self.rb.initBal)
        self.msg += '初始比例： USDT {}% ,TWD {}%\n'.format(round((self.rb.proportion['USDT']*100),2),round((self.rb.proportion['TWD']*100),2))
        self.msg += '差多少再平衡： {}% \n'.format(round((self.rb.grade*100),2))
        self.msg += '上次USDT成交價： {} \n'.format(self.rb.initPrice)
        self.msg += '當前比例： USDT {}% ,TWD {}%\n'.format(round((self.rb.newPro['USDT']*100),2),round((self.rb.newPro['TWD']*100),2))
        self.msg += '當前資產狀態： {} USDT ,{} TWD\n'.format(round((self.rb.balance['USDT']),2),round((self.rb.balance['TWD']),2))

        self.printInfo()
        self.page.after(30000,self.checking)

    def del_rb(self):
        res = askyesno(title = '詢問',message='確定要關閉屯幣寶？')
        if res :
            try:
                if self.sellSelf.get() == self.selloption[0]:
                    self.msg = '已關閉屯幣寶，請手動賣出USDT'
                elif self.sellSelf.get() == self.selloption[1]:
                    self.rb.del_rb()
                    self.msg = '已關閉屯幣寶，已自動賣出USDT'
                self.printInfo()
                self.page.quit()
            except Exception as e:
                self.msg+= 'Error:'+str(e)+'\n(API請求失敗，請確認下單參數及餘額)'

    def printInfo(self):
        self.st['state'] = 'normal'	
        self.st.delete('0.0','end')
        self.st.insert('end',str(self.msg)+'\n')
        self.st.update()
        # self.page.after(1000,self.printInfo)
        self.msg = ''
        self.st['state'] = 'disabled'	

