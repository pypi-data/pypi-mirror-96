# EncDec
EncDec is a very thin wrapper around **[Fernet](https://cryptography.io/en/latest/fernet.html)** and you can use it to encrypt and decrypt data on the fly. I have written this package just to simplify the encryption and decryption of the data in Python and I wanted to give me a possibility of easy switching to any other encryption backend later if needed.

## Installation
Install the package from PyPi or install it from the source:

```bash
pip3 install encdec==1.0.4
```

or

```bash
git clone https://github.com/rehmatworks/encdec.git \
&& cd encdec \
&& pip3 install -r requirements.txt \
&& python3 setup.py install
```

## Usage
Need to generate a key for encryption. Generate this key and store it safely. If the key is lost, it will never be possible for you to decrypt the data back.

```python
from encdec.lib import EncDec


enc = EncDec()
encryption_key = enc.generate_key()

# Encrypt data
enc = EncDec(encryption_key=encryption_key)
encrypted_data = enc.encrypt('Hellow world!')

# Decrypt data
enc = EncDec(encryption_key=encryption_key)
decrypted_data = enc.decrypt('encrypted-string')
```

On failure, both `encrypt()` and `decrypt()` will return `None`. If you want to see the debug message, you can do so by setting `is_debug` property to `True`. The exception `EncdecError` will be raised if an error occurs.

```python
from encdec.lib import EncDec, EncdecError


enc = EncDec(encryption_key='encryption_key', is_debug=True)

try:
    encrypted_data = enc.encrypt('Hellow world!')
except EncdecError as e:
    print('Error occored: {}'.format(str(e)))
```

As I mentioned earlier, it is a very thin wrapper around **Fernet**. You can use the main library directly or you can use it in your project if you expect to switch to any other encryption backend in the longer run.