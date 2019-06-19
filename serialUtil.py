# -*- coding: utf-8 -*-

import sys
import time
import datetime

# シリアルポート通信制御用のクラス
class SerialUtil():
  def __init__(self, serial, store):
    self.ser = serial
    self.store = store

  # ポートへの書き込み raw: bytes
  def writeb(self, raw):
    return self.ser.write(raw)

  # ポートへの書き込み cmd: 文字列
  # 文字列をバイト列に変換し、末尾に改行を付ける
  def write(self, cmd):
    return self.ser.write((cmd+"\r\n").encode())

  # ポートから1行読む
  def read(self):
    return self.ser.readline().decode()

  # 0.1秒待ちながらバッファが無くなるまで読む(読んだ結果は画面に表示)
  def readWhile(self):
    time.sleep(0.1)
    while self.ser.in_waiting > 0 :
      print("read: "+self.read(), end="")
      time.sleep(0.1)

  # シリアルポートにコマンド送信
  # その後、エコーバックと結果を画面に表示
  def command(self, cmd):
    print("command: " + cmd)
    self.write(cmd)
    print("echo: "+self.read(), end="") # エコーバック
    time.sleep(0.1)
    while self.ser.in_waiting > 0 :
      print("back: "+self.read(), end="")
      time.sleep(0.1)

  # コマンドを送信し、結果を文字列で得る
  def func(self, cmd):
    print("func: " + cmd)
    self.write(cmd)
    print("echo: "+self.read(), end="") # エコーバック
    time.sleep(0.1)
    return self.read()

  # スマートメーターを探す処理
  def scan(self):
    print("scan")
    scanDuration = 4;   # スキャン時間。サンプルでは6なんだけど、4でも行けるので。（ダメなら増やして再試行）
    scanRes = {} # スキャン結果の入れ物

    # スキャンのリトライループ（何か見つかるまで）
    while "Channel" not in scanRes :
      # アクティブスキャン（IE あり）を行う
      # 時間かかります。10秒ぐらい？
      self.write("SKSCAN 2 FFFFFFFF " + str(scanDuration))

      # スキャン1回について、スキャン終了までのループ
      scanEnd = False
      while not scanEnd :
        line = self.read()
        print("read: "+line, end="")

        if line.startswith("EVENT 22") :
          # スキャン終わったよ（見つかったかどうかは関係なく）
          scanEnd = True
        elif line.startswith("  ") :
          # スキャンして見つかったらスペース2個あけてデータがやってくる
          # 例
          #  Channel:39
          #  Channel Page:09
          #  Pan ID:FFFF
          #  Addr:FFFFFFFFFFFFFFFF
          #  LQI:A7
          #  PairID:FFFFFFFF
          cols = line.strip().split(':')
          scanRes[cols[0]] = cols[1]
      scanDuration+=1

      if 7 < scanDuration and  "Channel" not in scanRes:
        # 引数としては14まで指定できるが、7で失敗したらそれ以上は無駄っぽい
        print("err: スキャンリトライオーバー")
        sys.exit(1)  # エラー終了
    return scanRes

  # スマートメーターとの接続待ち
  def waitToConnect(self):
    while True :
      line = self.read()
      print("wait: "+line, end="")
      if line.startswith("EVENT 24") :
        print("err: PANA 接続失敗")
        sys.exit(1)  # エラー終了
      elif line.startswith("EVENT 25") :
        # 接続完了！
        return

  # 電力情報取得メイン処理
  def observeWatt(self, ipv6Addr):
    cnt = 0
    while True:
      cnt+=1
      print("count: {0}".format(cnt))
      # ECHONET Lite フレーム作成
      # 　参考資料
      # 　・ECHONET-Lite_Ver.1.12_02.pdf (以下 EL)
      # 　・Appendix_H.pdf (以下 AppH)
      echonetLiteFrame = b""
      echonetLiteFrame += b"\x10\x81"      # EHD (参考:EL p.3-2)
      echonetLiteFrame += b"\x00\x01"      # TID (参考:EL p.3-3)
      # ここから EDATA
      echonetLiteFrame += b"\x05\xFF\x01"  # SEOJ (参考:EL p.3-3 AppH 「３．６ 管理・操作関連機器クラスグループ 」)
      echonetLiteFrame += b"\x02\x88\x01"  # DEOJ (参考:EL p.3-3 AppH 「３．３．２５ 低圧スマート電力量メータクラス規定」)
      echonetLiteFrame += b"\x62"          # ESV(62:プロパティ値読み出し要求) (参考:EL p.3-5)
      echonetLiteFrame += b"\x03"          # OPC(1個)(参考:EL p.3-7)
      echonetLiteFrame += b"\xE0"          # E0: 積算電力量
      echonetLiteFrame += b"\x00"          #
      echonetLiteFrame += b"\xE1"          # E1: 積算電力量の単位
      echonetLiteFrame += b"\x00"          #
      echonetLiteFrame += b"\xE7"          # E7: 瞬間電力量計測値
      echonetLiteFrame += b"\x00"          #

      # コマンド送信
      command = b"SKSENDTO 1 "+ipv6Addr.encode()+b" 0E1A 1 "+format(len(echonetLiteFrame),"04X").encode()+b" " + echonetLiteFrame
      print("command: {0}".format(command))
      self.writeb(command)

      waitTime = 0
      while True:
        time.sleep(0.1)
        if self.ser.in_waiting == 0 : # データが来てなかったら1秒待つ
          waitTime += 1
          if waitTime > 10:
            print("timeout!! " + str(waitTime))
            break
          print("wait.. " + str(waitTime))
          time.sleep(1)
          continue
        print("read..")
        line = self.read()
        waitTime = 0
        print("read: " + line, end="")

        # 受信データはたまに違うデータが来たり、
        # 取りこぼしたりして変なデータを拾うことがあるので
        # チェックを厳しめにしてます。
        if line.startswith("ERXUDP") :
          print("ERXUDP")
          cols = line.strip().split(' ')
          res = cols[8]   # UDP受信データ部分
          #tid = res[4:4+4];
          seoj = res[8:8+6]
          #deoj = res[14,14+6]
          ESV = res[20:20+2]
          #OPC = res[22,22+2]
          if seoj == "028801" and ESV == "72" :
            # スマートメーター(028801)から来た応答(72)なら
            EPC = res[24:24+2]
            # 先頭内容が積算電力量(E0)だったら
            if EPC == "E0" :
              pwMul = int(res[40:42], 16) # 位置取りコード
              pwTotal = round(int(res[28:36], 16) * self.multi(pwMul), 1) # 積算消費電力量
              pw = int(res[46:54], 16) # 瞬間消費電力量
              print(u"計測値:{0}[W], {1}[kW], {2}".format(pw, pwTotal, pwMul))
              self.store.store(datetime.datetime.now(), pw, pwTotal)
          break
      time.sleep(10) # 10秒

  # 積算消費電力量の倍率を返す
  def multi(self, x):
    if x == 0:
      return 1
    if x == 1:
      return 0.1
    if x == 2:
      return 0.01
    if x == 3:
      return 0.001
    if x == 4:
      return 0.0001
    if x == 10:
      return 10
    if x == 11:
      return 100
    if x == 12:
      return 1000
    if x == 13:
      return 10000
    print("err: 不明な係数" + x)
    sys.exit(1) 

