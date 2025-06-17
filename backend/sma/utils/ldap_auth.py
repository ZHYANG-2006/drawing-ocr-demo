import hashlib
import os

from sma.system.models.system import LdapConfig
from .encryption_utils import encryption_util  # 导入 CryptoUtils 类
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError
from ldap3 import ALL_ATTRIBUTES
from django.contrib.auth.hashers import make_password


class ldap_auth:
    def authenticate_with_ldap(username, password):
        # 从数据库中获取 LDAP 配置
        ldap_config = LdapConfig.objects.filter(enabled='1').first()
        if not ldap_config:
            return None
        # raise Exception("没有启用的 LDAP 配置")

        # 获取当前系统类型
        system_platform = os.name  # 可以使用 os.name 或 platform.system() 来获取操作系统类型

        # 根据不同操作系统切换路径
        if system_platform == 'nt':  # Windows
            keystore_path = 'D:/keystore/keystore.jks'  # Windows下的路径
        elif system_platform == 'posix':  # Linux 或 macOS
            keystore_path = '/mnt/pdf-analyze/keystore.jks'  # Linux/macOS 下的路径
        else:
            raise Exception(f"Unsupported system platform: {system_platform}")

        keystore_password = 'keystore-password'  # keystore 的密码
        alias = 'mykey'  # 密钥的别名

        # 从 JCEKS keystore 中加载 AES 密钥
        encryption_util.load_key_from_jceks(keystore_path, alias, keystore_password, '')

        # 使用解密后的密钥对加密的 LDAP 密码进行解密
        decrypted_password = encryption_util.decrypt(ldap_config.enc_password)

        # 连接 LDAP 服务器
        server = Server(ldap_config.server_address, get_info=ALL)
        dn = f"{ldap_config.root}"  # DN

        try:
            # 使用解密后的管理员密码进行 LDAP 绑定
            with Connection(server, ldap_config.username, decrypted_password, auto_bind=True) as conn:
                # 验证用户凭据（username 和 password）
                user_search_dn = ldap_config.root
                user_filter = f"({ldap_config.login_field}={username})"
                conn.search(user_search_dn, user_filter, attributes=ALL_ATTRIBUTES)

                if conn.entries:
                    # 找到用户后，再使用该用户的 DN 和密码进行验证
                    user_dn = conn.entries[0].entry_dn

                    # 使用用户的 DN 和密码再次进行绑定验证
                    user_conn = Connection(server, user_dn, password, auto_bind=True)
                    if user_conn.bind():
                        return {
                            'samaccountname': conn.entries[0].sAMAccountName.value,
                            'cn': conn.entries[0].cn.value,
                            'email': conn.entries[0].mail.value if hasattr(conn.entries[0], 'mail') else None,
                            'department': conn.entries[0].department.value,
                            'employeeid': conn.entries[0].employeeID.value,
                            'mobile': conn.entries[0].mobile.value if hasattr(conn.entries[0], 'mobile') else None,
                            'password': make_password(hashlib.new("md5", password.encode(encoding="UTF-8")).hexdigest())
                        }
                else:
                    return None
        except LDAPBindError:
            # LDAP 认证失败
            return None
