# Text into image

Under construction!  Currently experimenting and planning!

Developed by Hayk Sardaryan (c) 2021

## Examples of How To Use (Buggy Alpha Version)


```python
from Timage import Text2Image

T = Text2Image()
```
create image and text file ex. "img.jpg" and "abc.txt" 
```python
T.code('abc.txt', 'img.jpg')
```

You will receive: s_img.png file, it's a coded image

For decode you can use
```python
T.decode('s_im.png',secret_filename='secret.txt', max_char=2500)
```
You will receive: secret.txt file, it's a secret text

