import unittest
from unittest.mock import patch, MagicMock
from src.security.security import SecurityUsers

class TestSecurityUsersRobustness(unittest.TestCase):
    
    def setUp(self):
        self.security = SecurityUsers()
    
    # ============================================================
    # TESTS DE VALIDACIÓN DE CONTRASEÑA
    # ============================================================
    
    def test_weak_password_short(self):
        """Test: Contraseña demasiado corta"""
        print("\n=== Test: Contraseña demasiado corta ===")
        password = 'Ab1!'  # Solo 4 caracteres
        result = self.security.validate_password_with_feedback(password)
        print(f"Resultado: {result}")
        self.assertFalse(result['is_valid'])
        self.assertIn("al menos 8 caracteres", str(result['errors']))

    def test_weak_password_no_uppercase(self):
        """Test: Contraseña sin mayúsculas"""
        print("\n=== Test: Contraseña sin mayúsculas ===")
        password = 'password123!'  # Sin mayúsculas
        result = self.security.validate_password_with_feedback(password)
        print(f"Resultado: {result}")
        self.assertFalse(result['is_valid'])
        self.assertIn("mayúscula", str(result['errors']))

    def test_weak_password_no_lowercase(self):
        """Test: Contraseña sin minúsculas"""
        print("\n=== Test: Contraseña sin minúsculas ===")
        password = 'PASSWORD123!'  # Sin minúsculas
        result = self.security.validate_password_with_feedback(password)
        print(f"Resultado: {result}")
        self.assertFalse(result['is_valid'])
        self.assertIn("minúscula", str(result['errors']))

        
if __name__ == '__main__':
    unittest.main(verbosity=2)