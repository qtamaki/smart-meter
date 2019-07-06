#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install pyserial

from __future__ import print_function

import sys
import serial
import time

import serialUtil
import MySQLStore
import settings

# シリアルポート初期化
ser = serial.Serial(settings.SerialPort.path, 115200)

# 保存先の選択
#store = firestore.StoreUtil()
store = MySQLStore.MySQLStoreUtil() #firestore.StoreUtil()
try:
  util = serialUtil.SerialUtil(ser, store)

  # とりあえずバージョンを取得してみる（やらなくてもおｋ）
  util.command("SKVER")

  # Bルート認証パスワード設定
  util.command("SKSETPWD C " + settings.RouteB.password)

  # Bルート認証ID設定
  util.command("SKSETRBID " + settings.RouteB.account_id)

  # SKSCANを掛ける
  scanRes = util.scan()

  # スキャン結果からChannelを設定。
  util.command("SKSREG S2 " + scanRes["Channel"])

  # スキャン結果からPan IDを設定
  util.command("SKSREG S3 " + scanRes["Pan ID"])

  # MACアドレス(64bit)をIPV6リンクローカルアドレスに変換。
  # (BP35A1の機能を使って変換しているけど、単に文字列変換すればいいのではという話も？？)
  ipv6Addr = util.func("SKLL64 " + scanRes["Addr"]).strip()
  print(ipv6Addr)

  # PANA 接続シーケンスを開始します。
  util.command("SKJOIN " + ipv6Addr)

  # PANA 接続完了待ち（10行ぐらいなんか返してくる）
  util.waitToConnect()

  # これ以降、シリアル通信のタイムアウトを設定
  ser.timeout = 2

  # スマートメーターがインスタンスリスト通知を投げてくる
  # (ECHONET-Lite_Ver.1.12_02.pdf p.4-16)
  #print(ser.readline(), end="") #無視
  util.readWhile() # 読み捨てる

  util.observeWatt(ipv6Addr)

finally:
  store.close()
  ser.close()
