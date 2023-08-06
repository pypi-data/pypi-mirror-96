
from OpenSSL import crypto
from OpenSSL.crypto import _lib, _ffi, X509


class Certificate:

    def __init__(self, buff, digestalgo='md5'):
        self.content = []
        self._parse(buff, digestalgo)

    def get(self):
        return self.content

    def _parse(self, buff, digestalgo):
        pkcs7 = crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, buff)

        certs_stack = _ffi.NULL
        if pkcs7.type_is_signed():
            certs_stack = pkcs7._pkcs7.d.sign.cert
        elif pkcs7.type_is_signedAndEnveloped():
            certs_stack = pkcs7._pkcs7.d.signed_and_enveloped.cert

        pycerts = []

        for i in range(_lib.sk_X509_num(certs_stack)):
            tmp = _lib.X509_dup(_lib.sk_X509_value(certs_stack, i))
            pycert = X509._from_raw_x509_ptr(tmp)
            pycerts.append(pycert)

        if not pycerts:
            return None

        for cert in pycerts:
            sbj = cert.get_subject()
            name = 'C={}, ST={}, L={}, O={}, CN={}'.format(
                sbj.C, sbj.ST, sbj.L, sbj.O, sbj.CN
            )
            checksum = cert.digest(digestalgo).decode().replace(':', '')
            self.content.append((name, checksum))
