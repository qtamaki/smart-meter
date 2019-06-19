# スマートメーターから瞬間消費電力と積算消費電力を取得

スマートメーターから、電力情報を受け取り、MySQLに登録します。

## セットアップ

### pythonのインストール

3.7.x系で試しています。2.7.xでは動きません。OSに合わせて適当に入れてください。

### パッケージインストール

firebase-adminは必須ではありません。使っていないので。

```
pip install --upgrade firebase-admin sshtunnel pymysql pyserial
```

### DBの準備

MySQLにDBを作成する。

```
create database smame charset = 'utf8mb4';
grant all on smame.* to 'smame'@'localhost' identified by 'your identify';
grant all on smame.* to 'smame' identified by 'your identify';
```

テーブルを準備する。

```
create table meter_logs (
  id serial primary key,
  meter_no int not null default 0,
  created_at datetime not null,
  watt double not null default 0,
  accum_watt double not null default 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

create index idx_meter_logs_1 meter_logs(created_at);
```

## 接続キーの準備

* settings.py に下記の情報を設定する
  * 各電力会社のBルートサービスに申し込み、IDとパスワードを取得し設定
  * MySQLサーバーにSSHトンネリング経由で接続するので、ssh-keyを生成しプライベートキーへのパスを設定
  * FireStoreを利用する場合は、FireStoreのCertificateファイルをダンロードしてパスを設定

## USBドングルの準備

* RL7023 Stick-D/IPS を使用している
* パソコン(windowsとかMacとか)に接続し、シリアルポートの名称・パスを取得する(settings.pyに書いてあるどれかで行けるはず)

## 起動

```
python start.py
```
