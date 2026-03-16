// Herramienta para generar hashes de contraseñas (compatible con PasswordHelper del backend).
// Uso: dotnet run
// Ejecutar desde: Base_de_Datos/HashPasswordGenerator

using System;
using System.Security.Cryptography;

string Hash(string password)
{
    byte[] salt = RandomNumberGenerator.GetBytes(16);
    var pbkdf2 = new Rfc2898DeriveBytes(password, salt, 100_000, HashAlgorithmName.SHA256);
    byte[] hash = pbkdf2.GetBytes(32);
    byte[] hashBytes = new byte[48];
    Array.Copy(salt, 0, hashBytes, 0, 16);
    Array.Copy(hash, 0, hashBytes, 16, 32);
    return Convert.ToBase64String(hashBytes);
}

Console.WriteLine("-- Hashes para SkilledGuard DML --");
Console.WriteLine("clave123 (Administrador): " + Hash("clave123"));
Console.WriteLine("clave456 (Usuario):       " + Hash("clave456"));
Console.WriteLine("admin123 (Admin extra):   " + Hash("admin123"));
Console.WriteLine("user123 (Usuario extra):  " + Hash("user123"));
