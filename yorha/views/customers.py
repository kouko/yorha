# 基本Flask路由需要，只要是View家家戶戶必備
from yorha import app
from flask import render_template, request, session, redirect,url_for
from yorha.views.auth import login_required

# 資料庫
from yorha import models
from yorha.models import db, Customer

# 表單
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired

# viewmodels
from yorha.viewmodels.customers import customer_filter, avantable_user_for_form


"""
顧客列表v2 ===========================
"""
@app.route('/customers/list/',methods=('GET','POST'))
@login_required
def list_customer():

    from yorha.klibrary.type_converter import list2str, str2list

    # 如果session裡沒有記錄上次filter狀態的「customer_filter_value_dict」時，就生一個空的Dict出來
    if session.get('customer_filter_value_dict') is None:
        session['customer_filter_value_dict'] = {}

    # 初始化customer_filter_value_dict，開始處理filter value
    customer_filter_value_dict = {}
    # 如果URL內根本沒有argument，就使用session內的filter value
    if len(request.args) == 0:
        customer_filter_value_dict = session['customer_filter_value_dict']
    # 如果URL內有argument，就使用URL內的argument當成filter value
    elif len(request.args) != 0:
        # 將設定內所有search_type為指定值的欄位，填入URL裡同名argument的value
        for key in app.config['CUSTOMER_SCHEMA']:
            if key.search_type == 'SelectString':
                customer_filter_value_dict[key.class_name] = request.args.get(key.table_name)
            elif key.search_type == 'MultiSelectString':
                customer_filter_value_dict[key.class_name] = str2list(request.args.get(key.table_name))
        # 把這次的filter value存在session當下次的預設值用
        session['customer_filter_value_dict'] = customer_filter_value_dict


    # 產生FilterForm的定義
    customer_filter_form_key_dict = {}
    for key in app.config['CUSTOMER_SCHEMA']:
        if key.search_type == 'SelectString':
            customer_filter_form_key_dict[key.table_name] = SelectField(key.name, choices=key.search_option, default=customer_filter_value_dict.get(key.class_name))
        elif key.search_type == 'MultiSelectString':
            customer_filter_form_key_dict[key.table_name] = SelectMultipleField(key.name, choices=key.search_option, default= customer_filter_value_dict.get(key.class_name))

    # 產生FilterForm物件
    CustomerFilterForm = type('CustomerFilterForm',(FlaskForm,),customer_filter_form_key_dict)
    filter_form = CustomerFilterForm()

    # 如果POST回來，把Form的值轉寫到URL上，然後再GET自己（為了以後可以copy URL產生依樣的搜尋結果
    if request.method == 'POST':
        filter_key_in_url = ''
        for key in app.config['CUSTOMER_SCHEMA']:
            if key.search_type == 'SelectString' :
                filter_key_in_url += key.table_name + '=' + filter_form.data[key.table_name] + '&'
            elif key.search_type == 'MultiSelectString':
                filter_key_in_url += key.table_name + '=' + list2str(filter_form.data[key.table_name]) + '&'
        return redirect(url_for('list_customer') + '?' + filter_key_in_url )


    customer_list = customer_filter(**customer_filter_value_dict)
    return render_template('customer_list.html',
                           customer_list=customer_list,
                           filter_form=filter_form,
                           page_title='顧客列表')


"""
定義顧客資訊表單
"""
def gen_customer_data_form(target_customer=None):
    from yorha.klibrary.type_converter import list2str, str2list ,str_list_converter
    from wtforms import validators

    # 一個小函式來做出「取list的最後一個，如果list根本是空的的話就回傳None」
    def last_of_list(sorce_list):
        try:
            return sorce_list[-1]
        except IndexError:
            return None

    # 如果沒有指定顧客，就創一個全新的Customer Class
    if target_customer is None:
        customer = Customer()
    else:
        customer = target_customer

    # 自訂的WTForms validator，當指定的另一Field等於指定值時，此欄位為必填。用來實作使用者選擇「其他」時，需要另外填寫文字的檢查功能。
    def field_related_data_required(related_field, related_value):
        from wtforms.validators import ValidationError
        def _if_others(form, field):
            if form.data[related_field] == related_value and field.data in [None, '', [], ['']]:
                raise ValidationError('Error')
        return _if_others

    # 依據設定產生WTForm定義Field的Dict物件
    table_column_key_dict = {}
    for key in app.config['CUSTOMER_SCHEMA']:
        validator_obj_list = []
        if key.validator != None:
            if key.validator.get('required') is True:
                validator_obj_list.append(validators.DataRequired())
            elif key.validator.get('email') is True:
                validator_obj_list.append(validators.Email())

        if key.type == 'String':
            table_column_key_dict[key.table_name] = StringField(key.name,
                                                                default=last_of_list(getattr(customer, key.table_name)),
                                                                validators=validator_obj_list)

        elif key.type == 'OthersString':
            table_column_key_dict[key.table_name] = StringField(key.name,
                                                                default=last_of_list(getattr(customer, key.table_name)),
                                                                validators=[field_related_data_required(key.parents_table_name,'others')])

        elif key.type == 'SelectString':
            table_column_key_dict[key.table_name] = SelectField(key.name,
                                                                choices=key.option,
                                                                default=last_of_list(getattr(customer, key.table_name)),
                                                                validators=validator_obj_list)

        elif key.type == 'MultiSelectString':
            table_column_key_dict[key.table_name] = SelectMultipleField(key.name,
                                                                        choices=key.option,
                                                                        default=str2list(last_of_list(getattr(customer, key.table_name))),
                                                                        validators=validator_obj_list)


    class CustomerFormBase():
        def save(self):
            for key in app.config['CUSTOMER_SCHEMA']:
                if last_of_list(getattr(customer, key.table_name)) != self.data[key.table_name]:
                    getattr(customer, key.table_name).append(getattr(models, key.class_name)(str_list_converter(self.data[key.table_name])))
            db.session.add(customer)
            db.session.commit()

    CustomerForm = type('CustomerForm',(CustomerFormBase,FlaskForm),table_column_key_dict)

    return CustomerForm()






"""
新增顧客資料 ===================
"""
@app.route('/customers/new/', methods=('GET','POST'))
@login_required
def new_customer():

    form = gen_customer_data_form()
    form_html = []
    for key in app.config['CUSTOMER_SCHEMA']:
        form_html.append( [getattr(form,key.table_name).label, getattr(form,key.table_name)])


    if request.method == 'POST' and form.validate_on_submit() is True:
        form.save()
        return render_template('respond_msg.html',
                               page_title='Success',
                               title='200',
                               msg='成功儲存！',
                               continue_url=url_for('list_customer', responser_in_url=session['user_email']))
    elif request.method == 'POST' and form.validate_on_submit() is False:
        return render_template('respond_msg.html',
                               page_title='Success',
                               title='Error',
                               msg='儲存失敗，欄位格式錯誤！')
    return render_template('customer_data.html',
                           form=form,
                           form_html=form_html,
                           user_name=session['user_name'],
                           page_title='新增顧客')


"""
編輯顧客資料 ===================
"""
@app.route('/customers/edit/<customer_uuid>', methods=('GET','POST'))
@login_required
def edit_customer(customer_uuid):
    # 先Query出URL內指定UUID的顧客
    customer = Customer.query.\
        filter(Customer.customer_uuid == customer_uuid).first()

    form = gen_customer_data_form(customer)
    form_html = []
    for key in app.config['CUSTOMER_SCHEMA']:
        form_html.append( [getattr(form,key.table_name).label, getattr(form,key.table_name)])


    # 如果是用POST打這個網址，判斷value有變更就新增變更記錄。
    if request.method == 'POST' and form.validate_on_submit() is True:
        form.save()
        # 回傳成功訊息
        return render_template('respond_msg.html',
                               page_title='Success',
                               title='200',
                               msg='成功儲存！',
                               continue_url=url_for('list_customer', responser_in_url=session['user_email']))
    elif request.method == 'POST' and form.validate_on_submit() is False:
        return render_template('respond_msg.html',
                               page_title='Error',
                               title='Error',
                               msg='儲存失敗，欄位格式錯誤！')
    return render_template('customer_data.html',
                           form=form,
                           form_html = form_html,
                           page_title='顧客資料:' + customer.customer_name[-1].value)
