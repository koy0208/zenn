CREATE USER postgres WITH PASSWORD 'postgres'; -- ユーザー作成
CREATE DATABASE jaffleshop;-- DB作成
GRANT ALL PRIVILEGES ON DATABASE jaffleshop TO postgres; -- 権限付与