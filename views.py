# 有三種網頁轉換方法，必放
from django.shortcuts import render  # 呼叫模板，合成後送往瀏覽器
from django.http import HttpResponse, request  # 程式送往瀏覽器
from django.shortcuts import redirect  # 程式送往程式
import pymysql
import re
import pandas as pd
from datetime import datetime
from sql_account import sql_account

'''思考一下
1. 能否依照權限顯示資料 - ok
2. 是否可以刪除，修改時傳送訊息 - 暫不加入功能
3. 刪除，修改的javascrip能否提示時加入帳號 - ok
4. list_all 部門要做排序 - ok
5. 基本美化 - ok
6. 匯出列表 - ok
7. 匯入 - 考量實際應用出現的問題暫不加入功能
'''

'''
level
adm, pre, dir, spe, sup, dir, nor

dep
總部, 財務部, 人力資源部, 業務部, 客戶服務部, 總務部, 企劃部
admin_Office, Finance_Department, Human_Resources_Department, Sales_Department, Customer_Service_Department, General_Affairs_Department, Planning_Department'''

# ===========================測試回傳==============================
# return HttpResponse('hi')

# ========================staff_Login_Data_Retrieve=================================  
# 各分頁顯示登入資訊所需函式
def staff_Login_Data_Retrieve(request):
    # 設定空字典作為接收db tuple資料的轉換
    staff_Login_Data = {}
    staff_Login_Data['login_account'] = request.session['login_account']
    staff_Login_Data['login_name'] = request.session['login_name']
    staff_Login_Data['login_subjection_depar'] = request.session['login_subjection_depar']
    staff_Login_Data['level'] = request.session['level']
    # 判斷db是否有登錄，回傳到其他def與html
    staff_Login_Data['login'] = 1
    return staff_Login_Data
    
# =========================主頁面============================
def index(request):

    return render(request, 'index.html')

# ====================staff頁面=============================
def staff_index(request):
    show = {}
    # 從db > session內取得login資料
    if request.session.get("login_name") != None:
        # 呼叫staff_Login_Data_Retrieve存入變數
        staff_Login_Data=staff_Login_Data_Retrieve(request)
        
        # 判斷要顯示哪個頁面
        if (staff_Login_Data['login_subjection_depar'] and staff_Login_Data['level']) in (['總部'] and ['adm', 'pre']):
            show['data'] = 0
            # 將要顯示的登入資料傳送至模板
            return render(request, "staff\\staff_index.html", {'staff_Login_Data':staff_Login_Data, 'show':show})
        elif (staff_Login_Data['login_subjection_depar'] and staff_Login_Data['level']) in (['人力資源部'] and ['dir', 'spe']):
            show['data'] = 1
            return render(request, "staff\\staff_index.html", {'staff_Login_Data':staff_Login_Data, 'show':show})
        elif (staff_Login_Data['login_subjection_depar'] and staff_Login_Data['level']) in (['財務部, 業務部, 客戶服務部, 總務部, 企劃部'] and ['dir', 'spe', 'sup']):
            show['data'] = 2
            return render(request, "staff\\staff_index.html", {'staff_Login_Data':staff_Login_Data, 'show':show})
        else:
            return render(request, 'staff\\staff_index.html', {'staff_Login_Data':staff_Login_Data})
    else:
        return render(request, 'staff\\staff_index.html')
    
# ======================staff_login=======================
def staff_Login(request):
    if request.session.get("login_name") == None:
    # 呼叫staff_Login_Data_Retrieve存入變數
        # staff_Login_Data=staff_Login_Data_Retrieve(request)
        # 網頁獲取資料的方式
        if request.method == "POST":
            # 取出html表單的輸入值
            account = request.POST['account']
            name = request.POST['name']
            password = request.POST['password']
            # 連結資料庫 > 呼叫sql_account內的db_conect
            db = sql_account.connect()
            cursor = db.cursor()
            # 檢查帳號是否存在，單筆資料取出，對應取值的select不是對應sql，否則會tuple index out of range
            sql = "select account, password, name, subjection_depar, level from staff_contrl where account='{}'".format(account)
            cursor.execute(sql)
            db.commit()
            # 放置暫存區檢查
            staff_Login_Data = cursor.fetchone()
            # 一階段確認帳號是否為空值，對應html內之值
            if staff_Login_Data[0] != None :
                # 二階段確認密碼是否存在
                if staff_Login_Data[1] == password:
                    # 三階段確認姓名是否存在
                    if staff_Login_Data[2] == name:
                        # 將登陸資料存至session內供回應其他模板
                        # [0][1][2]對應 > sql select account,password,name,subjection_depar
                        request.session['login_account'] = staff_Login_Data[0]
                        request.session['login_name'] = staff_Login_Data[2]
                        request.session['login_subjection_depar'] = staff_Login_Data[3]
                        request.session['level'] = staff_Login_Data[4]
                        # return HttpResponse(request.session['level'])
                        # return HttpResponse("檢查完成")
                        return redirect("/staff_index/")
                    else:
                        return HttpResponse("查無此姓名，請重新登錄 <a href='/staff_Login/'>回上一頁</a>")
                else:
                    return HttpResponse("密碼錯誤，請重新登入 <a href='/staff_Login/'>回上一頁</a>")
            else:
                return HttpResponse("帳號錯誤，請聯繫管理員 <a href='/staff_index/'>回上一頁</a>")
        else:
            return render(request, 'staff\\staff_Login.html')
    else:
        # 呼叫staff_Login_Data_Retrieve存入變數
        staff_Login_Data=staff_Login_Data_Retrieve(request)
        return redirect("/staff_index/")

    # return HttpResponse('staff_Login')

# 登出時從有帳號 > 無帳號，會帶account
def staff_Logout(request, account=""):
    if request.session.get("login_name") != None:
        del request.session['login_account']
        del request.session['login_name']
        del request.session['login_subjection_depar']
        return redirect('staff\\staff_index.html')
    else:
        return HttpResponse("已登出職員管理系統 <a href='/index/'>返回主頁</a>")

# =======================staff_Create==========================
def staff_Create(request):
    if request.session.get("login_name") != None:
        # 呼叫staff_Login_Data_Retrieve存入變數
        staff_Login_Data=staff_Login_Data_Retrieve(request)
        
        # 進行權限檢查 > 部門檢查
        if request.session['login_subjection_depar'] in (['總部', '人力資源部'] or ['admin_Office','Human_Resources_Department']):
            # 進行權限檢查 > 職務等級檢查
            if request.session['level'] in ['adm', 'pre', 'dir', 'spe']:
                # 將要顯示的登入資料傳送至模板
                return render(request, 'staff\\staff_Create.html', {'staff_Login_Data':staff_Login_Data})
            else:
                # 權限等級檢查未通過
                return HttpResponse('權限等級不足')
        else:
            # 部門檢查未通過
            return HttpResponse('不隸屬於部門職權範圍')
    else:
        # 未登入不得新增
        return HttpResponse("尚未登入 <a href='/staff_Login/'>進行登入</a>")

def staff_DubleCheck(request):
    if request.session.get("login_name") != None:
        # 呼叫staff_Login_Data_Retrieve存入變數
        staff_Login_Data=staff_Login_Data_Retrieve(request)
        # 將要顯示的登入資料傳送至模板
        # 設定一變數為dic接收html資料
        data={}
        # 擷取create填寫的資料透過request.post轉為list，原始資料為dic{'key':values}
        # data['list'] = request.POST['dic']
        # [''] > '' > 字串
        data['account'] = request.POST['account']
        data['name'] = request.POST['name']
        data['password'] = request.POST['password']
        data['privacy_mail'] = request.POST['privacy_mail']
        data['mobile_phine'] = request.POST['mobile_phine']
        data['addr'] = request.POST['addr']
        data['emergency_contact_name'] = request.POST['emergency_contact_name']
        data['emergency_contact_tel'] = request.POST['emergency_contact_tel']
        data['subjection_depar'] = request.POST['subjection_depar']
        data['job_title'] = request.POST['job_title']
        data['depar_director'] = request.POST['depar_director']
        
        # ----------驗證區 >> 帳號，姓名，密碼，電話，信箱----------------------
        # 帳號驗證，只接受英文，數字，底線
        if not re.search(r"[A-Za-z]+", request.POST['account']):
            msg = "帳號輸入錯誤，帳號不能有空白與特殊字元"
            return HttpResponse(msg)
        elif len(request.POST['account']) < 4:
            msg = "帳號過短"
            return HttpResponse(msg)
        else:
            # 若帳號格式皆正確，存入原始變數並把所有空白都移除
            data['account'] = request.POST['account'].strip()
        
        # 姓名驗證，只接受中文
        if not re.search(r"[\u4e00-\u9fa5]", request.POST['name']):
            msg = "姓名輸入錯誤，只接受中文"
            return HttpResponse(msg)
        else:
            # 若姓名格式皆正確，存入原始變數並把所有空白都移除
            data['name'] = request.POST['name'].strip()
        
        # 密碼驗證，密碼要包含一個大小寫英文，長度大於6，小於15字元
        if re.search(r"\s", request.POST['password']):
            msg = "密碼輸入錯誤，不包含空白，請返回上一頁"
            return HttpResponse(msg)
        elif not re.search(r"[A-Z]", request.POST['password']):
            msg = "密碼輸入錯誤，需至少需一個大寫英文"
            return HttpResponse(msg)
        elif not re.search(r"[a-z]", request.POST['password']):
            msg = "密碼輸入錯誤，需至少需一個小寫英文"
            return HttpResponse(msg)
        # 長度檢查
        elif len(request.POST['password']) < 6:
            msg = "密碼輸入錯誤，長度需大於6個字元"
            return HttpResponse(msg)
        elif len(request.POST['password']) > 15:
            msg = "密碼輸入錯誤，長度需小於15個字元"
            return HttpResponse(msg)
        else:
            # 若密碼格式皆正確，存入原始變數並把所有空白都移除
            data['password'] = request.POST['password'].strip()
            
        # 手機驗證，只接受數字，不接受特殊字元，長度需 == 10
        if not re.search(r"09\d+", request.POST['mobile_phine']):
            msg = "手機號碼需為數字"
            return HttpResponse(msg)
        elif len(request.POST['mobile_phine']) > 10:
            msg = "手機號碼為10個數字"
            return HttpResponse(msg)
        elif len(request.POST['mobile_phine']) < 10:
            msg = "手機號碼為10個數字"
            return HttpResponse(msg)
        else:
            # 若手機號碼格式皆正確，存入原始變數並把所有空白都移除
            data['mobile_phine'] = request.POST['mobile_phine'].strip()
            
        # 私人信箱驗證，格式 > xxx@xxx.xxx，長度2-6字元
        if not re.search(r"[a-z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6}", request.POST['privacy_mail']):
            msg = "信箱格式錯誤"
            return HttpResponse(msg)
        else:
            # 若信箱格式皆正確，存入原始變數並把所有空白都移除
            data['privacy_mail'] = request.POST['privacy_mail'].strip()

        # 緊急聯絡人電話驗證，只接受數字，不接受特殊字元，長度需 == 10
        if not re.search(r"09\d+", request.POST['emergency_contact_tel']):
            msg = "緊急聯絡人電話號碼需為數字"
            return HttpResponse(msg)
        elif len(request.POST['emergency_contact_tel']) > 10:
            msg = "緊急聯絡人電話號碼為10個數字"
            return HttpResponse(msg)
        elif len(request.POST['emergency_contact_tel']) < 10:
            msg = "緊急聯絡人電話號碼為10個數字"
            return HttpResponse(msg)
        else:
            # 若緊急連絡人電話格式皆正確，存入原始變數並把所有空白都移除
            data['emergency_contact_tel'] = request.POST['emergency_contact_tel'].strip()
                    
        return render(request, 'staff\\staff_DubleCheck.html', {'data': data,'staff_Login_Data':staff_Login_Data})
    else:
            # 未登入不得新增
            return HttpResponse("尚未登入 <a href='/staff_Login/'>進行登入</a>")
        
def staff_CreateConfirm(request):
    try:
        # 接收staff_DubleCheck的輸入資料
        account = request.POST['account']
        name = request.POST['name']
        password = request.POST['password']
        privacy_mail = request.POST['privacy_mail']
        # 設定為'NULL' > 防止回傳時出現Nano資料庫會出錯(varchar)
        mail = 'NULL'
        mobile_phine = request.POST['mobile_phine']
        addr = request.POST['addr']
        emergency_contact_name = request.POST['emergency_contact_name']
        emergency_contact_tel = request.POST['emergency_contact_tel']
        # 設定為0 > 防止回傳時出現Nano資料庫會出錯(int)
        status = 0
        category = 0
        subjection_depar = request.POST['subjection_depar']
        job_title = request.POST['job_title']
        depar_director = request.POST['depar_director']
        level = 'NULL'
        note = 'NULL'
        nomal_hour_month = 0
        total_hour_month = 0
        official_leave = 0
        annual_sick_leave = 0
        overtime_hour = 0
        # 連結資料庫 > 呼叫sql_account內的db_conect
        db = sql_account.connect()
        cursor = db.cursor()
        # 先檢查account是否重複
        sql = "select * from staff_contrl where account='{}'".format(account)
        cursor.execute(sql)
        db.commit()
        # 將檢查結果放置變數中，temporary > 臨時
        tmp = cursor.fetchone()
        # 檢查變數中是否有值，若db檢查為空
        if tmp == None:
            # 存入db
            sql = "insert into staff_contrl (account, name, password, privacy_mail, mail, mobile_phine, addr, emergency_contact_name, emergency_contact_tel, status, category, subjection_depar, job_title, depar_director, level, note, nomal_hour_month, total_hour_month, official_leave, annual_sick_leave, overtime_hour) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}',{},{},'{}','{}','{}','{}','{}',{},{},{},{},{})".format(account, name, password, privacy_mail, mail, mobile_phine, addr, emergency_contact_name, emergency_contact_tel, status, category, subjection_depar, job_title, depar_director, level, note, nomal_hour_month, total_hour_month, official_leave, annual_sick_leave, overtime_hour)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            result = "儲存成功 <a href='/staff_index/'>回首頁</a>"
        else:
            return HttpResponse('帳號已存在，請另選帳號 <a href="/staff_Create/">回上一頁</a>')
    except:
        result = "儲存失敗"
    return HttpResponse(result)

# ===================staff_ListAll=========================
# 登入後判斷部門別顯示全部資訊
def staff_ListAll(request):
    # 檢查db session中是否有loginName > 獲取用get
    if request.session.get("login_name") != None:
        # 將已登入資料存至變數中
        staff_Login_Data=staff_Login_Data_Retrieve(request)
        if request.session['login_subjection_depar'] in (['總部'] or ['admin_Office']):
            # 進行權限檢查 > 職務等級檢查
            if request.session['level'] in ['adm', 'pre']:
                try:
                    # 連結資料庫 > 呼叫sql_account內的db_conect
                    db = sql_account.connect()
                    cursor = db.cursor()
                    # 列表需要抓出所有資料
                    sql = "select * from staff_contrl"
                    cursor.execute(sql)
                    db.commit()
                    # 存入變數中
                    staff_ListAll = cursor.fetchall()
                    cursor.close()
                    db.close()
                    # 回傳db資料與登陸資料
                    return render(request, "staff\\staff_ListAll.html", {'staff_ListAll': staff_ListAll, 'staff_Login_Data':staff_Login_Data})
                except:
                    return HttpResponse('讀取失敗，請重新嘗試 <a href="/staff_index/">回職員管理首頁</a>')
            else:
                # 權限等級檢查未通過
                return HttpResponse('權限等級不足')
        else:
            # 部門檢查未通過
            return HttpResponse('不隸屬於部門範圍')
    else:
        # 未登入不得觀看資料
        return HttpResponse('<a href="/staff_Login/">未登入，請登入後繼續</a>')

# 登入後判斷部門別顯示該部門資訊
def dep_Staff_ListAll(request):
    # 檢查db session中是否有loginName > 獲取用get
    if request.session.get("login_name") != None:
        # 將已登入資料存至變數中
        staff_Login_Data=staff_Login_Data_Retrieve(request)
        subjection_depar = request.session['login_subjection_depar']
        # return HttpResponse([staff_Login_Data])
        if request.session['login_subjection_depar'] in ['財務部', '人力資源部', '業務部', '客戶服務部', '總務部', '企劃部']:
            # 進行權限檢查 > 職務等級檢查
            if request.session['level'] in ['dir', 'spe', 'sup']:
                try:
                    # 連結資料庫 > 呼叫sql_account內的db_conect
                    db = sql_account.connect()
                    cursor = db.cursor()
                    # 列表需要抓出所有資料
                    sql = "select * from staff_contrl where subjection_depar='{}'".format(subjection_depar)
                    cursor.execute(sql)
                    db.commit()
                    # 存入變數中
                    dep_Staff_ListAll = cursor.fetchall()
                    cursor.close()
                    db.close()
                    # 回傳db資料與登陸資料
                    return render(request, "staff\\dep_Staff_ListAll.html", {'dep_Staff_ListAll': dep_Staff_ListAll, 'staff_Login_Data':staff_Login_Data})
                except:
                    return HttpResponse('讀取失敗，請重新嘗試 <a href="/staff_index/">回職員管理首頁</a>')
            else:
                # 權限等級檢查未通過
                return HttpResponse('權限等級不足')
        else:
            # 部門檢查未通過
            return HttpResponse('不隸屬於部門範圍')
    else:
        # 未登入不得觀看資料
        return HttpResponse('<a href="/staff_Login/">未登入，請登入後繼續</a>')

# ==================personal_staff_Revise===========================
# 修改一定會有帶值account
def staff_Revise(request, account=""):
    # 判斷是否有登入
    if request.session.get("login_name") != None:
        # 以session內的login_account作為sql搜尋條件
        account = request.session['login_account']
        if request.session['login_subjection_depar'] in (['總部', '財務部', '人力資源部', '業務部', '客戶服務部', '企劃部','總務部'] or ['admin_Office', 'Finance_Department', 'Human_Resources_Department', 'Sales_Department', 'Customer_Service_Department', 'Planning_Department', 'General_Affairs_Department']):
            if request.session['level'] in ['adm', 'pre', 'dir', 'sup', 'spe', 'dir', 'nor']:
                try:
                    # 連結資料庫 > 呼叫sql_account內的db_conect
                    db = sql_account.connect()
                    cursor = db.cursor()
                    sql = "select * from staff_contrl where account = '{}'".format(account)
                    cursor.execute(sql)
                    db.commit()
                    db.close()
                    cursor.close()
                    # 取出單個資料
                    staff_Revise_Data = cursor.fetchone()
                    # 判斷取出資訊是否為空值
                    if staff_Revise_Data != None:
                        # 呼叫def staff_Login_Data_Retrieve，basic.html顯示登入之資料
                        staff_Login_Data=staff_Login_Data_Retrieve(request)
                        # return HttpResponse(staff_Revise_Data) > 回傳測試
                        return render(request, 'staff\\staff_Revise.html', {'staff_Revise_Data': staff_Revise_Data, 'size':1,'staff_Login_Data':staff_Login_Data})
                    else:
                        return HttpResponse('資料庫無資料取出 <a href="/staff_index/" >回上一頁</a>')
                except:
                    return HttpResponse('資料庫連線失敗，請重試 <a href="/staff_index/" >回上一頁</a>')
            else:
                return HttpResponse('權限等級不足')
        else:
            return HttpResponse('不隸屬於部門範圍')        
    else:
        return HttpResponse("尚未登入 <a href='/staff_Login/'>進行登入</a>")

def staff_ReviseDB(request):
    # 將回傳值包回字典{key:value}
    data = {}
    # ----------驗證區 >> 帳號，姓名，密碼，電話，信箱----------------------
    # 姓名驗證，只接受中文
    if not re.search(r"[\u4e00-\u9fa5]", request.POST['name']):
        msg = "姓名輸入錯誤，只接受中文"
        return HttpResponse(msg)
    else:
        # 若姓名格式皆正確，存入原始變數並把所有空白都移除
        data['name'] = request.POST['name'].strip()  
    
    # 密碼驗證，密碼要包含一個大小寫英文，長度大於6，小於15字元
    if re.search(r"\s", request.POST['password']):
        msg = "密碼輸入錯誤，不包含空白，請返回上一頁"
        return HttpResponse(msg)
    elif not re.search(r"[A-Z]", request.POST['password']):
        msg = "密碼輸入錯誤，需至少需一個大寫英文"
        return HttpResponse(msg)
    elif not re.search(r"[a-z]", request.POST['password']):
        msg = "密碼輸入錯誤，需至少需一個小寫英文"
        return HttpResponse(msg)
    # 長度檢查
    elif len(request.POST['password']) < 6:
        msg = "密碼輸入錯誤，長度需大於6個字元"
        return HttpResponse(msg)
    elif len(request.POST['password']) > 15:
        msg = "密碼輸入錯誤，長度需小於15個字元"
        return HttpResponse(msg)
    else:
        # 若密碼格式皆正確，把所有空白都移除
        data['password'] = request.POST['password'].strip()
        
    # 手機驗證，只接受數字，不接受特殊字元，長度需 == 10
    if not re.search(r"09\d+", request.POST['mobile_phine']):
        msg = "手機號碼需為數字"
        return HttpResponse(msg)
    elif len(request.POST['mobile_phine']) > 10:
        msg = "手機號碼為10個數字"
        return HttpResponse(msg)
    elif len(request.POST['mobile_phine']) < 10:
        msg = "手機號碼為10個數字"
        return HttpResponse(msg)
    else:
        # 若手機號碼格式皆正確，存入原始變數並把所有空白都移除
        data['mobile_phine'] = request.POST['mobile_phine'].strip()
        
    # 私人信箱驗證，格式 > xxx@xxx.xxx，長度2-6字元
    if not re.search(r"[a-z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6}", request.POST['privacy_mail']):
        msg = "信箱格式錯誤"
        return HttpResponse(msg)
    else:
        # 若信箱格式皆正確，存入原始變數並把所有空白都移除
        data['privacy_mail'] = request.POST['privacy_mail'].strip()

    # 緊急聯絡人電話驗證，只接受數字，不接受特殊字元，長度需 == 10
    if not re.search(r"09\d+", request.POST['emergency_contact_tel']):
        msg = "緊急聯絡人電話號碼需為數字"
        return HttpResponse(msg)
    elif len(request.POST['emergency_contact_tel']) > 10:
        msg = "緊急聯絡人電話號碼為10個數字"
        return HttpResponse(msg)
    elif len(request.POST['emergency_contact_tel']) < 10:
        msg = "緊急聯絡人電話號碼為10個數字"
        return HttpResponse(msg)
    else:
        # 若緊急連絡人電話格式皆正確，存入原始變數並把所有空白都移除
        data['emergency_contact_tel'] = request.POST['emergency_contact_tel'].strip()    
    
    # 接收從sraff_Revise的表單資料，轉換為要放回資料庫的list資料
    # 此段接收但不執行db修改
    account = request.POST['account']
    # 將驗證完資料放回要存入db的變數中
    name = data['name']
    password = data['password']
    privacy_mail = data['privacy_mail']
    mail = request.POST['mail']
    mobile_phine = data['mobile_phine']
    addr = request.POST['addr']
    emergency_contact_name = request.POST['emergency_contact_name']
    emergency_contact_tel = data['emergency_contact_tel']
    status = request.POST['status']
    category = request.POST['category']
    subjection_depar = request.POST['subjection_depar']
    job_title = request.POST['job_title']
    depar_director = request.POST['depar_director']
    level = request.POST['level']
    note = request.POST['note']
    nomal_hour_month = request.POST['nomal_hour_month']
    total_hour_month = request.POST['total_hour_month']
    official_leave = request.POST['official_leave']
    annual_sick_leave = request.POST['annual_sick_leave']
    overtime_hour = request.POST['overtime_hour']
    
    # 執行db修改
    # 連結資料庫 > 呼叫sql_account內的db_conect
    db = sql_account.connect()
    cursor = db.cursor()
    # 要加上where條件式 > 否則資料庫會全改，若要多條件 > and
    sql = "update staff_contrl set name='{}', password='{}', privacy_mail='{}', mail='{}', mobile_phine='{}', addr='{}', emergency_contact_name='{}', emergency_contact_tel='{}', status={}, category={}, subjection_depar='{}', job_title='{}', depar_director='{}', level='{}', note='{}', nomal_hour_month={}, total_hour_month={}, official_leave={}, annual_sick_leave={}, overtime_hour={} where account='{}'".format(name, password, privacy_mail, mail, mobile_phine, addr, emergency_contact_name, emergency_contact_tel, status, category, subjection_depar, job_title, depar_director, level, note, nomal_hour_month, total_hour_month, official_leave, annual_sick_leave, overtime_hour, account)
    cursor.execute(sql)
    db.commit()
    
    return HttpResponse("<a href='/staff_Revise/'>個人資料修改成功，回至修改頁面</a>")

# ==================allstaff_staff_Revise===========================
def all_staff_Revise(request, account=""):
    # 判斷是否有登入
    if request.session.get("login_name") != None:
        # 進行權限檢查 > 部門檢查
        if request.session['login_subjection_depar'] in (['總部', '財務部', '人力資源部', '業務部', '客戶服務部', '企劃部', '總務部'] or ['admin_Office', 'Finance_Department', 'Human_Resources_Department', 'Sales_Department', 'Customer_Service_Department', 'Planning_Department', 'General_Affairs_Department']):
            # 進行權限檢查 > 職務等級檢查
            if request.session['level'] in ['adm', 'pre', 'spe', 'dir']:
                # 以staff_listAll內的account作為sql搜尋條件
                if account != "":
                    try:
                        # 連結資料庫 > 呼叫sql_account內的db_conect
                        db = sql_account.connect()
                        cursor = db.cursor()
                        sql = "select * from staff_contrl where account = '{}'".format(account)
                        cursor.execute(sql)
                        db.commit()
                        db.close()
                        cursor.close()
                        # 取出單個資料
                        all_Staff_Revise_Data = cursor.fetchone()
                        # 判斷取出資訊是否為空值
                        if all_Staff_Revise_Data != None:
                            # 呼叫def staff_Login_Data_Retrieve，basic.html顯示登入之資料
                            staff_Login_Data=staff_Login_Data_Retrieve(request)
                            return render(request, 'staff\\all_staff_Revise.html', {'all_Staff_Revise_Data': all_Staff_Revise_Data, 'size':1,'staff_Login_Data':staff_Login_Data})
                        else:
                            return HttpResponse('資料庫無資料取出 <a href="/staff_index/" >回上一頁</a>')
                    except:
                        return HttpResponse('資料庫連線失敗，請重試 <a href="/staff_index/" >回上一頁</a>')
                else:
                    return HttpResponse('資料庫未找到相關資料，請返回重新嘗試 <a href="/staff_index/" >回上一頁</a>') 
            else:
                # 權限等級檢查未通過
                return HttpResponse('權限等級不足')
        else:
            # 部門檢查未通過
            return HttpResponse('不隸屬於部門範圍')
    else:
        return HttpResponse("尚未登入 <a href='/staff_Login/'>進行登入</a>")    

def all_staff_ReviseDB(request, account=""):
        # 將回傳值包回字典{key:value}
    data = {}
    # ----------驗證區 >> 帳號，姓名，密碼，電話，信箱----------------------
    # 姓名驗證，只接受中文
    if not re.search(r"[\u4e00-\u9fa5]", request.POST['name']):
        msg = "姓名輸入錯誤，只接受中文"
        return HttpResponse(msg)
    else:
        # 若姓名格式皆正確，存入原始變數並把所有空白都移除
        data['name'] = request.POST['name'].strip()  
    
    # 密碼驗證，密碼要包含一個大小寫英文，長度大於6，小於15字元
    if re.search(r"\s", request.POST['password']):
        msg = "密碼輸入錯誤，不包含空白，請返回上一頁"
        return HttpResponse(msg)
    elif not re.search(r"[A-Z]", request.POST['password']):
        msg = "密碼輸入錯誤，需至少需一個大寫英文"
        return HttpResponse(msg)
    elif not re.search(r"[a-z]", request.POST['password']):
        msg = "密碼輸入錯誤，需至少需一個小寫英文"
        return HttpResponse(msg)
    # 長度檢查
    elif len(request.POST['password']) < 6:
        msg = "密碼輸入錯誤，長度需大於6個字元"
        return HttpResponse(msg)
    elif len(request.POST['password']) > 15:
        msg = "密碼輸入錯誤，長度需小於15個字元"
        return HttpResponse(msg)
    else:
        # 若密碼格式皆正確，把所有空白都移除
        data['password'] = request.POST['password'].strip()
        
    # 手機驗證，只接受數字，不接受特殊字元，長度需 == 10
    if not re.search(r"09\d+", request.POST['mobile_phine']):
        msg = "手機號碼需為數字"
        return HttpResponse(msg)
    elif len(request.POST['mobile_phine']) > 10:
        msg = "手機號碼為10個數字"
        return HttpResponse(msg)
    elif len(request.POST['mobile_phine']) < 10:
        msg = "手機號碼為10個數字"
        return HttpResponse(msg)
    else:
        # 若手機號碼格式皆正確，存入原始變數並把所有空白都移除
        data['mobile_phine'] = request.POST['mobile_phine'].strip()
        
    # 私人信箱驗證，格式 > xxx@xxx.xxx，長度2-6字元
    if not re.search(r"[a-z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6}", request.POST['privacy_mail']):
        msg = "私人信箱格式錯誤"
        return HttpResponse(msg)
    else:
        # 若信箱格式皆正確，存入原始變數並把所有空白都移除
        data['privacy_mail'] = request.POST['privacy_mail'].strip()
    
    # 公司信箱驗證，格式 > xxx@xxx.xxx，長度2-6字元
    if not re.search(r"[a-z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6}", request.POST['mail']):
        msg = "公司信箱格式錯誤"
        return HttpResponse(msg)
    else:
        # 若信箱格式皆正確，存入原始變數並把所有空白都移除
        data['mail'] = request.POST['mail'].strip()

    # 緊急聯絡人電話驗證，只接受數字，不接受特殊字元，長度需 == 10
    if not re.search(r"09\d+", request.POST['emergency_contact_tel']):
        msg = "緊急聯絡人電話號碼需為數字"
        return HttpResponse(msg)
    elif len(request.POST['emergency_contact_tel']) > 10:
        msg = "緊急聯絡人電話號碼為10個數字"
        return HttpResponse(msg)
    elif len(request.POST['emergency_contact_tel']) < 10:
        msg = "緊急聯絡人電話號碼為10個數字"
        return HttpResponse(msg)
    else:
        # 若緊急連絡人電話格式皆正確，存入原始變數並把所有空白都移除
        data['emergency_contact_tel'] = request.POST['emergency_contact_tel'].strip() 

    # 接收從all_staff_Revise的表單資料，轉換為要放回資料庫的list資料
    account = request.POST['account']
    name = data['name'] 
    password = data['password']
    privacy_mail = data['privacy_mail']
    mail = data['mail'] 
    mobile_phine = data['mobile_phine']
    addr = request.POST['addr']
    emergency_contact_name = request.POST['emergency_contact_name']
    emergency_contact_tel = data['emergency_contact_tel']
    status = request.POST['status']
    category = request.POST['category']
    subjection_depar = request.POST['subjection_depar']
    job_title = request.POST['job_title']
    depar_director = request.POST['depar_director']
    level = request.POST['level']
    note = request.POST['note']
    nomal_hour_month = request.POST['nomal_hour_month']
    total_hour_month = request.POST['total_hour_month']
    official_leave = request.POST['official_leave']
    annual_sick_leave = request.POST['annual_sick_leave']
    overtime_hour = request.POST['overtime_hour']
    # 執行修改
    # 連結資料庫 > 呼叫sql_account內的db_conect
    db = sql_account.connect()
    cursor = db.cursor()
    # 要加上where條件式 > 否則資料庫全改，多條件 > and
    sql = "update staff_contrl set name='{}', password='{}', privacy_mail='{}', mail='{}', mobile_phine='{}', addr='{}', emergency_contact_name='{}', emergency_contact_tel='{}', status={}, category={}, subjection_depar='{}', job_title='{}', depar_director='{}', level='{}', note='{}', nomal_hour_month={}, total_hour_month={}, official_leave={}, annual_sick_leave={}, overtime_hour={} where account='{}'".format(name, password, privacy_mail, mail, mobile_phine, addr, emergency_contact_name, emergency_contact_tel, status, category, subjection_depar, job_title, depar_director, level, note, nomal_hour_month, total_hour_month, official_leave, annual_sick_leave, overtime_hour, account)
    cursor.execute(sql)
    db.commit()
    return HttpResponse("<a href='/staff_ListAll/'>職員資料修改成功，回至職員列表</a>")

# ==================dep_all_staff_Revise===========================
def dep_all_staff_Revise(request, account=""):
    # 判斷是否有登入
    if request.session.get("login_name") != None:
        # 進行權限檢查 > 部門檢查
        if request.session['login_subjection_depar'] in (['總部', '財務部', '人力資源部', '業務部', '客戶服務部', '企劃部', '總務部']):
            # 進行權限檢查 > 職務等級檢查
            if request.session['level'] in ['adm', 'pre', 'spe', 'dir']:
                # 以staff_listAll內的account作為sql搜尋條件
                if account != "":
                    try:
                        # 連結資料庫 > 呼叫sql_account內的db_conect
                        db = sql_account.connect()
                        cursor = db.cursor()
                        sql = "select * from staff_contrl where account = '{}'".format(account)
                        cursor.execute(sql)
                        db.commit()
                        db.close()
                        cursor.close()
                        # 取出單個資料
                        dep_all_staff_Revise_Data = cursor.fetchone()
                        # return HttpResponse(dep_all_staff_Revisee_Data)
                        # 判斷取出資訊是否為空值
                        if dep_all_staff_Revise_Data != None:
                            # 呼叫def staff_Login_Data_Retrieve，basic.html顯示登入之資料
                            staff_Login_Data=staff_Login_Data_Retrieve(request)
                            return render(request, 'staff\\dep_all_staff_Revise.html', {'dep_all_staff_Revise_Data': dep_all_staff_Revise_Data, 'size':1,'staff_Login_Data':staff_Login_Data})
                        else:
                            return HttpResponse('資料庫無資料取出 <a href="/staff_index/" >回上一頁</a>')
                    except:
                        return HttpResponse('資料庫連線失敗，請重試 <a href="/staff_index/" >回上一頁</a>')
                else:
                    return HttpResponse('資料庫未找到相關資料，請返回重新嘗試 <a href="/staff_index/" >回上一頁</a>') 
            else:
                # 權限等級檢查未通過
                return HttpResponse('權限等級不足')
        else:
            # 部門檢查未通過
            return HttpResponse('不隸屬於部門範圍')
    else:
        return HttpResponse("尚未登入 <a href='/staff_Login/'>進行登入</a>")    

def dep_all_staff_ReviseDB(request, account=""):
        # 將回傳值包回字典{key:value}
    data = {}
    # ----------驗證區 >> 帳號，姓名，密碼，電話，信箱----------------------
    # 姓名驗證，只接受中文
    if not re.search(r"[\u4e00-\u9fa5]", request.POST['name']):
        msg = "姓名輸入錯誤，只接受中文"
        return HttpResponse(msg)
    else:
        # 若姓名格式皆正確，存入原始變數並把所有空白都移除
        data['name'] = request.POST['name'].strip()  
    
    # 密碼驗證，密碼要包含一個大小寫英文，長度大於6，小於15字元
    if re.search(r"\s", request.POST['password']):
        msg = "密碼輸入錯誤，不包含空白，請返回上一頁"
        return HttpResponse(msg)
    elif not re.search(r"[A-Z]", request.POST['password']):
        msg = "密碼輸入錯誤，需至少需一個大寫英文"
        return HttpResponse(msg)
    elif not re.search(r"[a-z]", request.POST['password']):
        msg = "密碼輸入錯誤，需至少需一個小寫英文"
        return HttpResponse(msg)
    # 長度檢查
    elif len(request.POST['password']) < 6:
        msg = "密碼輸入錯誤，長度需大於6個字元"
        return HttpResponse(msg)
    elif len(request.POST['password']) > 15:
        msg = "密碼輸入錯誤，長度需小於15個字元"
        return HttpResponse(msg)
    else:
        # 若密碼格式皆正確，把所有空白都移除
        data['password'] = request.POST['password'].strip()
        
    # 手機驗證，只接受數字，不接受特殊字元，長度需 == 10
    if not re.search(r"09\d+", request.POST['mobile_phine']):
        msg = "手機號碼需為數字"
        return HttpResponse(msg)
    elif len(request.POST['mobile_phine']) > 10:
        msg = "手機號碼為10個數字"
        return HttpResponse(msg)
    elif len(request.POST['mobile_phine']) < 10:
        msg = "手機號碼為10個數字"
        return HttpResponse(msg)
    else:
        # 若手機號碼格式皆正確，存入原始變數並把所有空白都移除
        data['mobile_phine'] = request.POST['mobile_phine'].strip()
        
    # 私人信箱驗證，格式 > xxx@xxx.xxx，長度2-6字元
    if not re.search(r"[a-z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6}", request.POST['privacy_mail']):
        msg = "私人信箱格式錯誤"
        return HttpResponse(msg)
    else:
        # 若信箱格式皆正確，存入原始變數並把所有空白都移除
        data['privacy_mail'] = request.POST['privacy_mail'].strip()
    
    # 公司信箱驗證，格式 > xxx@xxx.xxx，長度2-6字元
    if not re.search(r"[a-z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6}", request.POST['mail']):
        msg = "公司信箱格式錯誤"
        return HttpResponse(msg)
    else:
        # 若信箱格式皆正確，存入原始變數並把所有空白都移除
        data['mail'] = request.POST['mail'].strip()

    # 緊急聯絡人電話驗證，只接受數字，不接受特殊字元，長度需 == 10
    if not re.search(r"09\d+", request.POST['emergency_contact_tel']):
        msg = "緊急聯絡人電話號碼需為數字"
        return HttpResponse(msg)
    elif len(request.POST['emergency_contact_tel']) > 10:
        msg = "緊急聯絡人電話號碼為10個數字"
        return HttpResponse(msg)
    elif len(request.POST['emergency_contact_tel']) < 10:
        msg = "緊急聯絡人電話號碼為10個數字"
        return HttpResponse(msg)
    else:
        # 若緊急連絡人電話格式皆正確，存入原始變數並把所有空白都移除
        data['emergency_contact_tel'] = request.POST['emergency_contact_tel'].strip() 

    # 接收從all_staff_Revise的表單資料，轉換為要放回資料庫的list資料
    account = request.POST['account']
    name = data['name'] 
    password = data['password']
    privacy_mail = data['privacy_mail']
    mail = data['mail'] 
    mobile_phine = data['mobile_phine']
    addr = request.POST['addr']
    emergency_contact_name = request.POST['emergency_contact_name']
    emergency_contact_tel = data['emergency_contact_tel']
    status = request.POST['status']
    category = request.POST['category']
    subjection_depar = request.POST['subjection_depar']
    job_title = request.POST['job_title']
    depar_director = request.POST['depar_director']
    level = request.POST['level']
    note = request.POST['note']
    nomal_hour_month = request.POST['nomal_hour_month']
    total_hour_month = request.POST['total_hour_month']
    official_leave = request.POST['official_leave']
    annual_sick_leave = request.POST['annual_sick_leave']
    overtime_hour = request.POST['overtime_hour']
    # 執行修改
    # 連結資料庫 > 呼叫sql_account內的db_conect
    db = sql_account.connect()
    cursor = db.cursor()
    # 要加上where條件式 > 否則資料庫全改，多條件 > and
    sql = "update staff_contrl set name='{}', password='{}', privacy_mail='{}', mail='{}', mobile_phine='{}', addr='{}', emergency_contact_name='{}', emergency_contact_tel='{}', status={}, category={}, subjection_depar='{}', job_title='{}', depar_director='{}', level='{}', note='{}', nomal_hour_month={}, total_hour_month={}, official_leave={}, annual_sick_leave={}, overtime_hour={} where account='{}'".format(name, password, privacy_mail, mail, mobile_phine, addr, emergency_contact_name, emergency_contact_tel, status, category, subjection_depar, job_title, depar_director, level, note, nomal_hour_month, total_hour_month, official_leave, annual_sick_leave, overtime_hour, account)
    cursor.execute(sql)
    db.commit()
    return HttpResponse("<a href='/dep_Staff_ListAll/'>部門職員資料修改成功，回至職員列表</a>")

# ========================staff_Delete=================================
def staff_Delete(request, account=""):
    if request.session.get("login_name") != None:
        # 進行權限檢查 > 部門檢查
        if request.session['login_subjection_depar'] in (['總部', '財務部', '人力資源部', '業務部', '客戶服務部', '企劃部'] or ['admin_Office', 'Finance_Department', 'Human_Resources_Department', 'Sales_Department', 'Customer_Service_Department', 'Planning_Department']):
            # 進行權限檢查 > 職務等級檢查
            if request.session['level'] in ['adm', 'pre']:
                # 以listall表單內的account作為sql搜尋條件
                if account != "":
                    try:
                        # 連結資料庫 > 呼叫sql_account內的db_conect
                        db = sql_account.connect()
                        cursor = db.cursor()
                        sql = "delete from staff_contrl where account = '{}'".format(account)
                        cursor.execute(sql)
                        db.commit()
                        db.close()
                        cursor.close()
                        return HttpResponse("<a href='/staff_ListAll/'>刪除成功，回至列表</a>")
                    except:
                        return HttpResponse("<a href='/staff_ListAll/'>刪除失敗，請重試</a>")
                else:
                    return render(request, "staff\\staff_ListAll.html")
            else:
                # 權限等級檢查未通過
                return HttpResponse('權限等級不足')
        else:
            # 部門檢查未通過
            return HttpResponse('不隸屬於部門範圍')
    else:
        return HttpResponse("尚未登入 <a href='/staff_Login/'>進行登入</a>")    

# ========================all_staff_data_Export=================================
# 所有檔案匯出
def all_staff_data_Export(request):
    try:
        # 連結資料庫 > 呼叫sql_account內的db_conect
        db = sql_account.connect()
        cursor = db.cursor()
        sql = "select *  from staff_contrl"
        cursor.execute(sql)
        all_staff_data = cursor.fetchall()

        # 取得sql欄位
        field = cursor.description
        # columns > sql列
        columns = []
        # 以長度透過迴圈加入變數中
        for i in range(len(field)):
            columns.append(field[i][0])

        # 取得本機時間並格式化(excel不接受特殊字元)，需要引入datetime
        localTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%p")
        # 設定存取路徑，名稱為現在時間
        result_PATH = r'D:\\python課程\\自我練習與實作\\rex_web\\{}.xlsx'.format('職員管理總表備份'+localTime)

        # 以pandas寫入路徑
        writer = pd.ExcelWriter( result_PATH , engine='xlsxwriter')
        # 添加sql欄位
        df = pd.DataFrame(columns=columns)
        # 將sql欄位寫入excel中
        for i in range(len(all_staff_data)):
            df.loc[i] = list(all_staff_data[i])  
        #  sheet_name 資料夾底部名稱
        df.to_excel(writer, sheet_name='所有職員管理表' ,index =False)

        writer .save()
        writer.close()
        db.close()
        cursor.close()
        return HttpResponse("下載成功，路徑名稱為 : {} &nbsp;&nbsp;&nbsp;<a href='/staff_index/'>返回管理頁面</a>".format(result_PATH))
    except:
        return HttpResponse("資料庫連線錯誤，請重試")

# ========================staff_contral_erp_process_chart=================================
# erp流程圖
def staff_contral_erp_process_chart(request):
    
    # return HttpResponse("hi")
    return render(request, 'process_chart\\staff_contral_erp_process_chart.html')

# ========================satff_list_all_dep_condion=================================
def satff_list_all_dep_condion(request):
    if request.session.get("login_name") != None:
        # 以session內的login_account作為sql搜尋條件
        account = request.session['login_account']
        try:
            # 連結資料庫 > 呼叫sql_account內的db_conect
            db = sql_account.connect()
            cursor = db.cursor()
        except:
            return HttpResponse('連結資料庫失敗') 
        # 抓出列表中的部門名稱
        dep_condition = request.POST['dep_condition']
        if dep_condition != None:
            # 連結資料庫 > 呼叫sql_account內的db_conect
            db = sql_account.connect()
            cursor = db.cursor()
            sql = "select * from staff_contrl where subjection_depar='{}'".format(dep_condition)
            cursor.execute(sql)
            db.commit()
            staff_ListAll = cursor.fetchall()
            db.close()
            cursor.close()
            if staff_ListAll != None:
                # 呼叫def staff_Login_Data_Retrieve，basic.html顯示登入之資料
                staff_Login_Data=staff_Login_Data_Retrieve(request)
                return render(request, 'staff\\staff_ListAll.html', {'staff_ListAll': staff_ListAll, 'staff_Login_Data':staff_Login_Data})
            else:
                return HttpResponse('資料庫無資料取出 <a href="/staff_index/" >回上一頁</a>')
        else:
            return HttpResponse('資料庫無資料取出 <a href="/staff_index/" >回上一頁</a>')
    else:
        return HttpResponse('資料庫無資料取出 <a href="/staff_index/" >回上一頁</a>')
