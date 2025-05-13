from django.http import JsonResponse
from utils.fbmsg import FBMsg
from django.contrib import auth
from django.contrib.auth.models import User
import json
from userprofile.models import Users
from staff.models import ListModel as staff

def login(request, *args, **kwargs):
    post_data = json.loads(request.body.decode())
    data = {
        "name": post_data.get('name'),
        "password": post_data.get('password'),
    }
    ip = request.META.get('HTTP_X_FORWARDED_FOR') if request.META.get(
        'HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')
    if User.objects.filter(username=str(data['name'])).exists():
        user = auth.authenticate(username=str(data['name']), password=str(data['password']))
        if user is None:
            err_ret = FBMsg.err_ret()
            err_ret['data'] = data
            return JsonResponse(err_ret)
        else:
            auth.login(request, user)
            user_detail = Users.objects.filter(user_id=user.id).first()
            
            # 修复部分：添加检查确保 staff 对象存在
            staff_obj = staff.objects.filter(openid=user_detail.openid, staff_name=str(user_detail.name)).first()
            if staff_obj is None:
                # 如果找不到对应的 staff 记录，返回错误信息
                err_ret = FBMsg.err_ret()
                err_ret['ip'] = ip
                err_ret['data'] = data
                err_ret['msg'] = "未找到对应的员工记录"
                return JsonResponse(err_ret)
                
            staff_id = staff_obj.id
            data = {
                "name": data['name'],
                'openid': user_detail.openid,
                "user_id": staff_id
            }
            ret = FBMsg.ret()
            ret['ip'] = ip
            ret['data'] = data
            return JsonResponse(ret)
    else:
        err_ret = FBMsg.err_ret()
        err_ret['ip'] = ip
        err_ret['data'] = data
        return JsonResponse(err_ret)
