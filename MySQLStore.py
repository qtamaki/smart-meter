# -*- coding: utf-8 -*-

# pip install sshtunnel
# pip install pymysql

from sshtunnel import SSHTunnelForwarder
# モジュール読み込み
import pymysql.cursors
import settings

class MySQLStoreUtil():
  def __init__(self):
    # SSHトンネリングで接続する設定(直接接続するなら不要)
    self.server = SSHTunnelForwarder(
      (settings.SSHTunnnel.server_address, settings.SSHTunnnel.server_port),
      #ssh_host_key=settings.SSHTunnnel.ssh_host_key,
      ssh_host_key=None,
      ssh_pkey=settings.SSHTunnnel.ssh_pkey,
      ssh_username=settings.SSHTunnnel.ssh_username,
      ssh_password=settings.SSHTunnnel.ssh_password,
      remote_bind_address=("127.0.0.1", 3306)
    )
    self.server.start()
    # MySQLに接続する
    self.conn = pymysql.connect(host=settings.MySQL.host,
                                port=self.server.local_bind_port,
                                user=settings.MySQL.user,
                                password=settings.MySQL.password,
                                db=settings.MySQL.db,
                                charset=settings.MySQL.charset,
                                cursorclass=pymysql.cursors.DictCursor)

  def store(self, dt, watt, accumWatt):
    # select
    # SQLを実行する
    cursor = self.conn.cursor()
    try:
      sql = "insert into meter_logs (meter_no, created_at, watt, accum_watt)values(%s,%s,%s,%s)"
      cursor.execute(sql, (1, dt, watt, accumWatt))
      self.conn.commit()
    except Exception as e:
      self.conn.rollback()
      raise e
    finally:
      cursor.close()

  def close(self):
    # MySQLから切断する
    self.conn.close()
    self.server.stop()
