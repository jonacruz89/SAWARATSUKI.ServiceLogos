# Replace Rider Startup Image

---

## Version 2024.1

---

- Open the `%userprofile%\AppData\Local\Programs\Rider\lib` folder
- Copy `app.jar` to an empty folder and make sure to back it up
- Create a new folder in this directory and move `app.jar` into it
- Go into this folder, right-click, choose `Open in Terminal`, and enter `jar -xvf app.jar` to extract. After extraction, delete `app.jar`
- Then go to the `rider\artwork\release` directory within this folder
- Rename the downloaded images to `splash.png` and `splash@2x.png` to replace the original images
- Return to the extracted folder, then run `jar -cfM0 ../app.jar ./` to compress the current folder, and save it to the parent directory
- Put the new `app.jar` into `%userprofile%\AppData\Local\Programs\Rider\lib` to replace the original
- Finally, delete all files in `%userprofile%\AppData\Local\JetBrains\Rider2024.1\splash`
