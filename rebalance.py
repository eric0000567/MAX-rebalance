import ast
import math
from operator import inv
import os
from max.client import Client

class Rebalance:
    def __init__(self,key,screct,pair='usdttwd'):
        self.client = Client(key, screct)
        vip_level = self.client.get_private_vip_level()
        self.maker_fee = float(vip_level['current_vip_level']['maker_fee'])
        self.taker_fee = float(vip_level['current_vip_level']['taker_fee'])
        self.pair = pair
        self.initBal = 0 
        self.balance = {'USDT':0,'TWD':0}
        self.proportion = {'USDT':0,'TWD':0}
        self.newPro = {'USDT':0,'TWD':0}
        self.grade = 0.005
        self.rb_path = 'rebalance_parameter.txt'
        self.rb_exists()

    def rb_exists(self):
        if os.path.exists(self.rb_path):
            with open(self.rb_path) as f:
                self.initBal =  float(ast.literal_eval(f.readline()))
                self.balance = ast.literal_eval(f.readline())
                self.proportion =  ast.literal_eval(f.readline())
                self.newPro =  ast.literal_eval(f.readline())
                self.grade =  float(ast.literal_eval(f.readline()))
                self.pair =  ast.literal_eval(f.readline())

    def _record(self):
        with open(self.rb_path,'w') as f:
            f.write(str(self.initBal)+'\n')
            f.write(str(self.balance)+'\n')
            f.write(str(self.proportion)+'\n')
            f.write(str(self.newPro)+'\n')
            f.write(str(self.grade)+'\n')
            f.write('"'+str(self.pair)+'"\n')

    def get_assets_info(self):
        #get available balance
        ava_balance = {'USDT':self.client.get_private_account_balance('usdt')['balance'],
                    'TWD':self.client.get_private_account_balance('twd')['balance']}
        return ava_balance

    def createBal(self ,investment ,coinA_pro=0.5 ,coinB_pro=0.5, grade=0.005):
        sellPrice = float(self.client.get_public_all_tickers(self.pair)['sell'])
        if coinA_pro+coinB_pro != 1:
            print('幣種比例加總應等於100%')
            return False
        initUSDT = (investment*coinA_pro)/sellPrice
        self.balance['USDT'] = math.floor((initUSDT*0.9985)*100)/100
        self.balance['TWD'] = investment*coinB_pro
        self.proportion['USDT'] = coinA_pro
        self.proportion['TWD'] = coinB_pro
        self.grade = grade
        self.initBal = investment
        res = self.client.set_private_create_order(
            pair=self.pair,
            side='buy',
            amount=math.ceil(initUSDT*100)/100,
            price=sellPrice
        )
        print(res)
        self._record()
        return True

    def checking(self):
        lastPrice = float(self.client.get_public_all_tickers(pair=self.pair)['sell'])
        nowUSDTBalance = self.balance['USDT']*lastPrice
        interval = nowUSDTBalance/(nowUSDTBalance+self.balance['TWD'])
        self.newPro['USDT'] = interval
        self.newPro['TWD'] = self.balance['TWD']/(nowUSDTBalance+self.balance['TWD'])
        grade = interval-self.proportion['USDT']
        if (abs(grade)-self.taker_fee)>self.grade:
            print('over grade')
            side = 'sell' if grade>0 else 'buy'
            amount = self.balance['USDT']*abs(grade/2)
            amount = math.floor(amount*100)/100
            price = self.client.get_public_all_tickers(self.pair)
            if amount>=9:
                print('start rebalance..')
                try:
                    res = self.client.set_private_create_order(
                        pair=self.pair,
                        side=side,
                        amount=amount,
                        price=int(price['sell']) if side=='buy' else int(price['buy'])
                    )
                    self.balance['USDT'] = self.balance['USDT']-amount if grade>0 else self.balance['USDT']+amount-(amount*0.0015)
                    self.balance['TWD'] = self.balance['TWD']+((amount-(amount*0.0015))*lastPrice) if grade>0 else self.balance['TWD']-(amount*lastPrice)
                    print(res)
                except Exception as e:
                    print(str(e))

    def del_rb(self):
        price = self.client.get_public_all_tickers(self.pair)
        res = self.client.set_private_create_order(
                    pair=self.pair,
                    side='sell',
                    amount=self.balance['USDT']*(1-self.taker_fee),
                    price=price['buy']
                )
        print(res)
