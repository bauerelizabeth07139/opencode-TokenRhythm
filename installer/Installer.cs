using System;
using System.IO;
using System.Reflection;
using System.Text;

class Program
{
    [STAThread]
    static int Main()
    {
        Console.OutputEncoding = Encoding.UTF8;
        Console.WriteLine();
        Console.WriteLine("================================================");
        Console.WriteLine("  OpenCode - TokenRhythm Provider Installer");
        Console.WriteLine("================================================");
        Console.WriteLine();

        string configDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".config", "opencode");
        string configFile = Path.Combine(configDir, "opencode.jsonc");

        try
        {
            if (!Directory.Exists(configDir))
            {
                Console.WriteLine("[*] Creating config directory: " + configDir);
                Directory.CreateDirectory(configDir);
            }

            if (File.Exists(configFile))
            {
                Console.WriteLine("[*] Existing opencode.jsonc found, backing up to opencode.jsonc.bak");
                File.Copy(configFile, Path.Combine(configDir, "opencode.jsonc.bak"), true);
            }

            byte[] data;
            using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("opencode.jsonc"))
            {
                if (s == null) throw new Exception("Embedded resource 'opencode.jsonc' not found.");
                data = new byte[s.Length];
                int read = 0;
                while (read < data.Length)
                {
                    int n = s.Read(data, read, data.Length - read);
                    if (n == 0) break;
                    read += n;
                }
            }
            File.WriteAllBytes(configFile, data);

            Console.WriteLine();
            Console.WriteLine("[OK] TokenRhythm provider preset installed successfully!");
            Console.WriteLine();
            Console.WriteLine("    Next steps:");
            Console.WriteLine("      1. Run:  opencode");
            Console.WriteLine("      2. Type /connect, select Other, provider ID: tokenrhythm");
            Console.WriteLine("      3. Paste your TokenRhythm API key, then /models to pick a model");
            Console.WriteLine();
            WaitForExit();
            return 0;
        }
        catch (Exception ex)
        {
            Console.WriteLine("[X] Failed: " + ex.Message);
            WaitForExit();
            return 1;
        }
    }

    static void WaitForExit()
    {
        try { Console.ReadKey(); }
        catch { }
    }
}
