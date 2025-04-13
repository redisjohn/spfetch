'''X509 Certificate Inspector'''
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class CertificateInspector:
    def __init__(self, pem_cert_str):
        self.pem_cert_str = pem_cert_str.strip()
        self.cert = self._load_certificate()

    def _load_certificate(self):
        try:
            return x509.load_pem_x509_certificate(
                self.pem_cert_str.encode(), default_backend()
            )
        except Exception as e:
            raise ValueError(f"Failed to load PEM certificate: {e}")

    def get_expiration_date(self):
        return self.cert.not_valid_after_utc

    def get_subject(self):
        return self.cert.subject

    def get_issuer(self):
        return self.cert.issuer

    def get_serial_number(self):
        return self.cert.serial_number

'''
# Example usage
if __name__ == "__main__":
    with open("cert.b64", "r") as f:
        base64_cert = f.read()

    try:
        inspector = CertificateInspector(base64_cert)
        print("✅ Certificate expires on:", inspector.get_expiration_date())
        print("📌 Subject:", inspector.get_subject())
        print("🛡️ Issuer:", inspector.get_issuer())
        print("🔢 Serial Number:", inspector.get_serial_number())
    except ValueError as e:
        print("❌ Error:", e)
'''