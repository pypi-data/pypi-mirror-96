#### 介绍

用户、角色、权限，封装控件

#### 发布流程

```
python setup.py sdist 
twine upload dist/ZmUser-1.0.1.tar.gz
```

#### 使用实例

```shell
pip install -r requirements.txt

cd sample
flask db init
flask db migrate
flask db upgrade

python run.py
```

