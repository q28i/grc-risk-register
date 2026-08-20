using System;
using System.IO;
using System.Diagnostics;

namespace GRCRiskRegister.Updater
{
    class Program
    {
        static int Main(string[] args)
        {
            Console.Title = "GRC Risk Register — Updater";
            Console.WriteLine("=======================================================");
            Console.WriteLine("  GRC Risk Register — Application Updater");
            Console.WriteLine("=======================================================");

            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string updaterPy = Path.Combine(baseDir, "updater.py");

            if (!File.Exists(updaterPy))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("\n[ERROR] updater.py not found in: " + baseDir);
                Console.ResetColor();
                Console.WriteLine("Press any key to exit...");
                try { Console.ReadKey(); } catch { }
                return 1;
            }

            // Find Python (local runtime or system)
            string pythonExe = null;
            string runtimePy = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "runtime", "python.exe"));
            if (File.Exists(runtimePy))
            {
                pythonExe = runtimePy;
            }

            if (string.IsNullOrEmpty(pythonExe))
            {
                string[] candidates = new string[] { "py.exe", "python.exe" };
                foreach (string cand in candidates)
                {
                    try
                    {
                        ProcessStartInfo psi = new ProcessStartInfo(cand, "--version")
                        {
                            UseShellExecute = false,
                            CreateNoWindow = true
                        };
                        using (Process p = Process.Start(psi))
                        {
                            if (p != null && p.WaitForExit(2000) && p.ExitCode == 0)
                            {
                                pythonExe = cand;
                                break;
                            }
                        }
                    }
                    catch { }
                }
            }

            if (string.IsNullOrEmpty(pythonExe))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("\n[ERROR] Python was not found on this system.");
                Console.WriteLine("Please run 'Start GRC Risk Register.exe' first to provision runtime.\n");
                Console.ResetColor();
                Console.WriteLine("Press any key to exit...");
                try { Console.ReadKey(); } catch { }
                return 1;
            }

            string allArgs = "\"" + updaterPy + "\"";
            if (args != null && args.Length > 0)
            {
                allArgs += " " + string.Join(" ", args);
            }

            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = pythonExe,
                Arguments = allArgs,
                WorkingDirectory = baseDir,
                UseShellExecute = false
            };

            try
            {
                using (Process proc = Process.Start(startInfo))
                {
                    proc.WaitForExit();
                    return proc.ExitCode;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("[ERROR] Failed to run updater: " + ex.Message);
                return 1;
            }
        }
    }
}
