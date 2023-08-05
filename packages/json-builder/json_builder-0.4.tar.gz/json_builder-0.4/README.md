# json_builder

Build or modify json objects incrementally using json paths

## Installation

The quick way:

```sh
pip install json_builder
```

## Usage

Before start, check the json path syntax: https://goessner.net/articles/JsonPath/

### Add new key
```
root_object = {"a": 10}
JsonBuilder.add(root_object, "$.b", 20)
JsonBuilder.add(root_object, "$.c.d.e", 30)
print(root_object)

Output:
{
  'a': 10,
  'b': 20,
  'c': {
    'd': {
      'e': 30
    }
  }
}
```

### Modify existing key value
```
root_object = {
        'a': 10,
        'b': 20,
        'c': {
            'd': {
                'e': 30
            }
        }
    }
JsonBuilder.add(root_object, "$.c.d.e", "test")
print(root_object)

Output:
{
  'a': 10,
  'b': 20,
  'c': {
    'd': {
      'e': 'test'
    }
  }
}
```

### Create a list
```
root_object = {
        'a': 10,
    }
JsonBuilder.add(root_object, "$.b[0]", "1")
JsonBuilder.add(root_object, "$.b[1]", "2")
JsonBuilder.add(root_object, "$.b[2]", {"c": 20})
print(root_object)

Output:
{
  'a': 10,
  'b': [
    '1',
    '2',
    {
      'c': 20
    }
  ]
}
```

### Modify existing list index
```
root_object = {
        'a': 10,
        'b': [
            '1',
            '2',
            {
                'c': 20
            }
        ]
    }
JsonBuilder.add(root_object, "$.b[2]", '3')
print(root_object)

Output:
{
  'a': 10,
  'b': [
    '1',
    '2',
    '3'
  ]
}
```
## Exceptions

### Object is not json serializable
Values that are not json serializable are not allowed
```
root_object = object()
JsonBuilder.add(root_object, "$.b[4]", '3')
print(root_object)

root_object = {}
JsonBuilder.add(root_object, "$.b[4]", object())
print(root_object)

Output:
TypeError: Object <object object at 0x00000295240A4D20> is not JSON serializable.
```

### Invalid json path
**Check the json path syntax: https://goessner.net/articles/JsonPath/**
```
root_object = {}
JsonBuilder.add(root_object, ".b[4]", 3)
print(root_object)

Output:
ValueError: Invalid json path ".b[4]". Check https://goessner.net/articles/JsonPath/ for more details.
```
### Object is not a dictionary
```
root_object = {
  'a': []
}
JsonBuilder.add(root_object, "$.a.b", 1)
print(root_object)

Output:
Exception: Can't insert key "b", object is not a dictionary. Root: {'a': []}. Json path: $.a.b
```
### Object is not a list
```
root_object = {
  'a': {}
}
JsonBuilder.add(root_object, "$.a[0]", 1)
print(root_object)

Output:
Exception: Can't insert on position "0", object is not a list. Root: {'a': {}}. Json path: $.a[0]
```
### Previous list index not defined
List items must be added consecutively
```
root_object = {
  'a': []
}
JsonBuilder.add(root_object, "$.a[0]", 1)
JsonBuilder.add(root_object, "$.a[2]", 2)
print(root_object)

Output:
Exception: Index to big "2", previous list indexes not defined. Root: {'a': [1]}. Json path: $.a[2]
```

## License
MIT

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
