

class RouteB():
  # Bルート認証ID（東京電力パワーグリッドから郵送で送られてくるヤツ）
  account_id = ""
  # Bルート認証パスワード（東京電力パワーグリッドからメールで送られてくるヤツ）
  password = ""

class SerialPort():
  # シリアルポートデバイス名
  path = 'COM3'  # Windows の場合
  #path = '/dev/ttyUSB0'  # Linux(ラズパイなど）の場合
  #path = '/dev/cu.usbserial-A103BTPR'    # Mac の場合
  speed = 115200

class MySQL():
  host='127.0.0.1'
  user='smame'
  password='your identify'
  db='smame'
  charset='utf8'

class SSHTunnnel():
  server_address = "SERVER ADDRESS"
  server_port = 22
  ssh_host_key=None,
  ssh_pkey="private.key",
  ssh_username="USERNAME",
  ssh_password=None,
  remote_bind_address=("127.0.0.1", 3306)

class FireStore():
  certificate_json_file = "xxx.json"
