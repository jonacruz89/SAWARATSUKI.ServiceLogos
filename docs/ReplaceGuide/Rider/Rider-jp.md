# Rider のスタートアップ画像の交換

---

## 2024.1 バージョン

---

- `%userprofile%\AppData\Local\Programs\Rider\lib` フォルダを開く
- `app.jar` を空のフォルダにコピーし、バックアップを取る
- 同じディレクトリに新しいフォルダを作成し、`app.jar` を移動する
- このフォルダに入り、右クリックして「ターミナルで開く」を選択し、`jar -xvf app.jar` と入力して解凍する。解凍後、`app.jar` を削除する
- このフォルダ内の `rider\artwork\release` ディレクトリに移動
- ダウンロードした画像を `splash.png` と `splash@2x.png` にリネームして、元の画像を置き換える
- 解凍されたフォルダに戻り、`jar -cfM0 ../app.jar ./` を実行して、現在のフォルダを圧縮し、上のディレクトリに保存する
- 新しい `app.jar` を `%userprofile%\AppData\Local\Programs\Rider\lib` に配置して、元のファイルと交換する
- 最後に、`%userprofile%\AppData\Local\JetBrains\Rider2024.1\splash` のすべてのファイルを削除する
