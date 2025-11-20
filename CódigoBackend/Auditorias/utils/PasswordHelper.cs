using System.Security.Cryptography;

namespace Auditorias.utils
{
    public static class PasswordHelper
    {
        public static string HashPassword(string password)
        {
            byte[] salt = RandomNumberGenerator.GetBytes(16); // generacion de un valor aleatorio para asegurar que dos claves iguales no generen el mismo hash
            var pbkdf2 = new Rfc2898DeriveBytes(password, salt, 100_000, HashAlgorithmName.SHA256);// mediante el algoritmo PBKDF2 dificulta ataques de fuerza bruta
            byte[] hash = pbkdf2.GetBytes(32);

            byte[] hashBytes = new byte[48];
            Array.Copy(salt, 0, hashBytes, 0, 16);
            Array.Copy(hash, 0, hashBytes, 16, 32);
            return Convert.ToBase64String(hashBytes); // combina el salt y el hash y lo convierte a base 64 dando como resultado la cadena cifrada
        }

        public static bool VerifyPassword(string password, string storedHash)
        {
            byte[] hashBytes = Convert.FromBase64String(storedHash); // convierte el hash almacenado en base64 a bytes
            byte[] salt = new byte[16]; 
            Array.Copy(hashBytes, 0, salt, 0, 16); // extrae el salt del hash almacenado

            var pbkdf2 = new Rfc2898DeriveBytes(password, salt, 100_000, HashAlgorithmName.SHA256); 
            byte[] hash = pbkdf2.GetBytes(32); // vuelve a hashear la contraseña ingresada utilizando el mismo salt o valor aleatorio

            for (int i = 0; i < 32; i++)
            {
                if (hashBytes[i + 16] != hash[i])
                    return false;
            }
            return true; // compara byte a byte el hash calculado con el hash guardado en la base de datos, si coincide retorna true si no false 
        }
    }
}