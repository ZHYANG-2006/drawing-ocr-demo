from Crypto.Cipher import AES
import base64
import jks


class encryption_util:
    secret_key = None

    @staticmethod
    def load_key_from_jceks(keystore_path, alias, keystore_password, key_password):
        """
        从 JCEKS keystore 中加载 AES 密钥
        :param keystore_path: keystore 文件路径
        :param alias: keystore 中的密钥别名
        :param keystore_password: keystore 的密码
        :param key_password: 该密钥的密码
        :return: 加载的 AES 密钥
        """
        # 加载 keystore
        keystore = jks.KeyStore.load(keystore_path, keystore_password)

        # 提取密钥，密钥存储在别名为 alias 的条目下
        secret = keystore.secret_keys[alias]

        # 密钥以字节形式存储，转换为可用于 AES 的密钥
        encryption_util.secret_key = secret.key

    @staticmethod
    def encrypt(input_data):
        """
        使用 AES 加密数据
        :param input_data: 需要加密的字符串
        :return: 加密后的字符串（Base64 编码）
        """
        cipher = AES.new(encryption_util.secret_key, AES.MODE_ECB)
        input_data_padded = input_data.ljust(16)  # 填充输入数据，使其长度为 16 的倍数
        encrypted_bytes = cipher.encrypt(input_data_padded.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    @staticmethod
    def decrypt(encrypted_data):
        """
        使用 AES 解密数据
        :param encrypted_data: Base64 编码的加密数据
        :return: 解密后的原始字符串
        """
        cipher = AES.new(encryption_util.secret_key, AES.MODE_ECB)
        decoded_encrypted_data = base64.b64decode(encrypted_data)
        decrypted_bytes = cipher.decrypt(decoded_encrypted_data)
        return decrypted_bytes.decode('utf-8').strip()