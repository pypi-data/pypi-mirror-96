# NAME

url-param-sorted - предоставляет функцию для cортировки параметров url в порядке их возрастания

# VERSION

0.0.2

# SYNOPSIS

```python
from url_param_sorted import url_param_sorted

url_param_sorted('y=1&z=&x=2&x=3&z&x=1')	# -> 'x=1&x=2&x=3&y=1&z&z='

url_param_sorted({'y': 1, 'z': ["", None], 'x': [2, 3, 1]})		# -> 'x=1&x=2&x=3&y=1&z&z='

try:
	url_param_sorted([])	# -> raise TypeError("Аргумент может быть только str или dict")
except TypeError as e:
	pass
```

# DESCRIPTION

Функция `url_param_sorted` сортирует параметры url в порядке их возрастания.

С библиотекой поставляется утилита `url-param-sorted`.

```sh
$ url-param-sorted 'y=1&z=&x=2&x=3&z&x=1'
x=1&x=2&x=3&y=1&z&z=
```

# INSTALL

```sh
$ pip3 install url-param-sorted
```

# REQUIREMENTS

* Нет

# AUTHOR

Kosmina O. Yaroslav <darviarush@mail.ru>

# LICENSE

MIT License

Copyright (c) 2020 Kosmina O. Yaroslav

