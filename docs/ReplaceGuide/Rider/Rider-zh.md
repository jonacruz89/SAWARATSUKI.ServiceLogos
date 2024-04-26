# 替换 Rider 启动图片

---

## 2024.1 版本

---

- 打开 `%userprofile%\AppData\Local\Programs\Rider\lib` 文件夹
- 将 `app.jar` 复制到一个空的文件夹，并注意备份该文件
- 在此目录下再创建一个新的文件夹,并将 `app.jar` 移动进去
- 进入此文件夹,右键选择 `在终端中打开` ，输入 `jar -xvf app.jar` 解压,解压完后删除 `app.jar`
- 然后进入此文件夹中的 `rider\artwork\release` 目录
- 将下载好的图片重命名为 `splash.png` 和 `splash@2x.png` 替换原来的图片
- 回到解压后的目录,通过终端执行 `jar -cfM0 ../app.jar ./` 来压缩当前目录,并将结果保存到上层目录
- 将新的 `app.jar` 放到 `%userprofile%\AppData\Local\Programs\Rider\lib` 进行替换
- 最后将 `%userprofile%\AppData\Local\JetBrains\Rider2024.1\splash` 内的文件全部删除
