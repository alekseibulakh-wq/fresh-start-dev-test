import unittest

def greet(name):
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    name = " ".join(name.split())
    if not name:
        raise ValueError("name must not be empty or whitespace-only")
    return f"Hello, {name}!"

class GreetingTests(unittest.TestCase):
    def test_name(self):
        self.assertEqual(greet("Ada"), "Hello, Ada!")

    def test_whitespace(self):
        self.assertEqual(greet("  Ada\tLovelace\n"), "Hello, Ada Lovelace!")

    def test_unicode(self):
        self.assertEqual(greet("\u2003Zoë\u00a0李\u3000"), "Hello, Zoë 李!")

    def test_empty(self):
        for value in ("", " ", "\t\n"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                greet(value)

    def test_type(self):
        for value in (None, 42, True, b"Ada", []):
            with self.subTest(value=value), self.assertRaises(TypeError):
                greet(value)

if __name__ == "__main__":
    unittest.main()
