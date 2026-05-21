from flask import Blueprint, request, flash, session, jsonify
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({'success': False, 'message': '用户名或密码不能为空'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400

    # 创建用户（注意：你后续应该改为安全的哈希密码）
    new_user = User(name=name, password=password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '数据库写入失败', 'error': str(e)}), 500

    # 自动生成 token（与登录逻辑保持一致）
    import secrets
    token = secrets.token_hex(16)

    # 自动设置 session（如果你想注册后自动登录）
    session['user_id'] = new_user.id
    session['name'] = new_user.name

    return jsonify({
        'success': True,
        'message': '注册成功',
        'token': token,
        'user': {
            'id': new_user.id,
            'name': new_user.name,
        }
    })



@auth_bp.route('/check_username', methods=['POST'])
def check_username():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'message': '用户名不能为空'}), 400

    # 检查数据库中是否已存在
    exists = User.query.filter_by(name=name).first() is not None

    return jsonify({
        'success': True,
        'exists': exists
    })



@auth_bp.route('/login', methods=['POST'])
def login():
    # 获得用户名和密码
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400
    name = data.get('name')
    password = data.get('password')
    if not name or not password:
        return jsonify({'success': False, 'message': '用户名或密码不能为空'}), 400

    # 查询数据库
    user = User.query.filter_by(name=name).first()  # 改为查询用户名
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    # 验证用户和密码（仍然需要修复密码安全问题）
    if user.password != password:
        flash('用户名或密码错误', 'danger')  # 更新提示信息
        return jsonify({'success': False, 'message': '密码错误'}), 401

    # 登录成功，设置session
    session['user_id'] = user.id
    session['name'] = user.name  # 改为存储用户名
    flash('登录成功', 'success')  # 更新提示信息

    # 生成 token
    import secrets
    token = secrets.token_hex(16)
    # 返回结果
    return jsonify({
        'success': True,
        'message': '登录成功',
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name
        }
    })


# @auth_bp.route('/logout')
# def logout():
#     session.clear()
#     flash('已退出登录', 'info')  # 更新提示信息
#     return redirect(url_for('index'))