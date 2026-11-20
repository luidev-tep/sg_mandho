import hashlib
import unittest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
from src.security.security import SecurityUsers
from app import app


class TestSecurityHashingAndRecaptcha(unittest.TestCase):
    def setUp(self):
        self.security = SecurityUsers()
        self.client = app.test_client()

    def test_verify_password_legacy_md5(self):
        """Verifica que contraseñas con hash MD5 legado de 32 hex sean validadas correctamente."""
        plain = "MiClaveSegura2026!"
        md5_hash = hashlib.md5(plain.encode()).hexdigest()
        
        # Debe validar positivamente la clave correcta
        self.assertTrue(self.security._SecurityUsers__verify_password(plain, md5_hash))
        # Debe fallar con clave incorrecta
        self.assertFalse(self.security._SecurityUsers__verify_password("ClaveErronea123!", md5_hash))

    def test_verify_password_scrypt(self):
        """Verifica que contraseñas con hash moderno Werkzeug (scrypt) sean validadas correctamente."""
        plain = "ClaveModerna2026!"
        modern_hash = generate_password_hash(plain)
        
        self.assertTrue(self.security._SecurityUsers__verify_password(plain, modern_hash))
        self.assertFalse(self.security._SecurityUsers__verify_password("PasswordWrong!", modern_hash))

    @patch("src.security.security.update_user_info")
    @patch("src.security.security.get_user_info")
    @patch("src.security.security.DIM_DATE")
    def test_login_transparent_upgrade_md5_to_scrypt(self, mock_dim_date, mock_get_user, mock_update_user):
        """Valida que un login exitoso con hash MD5 dispara la actualización a hash moderno."""
        mock_date_instance = MagicMock()
        mock_date_instance.full_date = (2025, 1, 1)
        mock_dim_date.return_value = mock_date_instance

        plain = "SuperPassword123!"
        md5_hash = hashlib.md5(plain.encode()).hexdigest()

        mock_get_user.return_value = {
            'username': 'admin_test',
            'password': md5_hash,
            'RoleName': 'delegado',
            'CustomerFraction': 'centro',
            'DIM_CustomerId': 'cust-12345',
            'DIM_AccountId': 'acc-12345',
            'StartDate': '2025-01-01',
            'EndDate': '2025-12-31',
            'StatusName': 'activo'
        }
        mock_update_user.return_value = (200, "Actualizado")

        status, msg, user_data = self.security.authenticate_user({
            'name': 'admin_test',
            'password': plain,
            'role': 'delegado',
            'manzana': 'centro'
        })

        self.assertEqual(status, 200)
        # Verifica que se haya llamado al upgrade
        mock_update_user.assert_called_once()
        args, _ = mock_update_user.call_args
        new_hash = args[0]
        # El nuevo hash no debe ser MD5 de 32 caracteres y debe validar contra la clave en texto plano
        self.assertFalse(self.security._SecurityUsers__is_legacy_hash(new_hash))
        self.assertTrue(self.security._SecurityUsers__verify_password(plain, new_hash))

    @patch.dict("os.environ", {"RECAPTCHA_ENABLED": "false"})
    @patch("src.routes.security_route.security_options.authenticate_user")
    def test_login_flow_recaptcha_disabled(self, mock_auth):
        """Con RECAPTCHA_ENABLED=false no se requiere token de reCAPTCHA."""
        mock_auth.return_value = (401, "Datos incorrectos", None)
        response = self.client.post("/api/security/login/", json={
            "name": "usuario",
            "password": "Password123!",
            "role": "delegado",
            "manzana": "centro"
        })
        # Al no exigir recaptcha, procede a autenticar y devuelve el resultado de authenticate_user (401)
        self.assertEqual(response.status_code, 401)

    @patch.dict("os.environ", {"RECAPTCHA_ENABLED": "true"})
    def test_login_flow_recaptcha_enabled_requires_token(self):
        """Con RECAPTCHA_ENABLED=true se exige token de reCAPTCHA en el request."""
        response = self.client.post("/api/security/login/", json={
            "name": "usuario",
            "password": "Password123!",
            "role": "delegado",
            "manzana": "centro"
        })
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertIn("reCAPTCHA", json_data.get("message", ""))
