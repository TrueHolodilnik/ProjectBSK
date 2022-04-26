from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import io

class Encryptor:

    def __init__(self):
        self.mode = AES.MODE_EAX
        key = RSA.generate(2048)
        self.selfPublicKey = None
        self.selfPrivateKey = None
        self.setPrivateKey(key.export_key())
        self.setSelfPublicKey(key.publickey().export_key())

    def getSelfPublicKey(self):
        return self.selfPublicKey

    def getPrivateKey(self):
        return self.selfPrivateKey

    def setSelfPublicKey(self, key):
        self.selfPublicKey = key
        file_out = open("receiver.pem", "wb")
        file_out.write(self.selfPublicKey)
        file_out.close()

    def setPrivateKey(self, key):
        self.selfPrivateKey = key
        file_out = open("private.pem", "wb")
        file_out.write(self.selfPrivateKey)
        file_out.close()

    def encryptBlock(self, data):

        recipient_key = RSA.import_key(open("receiver.pem").read())
        session_key = get_random_bytes(16)

        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)

        output = io.StringIO()
        [output.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
        return output

    def decryptBlock(self, data):

        private_key = RSA.import_key(open("private.pem").read())

        enc_session_key, nonce, tag, ciphertext = \
            [data.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]

        # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return data
