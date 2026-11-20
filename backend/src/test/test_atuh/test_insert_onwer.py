import unittest
from unittest.mock import patch, MagicMock
from src.security.security import SecurityUsers

class TestSecurityUsersRobustness(unittest.TestCase):
    
    def setUp(self):
        self.security = SecurityUsers()
        self.valid_data = {
            'DIM_CustomerId': 'test-customer-001',
            'CustomerFraction': 'tepetate',
            'username': 'demo_user',
            'password': 'ChangeMe123!',
            'RoleName': 'comitiva',
            'serviceName': 'delegacion',
        }

    # ============================================================
    # TESTS DE VALIDACIÓN GENERAL (TODO LO DEMÁS)
    # ============================================================

    # TESTS DE VALIDACIÓN DE DATOS DE ENTRADA
    def test_missing_required_fields(self):
        """Test: Campos requeridos faltantes"""
        print("\n=== Test: Campos requeridos faltantes ===")
        incomplete_data = {'username': 'test'}
        status, message = self.security.insert_new_Onwer(incomplete_data)
        print(f"Status: {status}, Mensaje: {message}")
        self.assertEqual(status, 400)
        self.assertIn("faltan campos", message.lower())

    def test_invalid_field_types(self):
        """Test: Tipos de datos incorrectos"""
        print("\n=== Test: Tipos de datos incorrectos ===")
        invalid_type_data = self.valid_data.copy()
        invalid_type_data['DIM_CustomerId'] = 12345  # Debería ser string
        status, message = self.security.insert_new_Onwer(invalid_type_data)
        print(f"Status: {status}, Mensaje: {message}")
        self.assertEqual(status, 400)

    def test_empty_fields(self):
        """Test: Campos vacíos"""
        print("\n=== Test: Campos vacíos ===")
        empty_data = self.valid_data.copy()
        empty_data['username'] = ''
        status, message = self.security.insert_new_Onwer(empty_data)
        print(f"Status: {status}, Mensaje: {message}")
        self.assertEqual(status, 400)

    # TESTS DE VALIDACIÓN DE USUARIO
    @patch('src.security.security.is_admin')
    def test_user_already_admin(self, mock_is_admin):
        """Test: Usuario que ya es administrador"""
        print("\n=== Test: Usuario que ya es administrador ===")
        mock_is_admin.return_value = True
        status, message = self.security.insert_new_Onwer(self.valid_data)
        print(f"Status: {status}, Mensaje: {message}")
        self.assertEqual(status, 403)
        self.assertIn("administrador", message.lower())


if __name__ == '__main__':
    # Ejecutar tests con verbosidad para ver los mensajes
    unittest.main(verbosity=2)
