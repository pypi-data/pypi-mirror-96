from flask import jsonify as jsonify_deity, g

Error_Code = {
    10001: "缺少必填参数",
    10002: "参数类型错误",
    10003: "可选参数错误",
    10004: "信息上传重复",  # 例如相同手机号已经注册了账户
    10005: "无指定数据",  # 例如根据id寻找指定信息时，无指定信息
    10006: "上传数据不合理",  # 例如商品价格<=0
    10007: "无指定接口",
    10008: "无权限",
    10009: "失败",
}


def jsonify_list_page(data=None, msg=None, total=0, **kwargs):
    # 分页列表
    # pageNo
    # pageSize
    # totalCount
    # totalPage
    total_page = total // g.page_size
    if total_page * g.page_size < total:
        total_page += 1
    return jsonify_deity(success=True,
                         code=0,
                         msg=msg,
                         data=data,
                         pageNo=g.page + 1,  # 这里主要是根据ant design页面从1开始的原因，所以+1
                         pageSize=g.page_size,
                         totalCount=total,
                         totalPage=total_page,
                         **kwargs)


def jsonify_success(data=None, msg=None, **kwargs):
    return jsonify(True, 0, msg, data, **kwargs)


def jsonify_fail(code=0, msg=None, **kwargs):
    return jsonify(False, code, msg, **kwargs)


def jsonify(success=False, code=0, msg=None, data=None, **kwargs):
    if not msg:
        if success:
            msg = "成功"
        else:
            msg = Error_Code.get(code, '错误')
    return jsonify_deity(success=success,
                         code=code, msg=msg, data=data, **kwargs)
